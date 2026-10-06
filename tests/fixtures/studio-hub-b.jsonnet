// Synthetic Studio-shaped source, with explicit non-default subnet allocations.
{
  realm: 'oc1', region: 'eu-frankfurt-1', region_short_name: 'fra', cis_level: 1,
  hub: { kind: 'hub_b', network: { vcn: '10.240.0.0/21', subnets: {
    lb: '10.240.5.0/24', fw: '10.240.1.0/24', mgmt: '10.240.2.0/24',
    mon: '10.240.3.0/24', dns: '10.240.4.0/24',
  } } },
  environments: {
    prod: {
      project_network: { network: { vcn: '10.240.64.0/21', subnets: {
        web: '10.240.65.0/24', app: '10.240.66.0/24',
        db: '10.240.67.0/24', infra: '10.240.68.0/24',
      } } },
      projects: { shop: {} },
      platforms: { data: { network: { vcn: '10.240.96.0/21', subnets: { app: '10.240.99.0/24' } } } },
    },
  },
  shared_platforms: { ops: { network: { vcn: '10.240.32.0/21', subnets: { app: '10.240.34.0/24' } } } },
  security_targets: [],
}
