# Tasks: Foundation Delivery Contract

**Input**: Design documents in `specs/001-foundation-delivery-contract/`.

**Prerequisites**: [Specification](spec.md), [plan](plan.md), [research](research.md),
[entities](data-model.md), [interfaces](contracts/delivery.md), [quickstart](quickstart.md).

**Tests**: Execute existing checks and focused smoke calls. No new application test suite
or runtime behavior is planned. Synthetic artifacts stay ignored; record results in
`specs/001-foundation-delivery-contract/acceptance.md`.

**Organization**: Tasks are grouped by story; all three stories are P1 because each is
necessary for the stated delivery contract. Completed implementation is reused and assessed.

## Format: `[ID] [P?] [Story] Description`

Sequential task IDs follow execution dependencies. Story labels identify the scenario.
No task is marked `[P]` because all evidence-writing tasks share `acceptance.md`; independent
check commands can be batched, followed by sequential evidence updates.

## Path Conventions

Paths are repository-relative. Authoring outputs live in the selected `specs/` feature.
Ignored revisions use `generated/sdd-*`; smoke artifacts use `.runtime/sdd-smoke-001`.

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Verify feature selection, completed quality checklist, resolved design artifacts, and constitution alignment in specs/001-foundation-delivery-contract/spec.md and .specify/feature.json before acceptance execution.

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T002 Create specs/001-foundation-delivery-contract/acceptance.md with FR-001–FR-015, SC-001–SC-006, all user-story scenarios, command-result slots, and separate pending installation checks per FR-014.
- [x] T003 Verify upstream.lock.json pins, existing .gitignore artifact exclusions, and documented private/credential-free execution boundaries; record findings in specs/001-foundation-delivery-contract/acceptance.md per FR-015 and Constitution I/IV.

**Checkpoint**: Requirements have an evidence destination and local artifacts are isolated.

## Phase 3: User Story 1 - Generate and review a supported design (Priority: P1)

**Goal**: Prove current authoritative generation, Studio intake, and reproducibility.
**Independent Test**: Model and Studio generation/catalog/family checks plus existing import cases.

- [x] T004 [US1] Run python3 -m unittest discover -s tests -v once; record suite and Studio preservation/source/negative-input results in specs/001-foundation-delivery-contract/acceptance.md using tests/test_studio.py and tests/test_reference.py per FR-001–FR-003, SC-001/SC-003 and US1/AC1–AC3.
- [x] T005 [US1] Generate examples/two-region.jsonnet twice, compare model/catalog/configurations/seeds, validate catalog/facade families, and import/validate tests/fixtures/studio-hub-b.jsonnet; record exact counts in specs/001-foundation-delivery-contract/acceptance.md per FR-001–FR-003 and SC-001.

**Checkpoint**: US1 has current positive and negative evidence; fixture counts are recorded.

## Phase 4: User Story 2 - Prepare independent foundation stacks (Priority: P1)

**Goal**: Verify selected operation/state/region contracts without deployment.
**Independent Test**: Inspect catalog, prepare all phases, and stage two independent runtime roots.

- [x] T006 [US2] Inspect generated/sdd-model-001/catalog.json and owning docs for OP00/global, OP01 hub phases, OP02/OP03 observability, OP04/common, and regional state/dependency boundaries; record mapping in specs/001-foundation-delivery-contract/acceptance.md per FR-004–FR-006, FR-009 and US2/AC1.
- [x] T007 [US2] Use tests/output_fixtures.py and scripts/reference.py to prepare common before outputs and all 13 model phases with same-region synthetic bindings; reuse existing suite ORM/conflict/missing/cross-region results and record them in specs/001-foundation-delivery-contract/acceptance.md per FR-006/FR-007, SC-002/SC-003 and US2/AC2–AC3.
- [x] T008 [US2] Call scripts/runtime.py stage_workdir for common/FRA and dev/AMS under .runtime/sdd-smoke-001; verify preserved provider aliases and catalog backend region/key without Terraform, recording results in specs/001-foundation-delivery-contract/acceptance.md per FR-007 and SC-002.

**Checkpoint**: US2 offline preparation passes; deployment scenario US2/AC4 is separately pending.

## Phase 5: User Story 3 - Hand a project boundary to MCCP (Priority: P1)

**Goal**: Verify machine/human boundary, routing, state provenance, and separate NSG ownership.
**Independent Test**: Render/consume prod-shop and dev-shop fixture packages and reuse lifecycle cases.

- [x] T009 [US3] Render prod/dev shop fixture packages using scripts/mccp.py and validate them through scripts/reference.py validate-handoff; check schema-3 JSON/Markdown, repository routing, catalog state owners, and INFRA/VCN NSG bindings, recording results in specs/001-foundation-delivery-contract/acceptance.md per FR-010–FR-013, SC-004 and US3/AC1.
- [x] T010 [US3] Confirm wrong source/state/region packages are rejected and reuse onboarding/retirement isolation and canonical/imported synchronization evidence from tests/test_mccp.py and tests/test_studio.py; record coverage in specs/001-foundation-delivery-contract/acceptance.md per FR-003/FR-011/FR-012, SC-003/SC-004 and US3/AC2–AC3.
- [x] T011 [US3] Review docs/project-onboarding.md, docs/studio-mccp-flow.md, docs/private-workflows.md and docs/validation.md for reviewed execution/publication, genuine run evidence, installation mapping, and project privilege boundaries; mark real acceptance pending in specs/001-foundation-delivery-contract/acceptance.md per FR-008/FR-009/FR-013/FR-014, SC-005/SC-006, US2/AC4 and US3/AC4.

**Checkpoint**: US3 package/consumer contracts pass offline; actual MCCP installation remains pending.

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T012 Run scripts/check_docs.py, validate task/checklist/placeholder formatting, verify whitespace and unchanged gen/scripts/tests/workflows/upstream sources against HEAD, and record scope evidence in specs/001-foundation-delivery-contract/acceptance.md per FR-014/FR-015 and Constitution V.
- [x] T013 Review complete requirement/scenario/SC traceability in specs/001-foundation-delivery-contract/acceptance.md, complete task statuses in specs/001-foundation-delivery-contract/tasks.md, and run convergence against spec/plan/tasks; append only concrete buildable gaps if any per FR-014 and SC-005.

## Dependencies & Execution Order

Setup T001 -> foundational T002/T003 -> US1 T004/T005 -> US2 T006–T008 -> US3 T009–T011
-> cross-cutting T012/T013. US2 and US3 negative/lifecycle checks reuse T004's single suite
run; no optional repeat is needed after application source remains unchanged.

Each story can independently be assessed with the committed example/fixtures. This run uses
US1's generated revision for smoke checks to avoid redundant generation. Evidence writes
are sequential, even when independent tool commands run together.

## Parallel Examples

- **US1**: Generate the model and import the Studio fixture in different ignored directories;
  their catalog/facade checks can run independently. Compare a repeated model after generation.
- **US2**: Inspect common and dev/AMS staged backends independently after their preparation;
  both use separate workdirs. Record the combined result sequentially.
- **US3**: Validate prod/dev package CLIs independently after rendering separate package paths;
  write the shared acceptance record after inspecting both results.

## Implementation Strategy

Deliver US1's reproducible design evidence first, then US2's selected-stack preparation,
then US3's project boundary evidence. Use existing tests/helpers and owning docs throughout.
The current implementation already supplies the behavior; completion here means verifying
and recording the offline contract. Keep real-installation scenarios explicitly pending.
A confirmed application defect requires a scoped design amendment, focused repair and checks;
a missing deployment result alone does not justify new runtime code.

## Phase 7: User Story 4 - Contributor Contract Alignment (Priority: P2)

**Goal**: Make the contributor guide match the current project purpose and governing contracts.
**Independent Test**: Review the guide against the constitution and owning docs; all local
links and whitespace checks must pass. This phase follows the owner's subsequent request.

- [x] T014 [US4] Review and update AGENTS.md with the delivery purpose, constitution/current SDD links, operation/state/handoff boundaries, private data/publication scope, retained helpers, and compatible Python/Jsonnet prerequisites per FR-016 and US4/AC1.
- [x] T015 [US4] Validate AGENTS.md and amended SDD artifact links/fences/whitespace, review obligations against owning docs, and append current acceptance evidence to specs/001-foundation-delivery-contract/acceptance.md per FR-016, SC-007 and US4/AC1.
