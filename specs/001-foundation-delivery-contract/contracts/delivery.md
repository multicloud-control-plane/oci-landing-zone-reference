# Existing Delivery Interfaces

## Generation and Studio intake — US1

Use `scripts/reference.py generate` with the reviewed model, or `import-studio` with a
supported ZIP/literal source and explicit home/LZ settings. Both produce a new revision
validated by `reference.py validate` and `check_contract.py`. Studio additionally retains
original source/hashes and an import report. Supported scope and promotion belong to
[Getting started](../../../docs/getting-started.md) and
[Studio import](../../../docs/studio-import.md). Resource definitions stay in pinned OE.

## Selected-stack execution — US2

`reference.py prepare` takes a generated revision, catalog stack ID, stage, producer-output
root, new prepared destination, runtime mode, and explicit firewall bindings as needed.
CLI mode supplies local files; ORM mode supplies private OCI bucket/object inputs. A global
stack starts without producer outputs. Regional dependencies are resolved against catalog
producers, rejecting conflicts and wrong-region resources.

`runtime.py` stages a complete new pinned Orchestrator workdir from CLI prepared inputs,
using the selected stack's state key/region and preserving provider aliases. These helpers
run neither OCI nor Terraform. Reviewed execution/publication belongs to
[CLI](../../../docs/terraform-cli.md), [ORM](../../../docs/resource-manager.md), and
[generation/dependencies](../../../docs/generation-and-dependencies.md). The existing
[optional workflows](../../../docs/private-workflows.md) remain installation choices.

## OP04 and MCCP delivery — US3

`onboard.py` updates canonical and imported declarations without changing regional foundation
resources. `reference.py handoff` accepts the declared environment/project/region, verified
common and workload outputs, and genuine protected repository/workflow/run/commit evidence.
It calls the pinned MCCP renderer and emits schema-3 JSON, canonical environment Markdown,
and a separate bound project NSG manifest in INFRA using the assigned VCN.

`reference.py validate-handoff` takes the selected foundation's protected catalog, both
machine/human files, and expected source repository. It verifies exact contract, project/
region/repository routing, distinct assigned targets, real state owners, and Markdown
consistency. OP04 state is `common/terraform.tfstate`; OP02 state belongs to the selected
`workload_<environment>/<region>` stack. Production uses `prod-<project>`/`production`;
dev/test/uat use `nonprod-<project>`/`shared-nonprod-v2`.

Installation mapping, source provenance verification, human handoff PR, separate project
NSG PR, and live MCCP requests remain governed by
[the owning integration guide](../../../docs/studio-mccp-flow.md) and
[project onboarding](../../../docs/project-onboarding.md). A locally valid package does
not prove that a selected live MCCP installation is connected.

## Acceptance evidence

Fixture outputs and fixture run metadata are restricted to ignored local artifacts and
must be labeled synthetic. Real acceptance remains the
[installation checklist](../../../docs/validation.md#real-installation-acceptance).
No new interface or compatibility promise is introduced by this feature.
