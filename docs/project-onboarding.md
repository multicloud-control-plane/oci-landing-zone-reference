# OP04 project onboarding

[Back to README](../README.md)

OP04 prepares a reviewed project-management change against consolidated IAM
in common; it does not create a second IAM state owner.

```bash
python3 scripts/onboard.py --model customer/model.jsonnet \
  --environment dev --project billing --output customer/model-next.json
python3 scripts/reference.py generate --model customer/model-next.json \
  --output generated/revision-002
```

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

```bash
python3 scripts/reference.py handoff \
  --generated generated/revision-002 --environment dev --project billing \
  --region eu-frankfurt-1 \
  --compartments private-outputs/common/compartments_output.json \
  --network private-outputs/workload_dev/eu-frankfurt-1/network_output.json \
  --source-repository example/private-foundation \
  --source-workflow 'MCCP project foundation handoff' \
  --source-run "$HANDOFF_SOURCE_RUN" --source-commit "$HANDOFF_SOURCE_COMMIT" \
  --output handoffs/dev-billing-fra
```

Set the variables and replace example provenance with the exact successful protected handoff run.
Before approving publication, verify that producer outputs reflect the applied
reviewed configuration. The command requires a new empty output directory and
produces:

- `project-foundation-handoff.json`: the existing MCCP schema-3 machine contract.
- `environments/dev/environment_information.md`: the canonical human handoff.
- `oci/dev/<region>/network/project-nsgs.json`: a deployable project-owned seed.

Publish the human handoff through its reviewed project PR. Publish the NSG seed
through a separate workload PR so that the project's existing Platform CI
plans/applies it. Its OCI changes belong to the project state, never common or
OP02. Existing project NSGs require a reviewed state transfer before changing
ownership or compartment; see [migration](migration.md).

The [private artifact workflow](../templates/workflows/project-handoff.yml)
automates generation/validation without deployment or repository creation.
Install it with a protected `foundation-handoff` environment and reviewed
producer outputs; set `FOUNDATION_PROJECT_HANDOFF_READY` only after adoption checks.
See [MCCP installation](studio-mccp-flow.md) for the catalog-based consumer gate.

Use separate prod/non-prod project repositories, executor and workload-state
bucket. Foundation grants effective permissions; JSON constraints do not enforce
IAM. Retirement removes project workload resources first, then common IAM and
handoff access, through separate reviews with recovery evidence.

After workload retirement, prepare the foundation change with
`scripts/onboard.py --operation retirement` using the same model/environment/project/output
arguments. It removes only that declaration and generated seeds; existing workload
states, project repositories and handoff access require the separate retirement
process. Review the common plan's expected IAM deletions before applying it.
