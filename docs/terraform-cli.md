# Terraform CLI runtime

[Back to README](../README.md)

Use a private approved pipeline when Day 2 needs Terraform plus scripts/API/
Ansible. Keep configuration and IaC code in separate repositories, and use a
dedicated scoped runner with Instance Principal.

```bash
python3 scripts/reference.py prepare \
  --generated generated/revision-001 --stack workload_prod/eu-frankfurt-1 \
  --outputs private-outputs --destination .runtime/prod-fra-inputs --runtime cli
python3 scripts/runtime.py \
  --generated generated/revision-001 --stack workload_prod/eu-frankfurt-1 \
  --prepared .runtime/prod-fra-inputs --destination .runtime/prod-fra-orchestrator \
  --bucket customer-fra-foundation-state --namespace CUSTOMER_NAMESPACE \
  --tenancy ocid1.tenancy.oc1..REPLACE_WITH_ACTUAL_TENANCY
```

Replace example runtime values. The tool stages the complete pinned checkout,
preserving facade `../` source and home/secondary provider region logic. Reviewed
override files select Instance Principal. The backend uses the catalog state
key and managed region. The private bucket must exist and have versioning.

In the authorized runner, use a Terraform version supporting the native OCI
backend (the inspected upstream workflow uses 1.15.8). Review and retain its
provider lock in the approved IaC code; use read-only lock mode afterward.

```bash
cd .runtime/prod-fra-orchestrator/rms-facade
terraform init -backend-config=backend.tfbackend
terraform validate
terraform plan -var-file=inputs.tfvars.json -out=operation.tfplan
# Independent reviewer approves this exact source revision and saved plan.
terraform apply operation.tfplan
```

Plan/apply use the same workspace, lock and inputs. Plans may contain sensitive
data; archive privately. Verify OCI backend locking and serialize by state key.
Publish official output JSON from the prepared outputs directory to the region's
private store. Keep local replicas of global outputs for regional independence.

The [private workflow template](../templates/workflows/stack-plan-apply.yml)
provides the reviewed plan/apply pattern. Configure protected environments,
trusted code revision, scoped runner, private output paths and required
review/check gates before enabling it. The public reference runs no privileged
jobs. Runtime change and brownfield state migration need separate windows.

Template installation requirements:

- Use a single dedicated runner selected by `FOUNDATION_RUNNER_LABELS` so both
  jobs share the same private operation directory. Use a regional installation
  or select a regional runner/bucket per operation when independence is required.
- Configure `REFERENCE_COMMIT` as an approved 40-character SHA, a fixed
  `TERRAFORM_VERSION`, `STATE_BUCKET`, `STATE_NAMESPACE`, `OCI_TENANCY_OCID`,
  `PRIVATE_OPERATION_ROOT` and `PRIVATE_OUTPUTS_ROOT`.
- Keep `config/model.jsonnet`, reviewed `config/.terraform.lock.hcl` and optional
  `config/firewall-bindings.json` in the private configuration repository.
- Alternatively select `configuration: studio` and install exports/metadata as
  described in [Studio import](studio-import.md); both modes share the same
  selected-operation plan/apply flow.
- The input output tree must already contain reviewed regional artifacts.
  Publish/replicate successful outputs before dispatching consumers.
- Protect both environments and prohibit self-approval of foundation-apply.
  Apply verifies the saved plan, variables, backend, lock and resolved config/
  dependencies. Jobs serialize per selected stack. Retain the plan privately
  through approval and clean up operation directories under the recovery policy.
