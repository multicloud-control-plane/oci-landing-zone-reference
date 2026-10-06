"""Synthetic deployed-output contracts; never contacts OCI."""
from pathlib import Path
import reference as ref


def synthetic_outputs(catalog, documents, directory):
    keys = [k for k in ref.resource_keys(documents['common/config.json']) if k.startswith('CMP-')]
    ref.write_json(Path(directory) / 'common/compartments_output.json', {
        'compartments': {k: {'id': 'ocid1.compartment.oc1..' + k} for k in keys},
    })
    for stack in catalog['stacks']:
        if stack['scope'] == 'global':
            continue
        config = documents[stack['configurations'].get('bootstrap', stack['configurations'].get('complete'))]
        resources = {k: {} for k in ('vcns', 'subnets', 'dynamic_routing_gateways', 'drg_route_tables', 'drg_attachments')}
        def oid(kind, key):
            return f"ocid1.{kind}.oc1.{stack['region']}.{key}"
        for category in config['network_configuration']['network_configuration_categories'].values():
            for key, vcn in category['vcns'].items():
                resources['vcns'][key] = {'id': oid('vcn', key)}
                for skey in vcn.get('subnets', {}):
                    resources['subnets'][skey] = {'id': oid('subnet', skey), 'vcn_id': oid('vcn', key)}
            gateways = category.get('non_vcn_specific_gateways', {})
            for field in ('dynamic_routing_gateways', 'inject_into_existing_drgs'):
                for key, drg in gateways.get(field, {}).items():
                    if field == 'dynamic_routing_gateways':
                        resources['dynamic_routing_gateways'][key] = {'id': oid('drg', key)}
                    for rkey in drg.get('drg_route_tables', {}):
                        resources['drg_route_tables'][rkey] = {'id': oid('drgroutetable', rkey)}
                    for akey in drg.get('drg_attachments', {}):
                        resources['drg_attachments'][akey] = {'id': oid('drgattachment', akey)}
        ref.write_json(Path(directory) / stack['id'] / 'network_output.json', {'network_resources': resources})
