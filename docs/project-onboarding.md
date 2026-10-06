# OP04 project onboarding

[Back to README](../README.md)

OP04 prepares a reviewed project-management change against consolidated IAM
in common; it does not create a second IAM state owner.

Use the canonical private source established in [Getting started](getting-started.md).
Keep `onboard.py` for this change: it synchronizes the top-level project
declaration and every imported `studio_configs` region. Hand editing only one
copy can lose the project at regeneration.

```bash
python3 scripts/onboard.py --model customer/config/model.jsonnet \
  --environment dev --project billing --output customer/config/model-next.jsonnet
python3 scripts/reference.py generate --model customer/config/model-next.jsonnet \
  --output generated/revision-002
python3 scripts/reference.py validate --generated generated/revision-002
python3 scripts/check_contract.py --generated generated/revision-002
```

Review the delta, then promote the candidate to `customer/config/model.jsonnet`
through the private configuration PR. The optional workflows read that canonical
path. Retain the matching generated revision as evidence for execution/gating.

Projects use the MCCP root plus Application, Database and Infrastructure children,
their four admin groups, and generic official TBAC policies. The reference reuses
the pinned MCCP TBAC adapter and the official OE add-on. Review/apply the complete
common configuration in the home region. Project naming follows MCCP: dev/test/uat/prod
and a DNS name of at most 30 characters, without a derived repository prefix.

Both model and Studio generation emit project NSG seeds separately under
`projects/<environment>-<project>/<region>/project-nsgs.json`. Their keys, names
and rules are preserved; handoff binds them to the shared VCN and the project's
INFRA compartment. They are absent from OP02 and have no foundation state.
Later onboarding changes common IAM and the new project seed, leaving OP02
unchanged. Never use seed regeneration to overwrite managed project manifests.

For a project runner, explicitly set `project_runner_dynamic_group` in the private
model to an existing approved dynamic group. Common then emits MCCP's fixed
PROJECTS/NETWORK/SECURITY runner policies once per environment, including the
conditional shared-VCN grant for NSG create/delete. With no selected principal,
no runner grants are emitted. This reference does not create a runner or its
identity; install project executors and workload-state access separately.

## Render with real protected-run evidence

After approved common execution, verify actual project IAM and publish refreshed
`common/compartments_output.json`. Verify that the selected environment's network
outputs reflect its applied configuration. Set all four `HANDOFF_SOURCE_*`
variables below to the actual private repository, workflow name, run ID and
40-character source commit of the protected job generating the package:

```bash
python3 scripts/reference.py handoff \
  --generated generated/revision-002 --environment dev --project billing \
  --region eu-frankfurt-1 \
  --compartments private-outputs/common/compartments_output.json \
  --network private-outputs/workload_dev/eu-frankfurt-1/network_output.json \
  --source-repository "$HANDOFF_SOURCE_REPOSITORY" \
  --source-workflow "$HANDOFF_SOURCE_WORKFLOW" \
  --source-run "$HANDOFF_SOURCE_RUN" --source-commit "$HANDOFF_SOURCE_COMMIT" \
  --output handoffs/dev-billing-fra
```

Use an existing protected job or the optional
[artifact-only workflow](private-workflows.md#artifact-only-project-handoff) to
obtain genuine provenance. Manual deployment/publication does not remove this
schema-3 requirement. Do not fabricate a workflow/run for a terminal invocation.
The command requires a new empty output directory and
produces:

- `project-foundation-handoff.json`: the existing MCCP schema-3 machine contract.
- `environments/dev/environment_information.md`: the canonical human handoff.
- `oci/dev/<region>/network/project-nsgs.json`: a deployable project-owned seed.

## Validate and publish manually

Before publication, Cloud Operations runs the
[catalog consumer gate](studio-mccp-flow.md#mccp-installation-and-consumer-gate)
against the matching reviewed revision and package. If using the artifact-only
template, download/unpack its package into `handoffs/dev-billing-fra/` for the
documented gate paths. Confirm distinct APP/DB/INFRA
compartments, environment/region, subnet roles, source-run evidence and actual
state owners (`common/terraform.tfstate` and the selected OP02 state).

In the correctly routed private project repository (`nonprod-billing` for dev,
`prod-billing` for prod), open reviewed PRs with these exact package files:

| Artifact | Manual publication | Completion check |
| --- | --- | --- |
| `project-foundation-handoff.json` | Retain with protected-run/deployment evidence in the approved private evidence store | Machine contract and catalog gate pass |
| `environments/dev/environment_information.md` | Copy to the same path in the project repository's human handoff PR | Reviewed targets/routing and consumer can read the published handoff |
| `oci/dev/eu-frankfurt-1/network/project-nsgs.json` | Copy to the same path in a separate workload PR | Existing Platform CI reviews/plans/applies NSGs in project INFRA |

Project NSG OCI changes belong to project state, never common or OP02. An initial
seed is not a replacement for a subsequently managed manifest. Existing project
NSGs require a reviewed state transfer before changing ownership or compartment;
see [migration](migration.md).

The [private artifact workflow](../templates/workflows/project-handoff.yml)
automates generation/validation without deployment or repository creation.
For its installation/variables, see [private workflows](private-workflows.md).
Successful artifact generation is followed by the operator publication above.

Use separate prod/non-prod project repositories, executor and workload-state
bucket. Foundation grants effective permissions; JSON constraints do not enforce
IAM. Retirement removes project workload resources first, then common IAM and
handoff access, through separate reviews with recovery evidence.

After workload retirement, prepare the foundation change with
`scripts/onboard.py --operation retirement` using the same model/environment/project/output
arguments. It removes only that declaration and generated seeds; existing workload
states, project repositories and handoff access require the separate retirement
process. Review the common plan's expected IAM deletions before applying it.
