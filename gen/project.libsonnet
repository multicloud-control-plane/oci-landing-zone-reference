// Projection only. Resource definitions remain owned by the pinned OE libraries.
local lz = import 'landing_zone.libsonnet';
local context = import 'render_context.libsonnet';

local select_fields(obj, predicate) = {
  [k]: obj[k] for k in std.objectFields(obj) if predicate(k, obj[k])
};
local replace_strings(value, source, replacement) =
  if std.type(value) == 'object' then {
    [k]: replace_strings(value[k], source, replacement) for k in std.objectFields(value)
  } else if std.type(value) == 'array' then [replace_strings(v, source, replacement) for v in value]
  else if std.type(value) == 'string' then std.strReplace(value, source, replacement)
  else value;
local output_reference(section, key) = 'output://network_resources/' + section + '/' + key + '/id';

function(model)
  assert std.objectHas(model.regions, model.home_region) : 'home_region must exist in regions';
  local region_names = std.objectFields(model.regions);
  local raw(region) =
    local r = model.regions[region];
    {
      region: region, region_short_name: r.short_name, realm: 'oc1', cis_level: 1,
      hub: { kind: 'hub_b', network: { vcn: r.hub } },
      environments: {
        [env]: {
          project_network: { network: { vcn: r.environments[env].network } },
          projects: model.projects[env],
          platforms: { [p]: { network: r.environments[env].platforms[p] }
                       for p in std.objectFields(r.environments[env].platforms) },
        } for env in std.objectFields(r.environments)
      },
      shared_platforms: { [p]: { network: r.shared_platforms[p] }
                          for p in std.objectFields(r.shared_platforms) },
    };
  local rendered = { [r]: lz(raw(r)) for r in region_names };
  local home = rendered[model.home_region];
  // Any IAM difference outside policy statements must be handled deliberately.
  local global_iam = std.foldl(function(acc, r)
    local other = rendered[r].iam;
    assert std.manifestJson(select_fields(acc, function(k, v) k != 'policies_configuration')) ==
           std.manifestJson(select_fields(other, function(k, v) k != 'policies_configuration')) :
           'regional IAM hierarchy differs; align the global model';
    assert std.objectFields(acc.policies_configuration.supplied_policies) ==
           std.objectFields(other.policies_configuration.supplied_policies) : 'regional policy keys differ';
    acc + { policies_configuration+: { supplied_policies: {
      [k]:
        local a = acc.policies_configuration.supplied_policies[k];
        local b = other.policies_configuration.supplied_policies[k];
        assert std.manifestJson(select_fields(a, function(f, v) f != 'statements')) ==
               std.manifestJson(select_fields(b, function(f, v) f != 'statements')) : 'regional policy metadata differs';
        a + { statements: std.set(a.statements + b.statements) }
      for k in std.objectFields(acc.policies_configuration.supplied_policies)
    } } }, region_names, home.iam);
  local notifications(document) = document.notifications_configuration + { topics: {
    [k]: document.notifications_configuration.topics[k] + {
      subscriptions: [{ protocol: 'EMAIL', values: [model.notification_email] }],
    } for k in std.objectFields(document.notifications_configuration.topics)
  } };
  local home_obs = home.observability_cis1;
  local common = global_iam + home.governance + {
    cloud_guard_configuration: home.security_cis1_pre.cloud_guard_configuration,
    security_zones_configuration: home.security_cis1_pre.security_zones_configuration + {
      recipes: select_fields(home.security_cis1_pre.security_zones_configuration.recipes,
                            function(k, v) std.member([z.recipe_key for z in std.objectValues(home.security_cis1_pre.security_zones_configuration.security_zones)], k)),
    },
    home_region_events_configuration: home_obs.home_region_events_configuration,
    notifications_configuration: notifications(home_obs) + {
      topics: select_fields(notifications(home_obs).topics, function(k, v)
        std.endsWith(k, '-IAM-KEY') || std.endsWith(k, '-CLOUDGUARD-KEY')),
    },
  };

  local project_region(region) =
    local full = rendered[region];
    local r = model.regions[region];
    local ctx = context.from_raw_config(raw(region));
    local n = ctx.n;
    local categories = full.network.network_configuration.network_configuration_categories;
    local hub_key = n.key('VCN', ['HUB']);
    local drg_key = n.key('DRG', ['HUB']);
    local hub_category_key = [k for k in std.objectFields(categories) if std.objectHas(categories[k].vcns, hub_key)][0];
    local original_drg = categories[hub_category_key].non_vcn_specific_gateways.dynamic_routing_gateways[drg_key];
    local hub_attachment_key = n.key('DRGATT', ['HUB', 'VCN']);
    local obs = full.observability_cis1;
    local shared_network_cmp = n.key_global('CMP', ['NETWORK']);
    local shared_security_cmp = n.key_global('CMP', ['SECURITY']);
    local network_category(source, cmp) = source + {
      category_compartment_id: cmp,
      vcns: { [key]: source.vcns[key] + { network_security_groups: {} }
              for key in std.objectFields(source.vcns) },
    };
    local hub_network(stage) =
      local source = if stage == 'bootstrap' then full.network_pre else full.network;
      local cat = source.network_configuration.network_configuration_categories[hub_category_key];
      local clean_vcns = { [k]: cat.vcns[k] + {
        load_balancers: {},
        security_lists: { [sl]: cat.vcns[k].security_lists[sl] + {
          ingress_rules: [rule for rule in cat.vcns[k].security_lists[sl].ingress_rules
                          if !std.startsWith(rule.description, 'EXAMPLE: Allow inbound traffic from the Bastion')],
        } for sl in std.objectFields(cat.vcns[k].security_lists) },
      } for k in std.objectFields(cat.vcns) };
      source + { network_configuration+: { network_configuration_categories: {
        [hub_category_key]: cat + {
          vcns: clean_vcns,
          non_vcn_specific_gateways+: { dynamic_routing_gateways: {
            [drg_key]: original_drg + {
              drg_attachments: { [hub_attachment_key]: original_drg.drg_attachments[hub_attachment_key] },
              drg_route_distributions: { [key]:
                local distribution = original_drg.drg_route_distributions[key];
                distribution + { statements: {
                  [statement_key]:
                    local statement = distribution.statements[statement_key];
                    local attachment_key = statement.match_criteria.drg_attachment_key;
                    statement + { match_criteria+: {
                      drg_attachment_key: null,
                      drg_attachment_id: output_reference('drg_attachments', attachment_key),
                    } }
                  for statement_key in std.objectFields(distribution.statements)
                  if stage == 'final'
                } }
                for key in std.objectFields(original_drg.drg_route_distributions)
              },
            },
          } },
        },
      } } };
    local regional_hub_obs = {
      notifications_configuration: notifications(obs) + { topics:
        select_fields(notifications(obs).topics, function(k, v)
          std.endsWith(k, '-NETWORK-KEY') || std.endsWith(k, '-SECURITY-KEY')) },
      alarms_configuration: obs.alarms_configuration + { alarms:
        select_fields(obs.alarms_configuration.alarms, function(k, v)
          v.supplied_alarm.metric_compartment_id == shared_network_cmp ||
          v.supplied_alarm.metric_compartment_id == shared_security_cmp) },
      events_configuration: obs.events_configuration + { event_rules:
        select_fields(obs.events_configuration.event_rules, function(k, v)
          v.compartment_id == shared_network_cmp || v.compartment_id == shared_security_cmp) },
      logging_configuration: obs.logging_configuration + {
        log_groups: select_fields(obs.logging_configuration.log_groups, function(k, v) v.compartment_id == shared_security_cmp),
        flow_logs: select_fields(obs.logging_configuration.flow_logs, function(k, v) std.member(v.target_compartment_ids, shared_network_cmp)),
      },
    };
    local scanning(scope_key, network_cmp, security_cmp) =
      local src = full.security_cis1_pre.scanning_configuration;
      local recipe = n.key_global('VSS-RCPH', scope_key);
      local target = n.key_global('VSS-TGTH', scope_key);
      { scanning_configuration: src + {
        default_compartment_id: security_cmp,
        host_recipes: { [recipe]: std.objectValues(src.host_recipes)[0] + { name: n.display_global('vss-rcph', scope_key) } },
        host_targets: { [target]: std.objectValues(src.host_targets)[0] + {
          name: n.display_global('vss-tgth', scope_key), host_recipe_id: recipe, target_compartment_id: network_cmp,
        } },
      } };
    local own_network(vcn_key, cmp) =
      local category_key = [k for k in std.objectFields(categories) if std.objectHas(categories[k].vcns, vcn_key)][0];
      local cat = network_category(categories[category_key], cmp);
      local attachment_key = [k for k in std.objectFields(original_drg.drg_attachments)
                              if original_drg.drg_attachments[k].network_details.attached_resource_key == vcn_key][0];
      local attachment = original_drg.drg_attachments[attachment_key];
      { network_configuration: { network_configuration_categories: {
        [category_key]: cat + { non_vcn_specific_gateways+: { inject_into_existing_drgs: {
          [drg_key]: { drg_id: drg_key, drg_attachments: {
            [attachment_key]: attachment + {
              drg_route_table_key: null,
              drg_route_table_id: output_reference('drg_route_tables', attachment.drg_route_table_key),
            },
          } },
        } } },
      } } };
    local env_obs(env) =
      local network_cmp = n.key_global('CMP', [env, 'NETWORK']);
      local security_cmp = n.key_global('CMP', [env, 'SECURITY']);
      local topics = { [kind]: n.key_global('NOTT', [env, kind]) for kind in ['NETWORK', 'SECURITY'] };
      {
        notifications_configuration: { default_compartment_id: security_cmp, topics: {
          [topics[kind]]: notifications(obs).topics[n.key_global('NOTT', [kind])] + {
            name: n.display_global('nott', [env, kind]), compartment_id: security_cmp,
          } for kind in ['NETWORK', 'SECURITY']
        } },
        alarms_configuration: { default_compartment_id: security_cmp, alarms: {
          [key]: obs.alarms_configuration.alarms[key] + {
            compartment_id: security_cmp, destination_topic_ids: [topics.NETWORK],
          } for key in std.objectFields(obs.alarms_configuration.alarms)
          if obs.alarms_configuration.alarms[key].supplied_alarm.metric_compartment_id == network_cmp
        } },
        events_configuration: { default_compartment_id: security_cmp, event_rules: {
          [key]: obs.events_configuration.event_rules[key] + { destination_topic_ids: [topics.SECURITY] }
          for key in std.objectFields(obs.events_configuration.event_rules)
          if std.member([network_cmp, security_cmp], obs.events_configuration.event_rules[key].compartment_id)
        } },
        logging_configuration: obs.logging_configuration + {
          default_compartment_id: security_cmp,
          log_groups: select_fields(obs.logging_configuration.log_groups, function(k, v) v.compartment_id == security_cmp),
          flow_logs: select_fields(obs.logging_configuration.flow_logs, function(k, v) std.member(v.target_compartment_ids, network_cmp)),
        },
      };
    local platform_obs(scope, p, cmp) =
      local segments = [scope, 'PLATFORM', p];
      local topic = n.key_global('NOTT', segments);
      local group = n.key_global('LGRP', segments + ['FLOW']);
      {
        notifications_configuration: { default_compartment_id: cmp, topics: {
          [topic]: notifications(obs).topics[n.key_global('NOTT', ['NETWORK'])] + {
            name: n.display_global('nott', segments), compartment_id: cmp,
          },
        } },
        alarms_configuration: { default_compartment_id: cmp, alarms: {
          [key + '-' + std.asciiUpper(scope) + '-' + std.asciiUpper(p)]:
            local src = obs.alarms_configuration.alarms[key];
            src + { compartment_id: cmp, display_name: src.display_name + '-' + scope + '-' + p,
                    destination_topic_ids: [topic], supplied_alarm+: { metric_compartment_id: cmp } }
          for key in std.objectFields(obs.alarms_configuration.alarms)
          if obs.alarms_configuration.alarms[key].supplied_alarm.metric_compartment_id == shared_network_cmp &&
             obs.alarms_configuration.alarms[key].supplied_alarm.namespace == 'oci_vcn'
        } },
        logging_configuration: { default_compartment_id: cmp,
          log_groups: { [group]: { name: n.display_global('lgrp', segments), compartment_id: cmp } },
          flow_logs: { [n.key_global('LOG', segments + [kind])]: {
            log_group_id: group, target_compartment_ids: [cmp], target_resource_type: kind,
          } for kind in ['vcn', 'subnet'] },
        },
      };
    local hub_path = 'lze_' + model.landing_zone_environment + '/' + region;
    local hub_docs = { [hub_path + '/' + stage + '/config.json']:
      replace_strings(hub_network(stage), 'OCI NFW PRIVATE IP OCID, e.g. ocid1.privateip.oc1.eu-frankfurt-1.abtheljs...', 'binding://firewall-private-ip-id') +
      regional_hub_obs + scanning(['SHARED'], shared_network_cmp, shared_security_cmp)
      for stage in ['bootstrap', 'final'] };
    local env_docs = { ['workload_' + env + '/' + region + '/config.json']:
      own_network(n.key('VCN', [env, 'PROJECTS']), n.key_global('CMP', [env, 'NETWORK'])) +
      env_obs(env) + scanning([env], n.key_global('CMP', [env, 'NETWORK']), n.key_global('CMP', [env, 'SECURITY']))
      for env in std.objectFields(r.environments) };
    local shared_platform_docs = { [hub_path + '/platform_' + p + '/config.json']:
      local cmp = n.key_global('CMP', ['SHARED', p]);
      own_network(n.key('VCN', ['SHARED', 'PLATFORM', p]), cmp) + platform_obs('shared', p, cmp) + scanning(['SHARED', p], cmp, cmp)
      for p in std.objectFields(r.shared_platforms) };
    local env_platform_docs = std.foldl(function(acc, env) acc + {
      ['workload_' + env + '/' + region + '/platform_' + p + '/config.json']:
        local cmp = n.key_global('CMP', [env, p]);
        own_network(n.key('VCN', [env, 'PLATFORM', p]), cmp) + platform_obs(env, p, cmp) + scanning([env, p], cmp, cmp)
      for p in std.objectFields(r.environments[env].platforms)
    }, std.objectFields(r.environments), {});
    hub_docs + env_docs + shared_platform_docs + env_platform_docs;
  { 'common/config.json': common } +
  std.foldl(function(acc, r) acc + project_region(r), region_names, {})
