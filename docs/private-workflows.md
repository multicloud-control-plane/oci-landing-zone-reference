# Optional private workflows

[Back to README](../README.md)

Use the existing [CLI helper flow](terraform-cli.md) as the execution path.
Install these templates when protected dispatch/approval and workflow evidence
are useful. They do not provision runners, buckets or repositories. Repository
and source setup belongs to [Getting started](getting-started.md); producer
publication belongs to [generation and dependencies](generation-and-dependencies.md).

## Install in the private configuration repository

Cloud Operations copies the selected templates from the reference checkout:

```bash
mkdir -p customer/.github/workflows
cp templates/workflows/stack-plan-apply.yml customer/.github/workflows/stack-plan-apply.yml
cp templates/workflows/project-handoff.yml customer/.github/workflows/project-handoff.yml
```

Review/commit the files in the private repository. The resulting source tree is:

```text
customer/
  .github/workflows/
    stack-plan-apply.yml
    project-handoff.yml
  config/
    model.jsonnet
    .terraform.lock.hcl             # approved provider lock
    firewall-bindings.json          # selected region, required for hub final
    studio/                        # optional configuration: studio exports
      studio-fra.zip
      studio-ams.zip
```

The templates check out this tree as `config-repo/` and the approved reference
as `reference/`. Workflow-generated revisions live in private runner directories,
not in source Git. The handoff workflow always uses `config/model.jsonnet`;
promote Studio's normalized model before using it.

## Variables and activation

Set GitHub Actions variables in the private configuration repository. These are
installation examples; substitute approved values. `REFERENCE_COMMIT` pins this
reference, independently of its upstream lock. The readiness variables must
equal the literal string `true`.

| Variable | Example value / meaning | Template |
| --- | --- | --- |
| `REFERENCE_COMMIT` | Approved full 40-character reference SHA (`git rev-parse HEAD` in the approved checkout) | Both |
| `FOUNDATION_RUNNER_LABELS` | `["self-hosted","linux","foundation-fra-01"]`, matching one dedicated runner | Both |
| `PRIVATE_OUTPUTS_ROOT` | `/srv/foundation/fra/private-outputs`, reviewed producer tree including common | Both |
| `FOUNDATION_AUTOMATION_READY` | `true`, after plan/apply adoption checks | Stack |
| `TERRAFORM_VERSION` | `1.15.8`, fixed approved version supporting the native OCI backend | Stack |
| `PRIVATE_OPERATION_ROOT` | `/srv/foundation/fra/operations`, private persistent workdirs | Stack |
| `STATE_BUCKET` | `customer-fra-foundation-state`, existing versioned state bucket | Stack |
| `STATE_NAMESPACE` | `CUSTOMER_NAMESPACE`, actual Object Storage namespace | Stack |
| `OCI_TENANCY_OCID` | `ocid1.tenancy.oc1..REPLACE_WITH_ACTUAL_TENANCY` | Stack |
| `HOME_REGION` | `eu-frankfurt-1` | Stack, Studio source only |
| `LANDING_ZONE_ENVIRONMENT` | `shared` | Stack, Studio source only |
| `NOTIFICATION_EMAIL` | `operations@example.com`, replace with approved address | Stack, Studio source only |
| `FOUNDATION_PROJECT_HANDOFF_READY` | `true`, after handoff/consumer adoption checks | Handoff |

Manually configure protected `foundation-plan`, `foundation-apply` and, when
installed, `foundation-handoff` environments. Require independent approval of
apply and prohibit self-approval. Verify trusted code revision, runner identity,
bucket permissions, private path access and provider lock before setting readiness.
Both templates run only in a **private repository, on `refs/heads/main`**, with
their own readiness variable set. A dispatch skipped by these gates is not
deployment or handoff evidence.

## Dispatch one operation and review its saved plan

The stack template takes `configuration` (`model` by default, or `studio`),
`stack` (exact catalog ID) and `stage` (`complete`, `bootstrap` or `final`). Start
with `stack: common`, `stage: complete`, then follow the
[regional sequence](generation-and-dependencies.md#initial-order-frankfurt-example).
Studio mode imports `config/studio/*.zip` with the three Studio variables above;
model mode reads `config/model.jsonnet`. Final reads `config/firewall-bindings.json`.

Use a **single dedicated runner** for both plan/apply jobs: the template passes
a filesystem path between jobs rather than uploading the plan. Labels selecting
a pool of independent machines are insufficient. Retain that path through
approval. The plan job records its private `plan.txt` path; the reviewer checks
the exact saved plan, source revision, inputs, lock, IAM/routing and state target.
Apply verifies hashes of the plan, tfvars, backend, lock, config and dependencies
before executing that plan. Jobs serialize by selected stack; also prevent
conflicting execution through other tools against the same state key.

The template has one fixed runner/bucket/output variable set. It does **not**
select a regional runner or bucket from the stack input. Use an approved regional
installation or an explicitly reviewed installation-specific selection before
dispatching another region; verify its bucket and output tree correspond to the
catalog's managed region. Do not change shared variables while a plan awaits
apply. After apply, verify OCI and manually publish outputs from the printed
`<job_root>/inputs/outputs` path before dispatching consumers. Retain/recover/clean
private operation directories under the installation's recovery policy.

## Artifact-only project handoff

The handoff template takes `environment` (`dev`, `test`, `uat`, `prod`), `project`
(DNS name without repository prefix) and `region` (declared OP02 region). It
generates from the promoted model, reads verified common and selected environment
outputs, calls the canonical schema-3 renderer and the catalog consumer gate,
and uploads a package for seven days. It performs no deployment, repository
creation or publication to project repositories.

It records genuine `GITHUB_REPOSITORY`, `GITHUB_WORKFLOW`, `GITHUB_RUN_ID` and
`GITHUB_SHA` from the protected run. Retain the package and run evidence before
artifact expiry. Schema 3 requires real workflow provenance even if deployment
and publication were manual: use this artifact-only job or an existing protected
job configured to call the same commands. Do not invent a run ID/workflow or
substitute a manual terminal session as workflow evidence.

Cloud Operations confirms producer deployment evidence and validates the
downloaded package against the matching reviewed catalog, then publishes through
the human handoff and separate project NSG PRs described in
[project onboarding](project-onboarding.md). Command/gate selection for an
existing MCCP installation belongs to [MCCP installation](studio-mccp-flow.md).
