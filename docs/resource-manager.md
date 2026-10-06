# Resource Manager runtime

[Back to README](../README.md)

Keep ORM during adoption if the customer already uses it. Create one stack per
catalog execution in its managed region, with the locked Orchestrator commit
and working directory `rms-facade`. Hub bootstrap/final share one ORM state.

```bash
python3 scripts/reference.py prepare \
  --generated generated/revision-001 --stack workload_prod/eu-frankfurt-1 \
  --outputs private-outputs --destination .runtime/prod-fra \
  --runtime orm --bucket customer-private-configurations
```

Upload prepared config/dependencies to the private Object Storage bucket using
the exact names from `inputs.tfvars.json`. Set tenancy OCID in ORM and grant the
approved operation permissions plus private input/output object access.

| Verified facade variable | Purpose |
| --- | --- |
| `configuration_source = "ocibucket"` | Private inputs |
| `oci_configuration_bucket` | Shared config/dependency bucket |
| `oci_configuration_objects` | Complete configuration |
| `oci_dependency_objects` | Reviewed aggregate dependencies |
| `save_output = true`, `output_format = "json"` | Official outputs |
| `oci_object_prefix` | Unique producer prefix |

Use `--stage bootstrap` or `--stage final --bindings customer/config/firewall-bindings.json`
for hub stages. Download actual files from `outputs/<stack-id>/` into the local
preparation tree. Verify persistence permissions and published artifacts.

Review the complete plan, stop unexpected destroys/replaces/IAM/routing/monitoring
changes, and obtain independent approval before Apply. Verify OCI behavior.
Do not cascade downstream applies. Configuration storage is not the ORM state.

Preparation enforces a conservative 1,000,000-byte limit on each remote config
and dependency file. A bucket alone does not remove the facade's content limit.
