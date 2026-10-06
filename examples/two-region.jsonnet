// Synthetic reference values. Copy into a customer-controlled private repository.
{
  home_region: 'eu-frankfurt-1',
  landing_zone_environment: 'shared',
  notification_email: 'operations@example.com',
  projects: { prod: { shop: {} }, dev: { shop: {} } },
  regions: {
    'eu-frankfurt-1': {
      short_name: 'fra',
      hub: '10.100.0.0/21',
      environments: {
        prod: { network: '10.100.64.0/21', platforms: {
          data: { vcn: '10.100.96.0/21', subnets: { app: '10.100.96.0/24' } },
        } },
        dev: { network: '10.100.128.0/21', platforms: {} },
      },
      shared_platforms: {
        ops: { vcn: '10.100.32.0/21', subnets: { app: '10.100.32.0/24' } },
      },
    },
    'eu-amsterdam-1': {
      short_name: 'ams',
      hub: '10.101.0.0/21',
      environments: {
        prod: { network: '10.101.64.0/21', platforms: {
          data: { vcn: '10.101.96.0/21', subnets: { app: '10.101.96.0/24' } },
        } },
        dev: { network: '10.101.128.0/21', platforms: {} },
      },
      shared_platforms: {
        ops: { vcn: '10.101.32.0/21', subnets: { app: '10.101.32.0/24' } },
      },
    },
  },
}
