// Copyright (c) 2026 Oracle and/or its affiliates.
// Reused from oci-landing-zone/config/render.libsonnet at
// 9b4033267af881e65fe8c2b212f220b2804cac09. Only principal parameterized.
function(environment, n, dynamic_group)
  local environment_key = n.key_global('CMP', [environment]);
  local environment_name = std.asciiLower(environment);
  local runner_principal = 'allow dynamic-group ' + dynamic_group;
{
      ['PCY-LZ-%s-GITOPS-PROJECTS-KEY' % std.asciiUpper(environment)]: {
        name: 'pcy-lz-%s-gitops-projects' % environment_name,
        description:
          'MVP GitOps runner access for project Compute, ADB, and NSGs.',
        compartment_id: environment_key,
        statements: [
          '%s to read all-resources in compartment cmp-lz-%s-projects' %
          [runner_principal, environment_name],
          '%s to manage instance-family in compartment cmp-lz-%s-projects' %
          [runner_principal, environment_name],
          '%s to manage volume-family in compartment cmp-lz-%s-projects' %
          [runner_principal, environment_name],
          '%s to manage autonomous-database-family in compartment cmp-lz-%s-projects' %
          [runner_principal, environment_name],
          '%s to use vnics in compartment cmp-lz-%s-projects' %
          [runner_principal, environment_name],
          '%s to manage network-security-groups in compartment cmp-lz-%s-projects' %
          [runner_principal, environment_name],
        ],
      },
      ['PCY-LZ-%s-GITOPS-NETWORK-KEY' % std.asciiUpper(environment)]: {
        name: 'pcy-lz-%s-gitops-network' % environment_name,
        description:
          'MVP GitOps runner access for shared-network workload attachment.',
        compartment_id: environment_key,
        statements: [
          '%s to use virtual-network-family in compartment cmp-lz-%s-network' %
          [runner_principal, environment_name],
          '%s to use subnets in compartment cmp-lz-%s-network' %
          [runner_principal, environment_name],
          '%s to use vnics in compartment cmp-lz-%s-network' %
          [runner_principal, environment_name],
          '%s to manage private-ips in compartment cmp-lz-%s-network' %
          [runner_principal, environment_name],
          "%s to manage vcns in compartment cmp-lz-%s-network where any {request.operation = 'CreateNetworkSecurityGroup', request.operation = 'DeleteNetworkSecurityGroup'}" %
          [runner_principal, environment_name],
        ],
      },
      ['PCY-LZ-%s-GITOPS-SECURITY-KEY' % std.asciiUpper(environment)]: {
        name: 'pcy-lz-%s-gitops-security' % environment_name,
        description:
          'MVP GitOps runner access for approved shared-security services.',
        compartment_id: environment_key,
        statements: [
          '%s to read ons-topics in compartment cmp-lz-%s-security' %
          [runner_principal, environment_name],
          '%s to use vaults in compartment cmp-lz-%s-security' %
          [runner_principal, environment_name],
          '%s to manage instance-images in compartment cmp-lz-%s-security' %
          [runner_principal, environment_name],
          '%s to use vss-family in compartment cmp-lz-%s-security' %
          [runner_principal, environment_name],
          '%s to use bastion in compartment cmp-lz-%s-security' %
          [runner_principal, environment_name],
          '%s to read logging-family in compartment cmp-lz-%s-security' %
          [runner_principal, environment_name],
        ],
      },
    }
