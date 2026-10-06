# Terraform CLI runtime

[Back to README](../README.md)

Use an approved private runner when Day 2 needs Terraform plus scripts/API/
Ansible. Start with the reviewed source/revision from
[Getting started](getting-started.md) and the sequence in
[generation and dependencies](generation-and-dependencies.md).

## Runner prerequisites

Cloud Operations manually installs a dedicated scoped OCI runner and approved
Instance Principal dynamic group/policies, a private state bucket in the managed
region with versioning, and private operation/output directories. Verify state
and input/output access for the selected operation. Home-region common needs
its global IAM role; regional executors need their operation's regional role.
Installing this reference creates none of these resources.

Install the generation tools and a fixed Terraform version supporting the native
OCI backend (the inspected pinned upstream workflow uses 1.15.8). First stage
common below, then create and privately review the provider lock using the
one-time setup before normal execution. Subsequent executions reuse that approved
lock in read-only mode.

## Prepare and stage common first

```bash
python3 scripts/reference.py prepare \
  --generated generated/revision-001 --stack common --stage complete \
  --outputs private-outputs --destination .runtime/common-inputs --runtime cli
python3 scripts/runtime.py \
  --generated generated/revision-001 --stack common \
  --prepared .runtime/common-inputs --destination .runtime/common-orchestrator \
  --bucket customer-fra-foundation-state --namespace CUSTOMER_NAMESPACE \
  --tenancy ocid1.tenancy.oc1..REPLACE_WITH_ACTUAL_TENANCY
```

Replace example runtime values with the approved home-region bucket, namespace
and tenancy. `runtime.py` stays the default: it stages a **new complete pinned
Orchestrator checkout**, preserving facade `../` source and provider aliases.
It prevents workdir, state-key and provider-override mistakes; do not maintain a
parallel hand-written HCL staging recipe. The tool runs no Terraform. It
preserves home/secondary provider region logic and adds Instance Principal
provider overrides plus catalog-derived backend key/region. Inspect those files
before execution. For common the key is `common/terraform.tfstate`; hub
bootstrap/final both use `lze_shared/<region>/terraform.tfstate`.

## Create the first provider lock (one time)

Run this setup only on the authorized runner, after staging common above, when
`customer/config/.terraform.lock.hcl` does not yet exist. Start at the reference
root. The pinned facade and runtime helper do not supply a provider lock.

```bash
set -e
test ! -e customer/config/.terraform.lock.hcl
cd .runtime/common-orchestrator/rms-facade
terraform init -backend=false
```

This setup downloads the pinned facade's modules/providers and creates
`.terraform.lock.hcl` without initializing or accessing the state backend.
Review its provider versions, constraints and checksums against the approved
pinned code and runner platform. After that review, return to the reference
root and retain the generated lock in the private configuration checkout:

```bash
cd ../../..
cp .runtime/common-orchestrator/rms-facade/.terraform.lock.hcl customer/config/.terraform.lock.hcl
git -C customer add config/.terraform.lock.hcl
git -C customer commit -m "chore: retain reviewed foundation provider lock"
```

Complete the private repository's review/approval process for this commit before
normal execution or enabling the optional workflow. Existing approved locks skip
this setup. Normal initialization below enables the OCI backend using the
helper-generated `backend.tfbackend` for the selected common state and bucket;
it must use the approved lock with `-lockfile=readonly`.

## Execute on the authorized runner

```bash
cp customer/config/.terraform.lock.hcl .runtime/common-orchestrator/rms-facade/.terraform.lock.hcl
cd .runtime/common-orchestrator/rms-facade
terraform init -lockfile=readonly -backend-config=backend.tfbackend
terraform validate
terraform plan -var-file=inputs.tfvars.json -out=operation.tfplan
terraform show -no-color operation.tfplan > operation-plan.txt
# Independent reviewer approves this exact source revision, inputs, lock and saved plan.
terraform apply operation.tfplan
```

Plan/apply use the same workspace, lock and inputs. Plans may contain sensitive
data; archive privately. Verify OCI backend locking and serialize by state key.
Return to the reference checkout and follow the
[output publication steps](generation-and-dependencies.md#publish-deployed-outputs).
Common publishes compartments before hub bootstrap. For the next operation,
select the catalog ID/stage, use fresh inputs/workdir paths and the appropriate
regional state bucket; `runtime.py` derives that selected stack's state key.

The optional [private workflows](private-workflows.md) provide the same saved
plan/approval pattern. That guide owns installation paths, variables and
activation. The public reference runs no privileged jobs. Runtime changes and
brownfield state migration need separate windows.
