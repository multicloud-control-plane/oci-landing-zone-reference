# Acceptance Evidence: Foundation Delivery Contract

**Date**: 2026-10-06
**Scope**: Current offline contract verification; real-installation acceptance is pending.
**Specification**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Tasks**: [tasks.md](tasks.md)

## Authoring and environment gates

- T001: Feature selection resolves to this directory; all design artifacts exist; the
  16-item built-in requirement-quality checklist passes; constitution pre/post design gates pass.
- T002: This record tracks 15 requirements, 6 outcomes, and 11 acceptance scenarios.
- T003: All four upstream commits are immutable 40-character hashes. Existing Git ignore
  rules exclude generated revisions, runtime/prepared artifacts, customer configuration,
  outputs, private outputs, and handoffs. Application source, tests, workflow templates,
  and upstream lock match HEAD before verification. `.gitignore` already had a user-owned
  `.agents/` addition; this feature does not change it.
- Local tools: default Python is 3.9.6 and is below the documented prerequisite. Use the
  already-installed `/opt/homebrew/bin/python3.11` (3.11.15); Jsonnet is 0.22.0. Commands
  using `python3` in the quickstart assume that name selects Python 3.10 or later.
- Analyze gate: 15/15 requirements and 6/6 outcomes covered; 13 mapped tasks; zero critical,
  high, ambiguity, duplication, constitution-conflict, or unmapped-task findings.

## Current command results

- T004: `python3.11 -m unittest discover -s tests -v` passed: **47 tests in 189.719s, OK**.
  Existing tests cover positive/negative Studio, ownership/regions/dependencies, ORM inputs,
  MCCP scope/provenance and canonical/imported project lifecycle contracts. Log: ignored
  `.runtime/sdd-unit.log`. Fixture outputs are synthetic and are not deployment evidence.

- T005: Model generation and catalog validation passed with **11 stacks, 13 phases,
  4 project NSG seeds, 431 owned keys**; pinned facade family validation passed for
  **17 documents**. A second generation was byte-identical across **all 19 revision files**.
  Studio fixture import/catalog validation passed with **5 stacks, 6 phases, 1 project
  seed, 200 owned keys**; pinned facade validation passed for **7 documents**. Studio ZIP
  verification, source preservation, normalized regeneration, unsupported choices, and
  onboarding preservation are additionally covered by T004's existing suite.
- T006: Catalog inspection/assertions confirm 11 unique state keys, only `common` as
  global, all stack state regions equal their managed region, two OP01 bootstrap/final
  stage pairs sharing their respective single state, and OP04 targeting `common` with
  no handoff state. Existing ownership/observability tests and operating guides confirm
  OP02/OP03-local resources and explicit producer boundaries.

- T007: Common was prepared before any producer-output directory existed. All **13
  configuration phases** then prepared from the existing synthetic-output fixture with
  regional private-IP bindings; all resolved configuration files contain no `output://`
  or `binding://` references. The suite's ORM private-bucket test and conflict/missing/
  cross-region failure cases passed. The calls in `quickstart.md` were executed directly.
- T008: Fresh complete pinned Orchestrator workdirs staged for common/FRA and dev/AMS.
  Backend assertions matched `common/terraform.tfstate` / Frankfurt and
  `workload_dev/eu-amsterdam-1/terraform.tfstate` / Amsterdam. Default, `home`, and
  `secondary_region` OCI aliases retain Instance Principal overrides. The three upstream
  checkouts actually used by generation/staging/rendering match clean immutable pins.
- T009: Production and development packages rendered with the existing canonical helper;
  both CLI `validate-handoff` calls passed. Targets were `prod-shop` / `production` and
  `nonprod-shop` / `shared-nonprod-v2`. Both use common OP04 state and their own OP02 state.
  JSON/Markdown agree; project NSG manifests bind to their INFRA compartment and assigned
  VCN without remaining binding references. Run/source values are explicitly synthetic.
- T010: **Six additional package checks** rejected wrong state owner, source repository,
  and region for both environments, with boundary-specific errors. T004's onboarding,
  imported-model synchronization, NSG ownership, retirement isolation, undeclared project,
  distinct compartment, and subnet/VCN failure cases all passed.
- T011: Owning setup/execution/publication guides retain saved-plan review, approved private
  identities, live producer verification, genuine protected-run provenance, and reviewed
  human/NSG publication. The selected MCCP installation must explicitly map these commands
  and catalog-based consumer gate; that installation and actual Day 1/Day 2 behavior have
  not been changed or accepted here. Runner grants remain the documented opt-in environment
  scope; this evidence makes no claim of per-project runner identity isolation.

- T012: `python3.11 scripts/check_docs.py` passed for **45 Markdown files**; task/checklist
  formatting, fences, placeholders, dates, and complete FR/SC/scenario references passed.
  `git diff --check` passed. `gen/`, `scripts/`, `tests/`, `templates/`, `.github/`,
  `examples/`, existing `docs/`, and `upstream.lock.json` match HEAD. Only authoring/evidence
  artifacts were added by this phase; the pre-existing `.gitignore` edit remains untouched.

- T013: Convergence assessed the current implementation and artifacts against **15 FR,
  6 SC, 11 scenarios, 4 plan decisions, and 5 constitution principles**. No actionable
  missing/partial/contradicting/unrequested work was found within the declared offline
  scope. The assessment left `tasks.md` byte-for-byte unchanged and appended no convergence
  phase; implementation bookkeeping subsequently marked T013 complete. US2/AC4 and US3/AC4
  remain pending installation acceptance, rather than being relabeled as offline passes.

## Requirement and scenario traceability

Historical acceptance is supporting context; the current T004–T011 results above provide
this run's offline evidence. PASS below means the identified local contract or documentation
check passed, and does not imply successful cloud deployment.

| Requirement | Current evidence / owner | Result |
| --- | --- | --- |
| FR-001 | T004/T005; pinned OE projection, model and Studio generation | PASS offline |
| FR-002 | T004/T005; Studio ZIP/source/snapshot/preservation/unsupported tests and import report | PASS offline |
| FR-003 | T004/T005/T010; 19 byte-identical files, Studio regeneration and synchronized lifecycle | PASS offline |
| FR-004 | T006; explicit OP00–OP04 catalog and operation guides | PASS offline |
| FR-005 | T006; unique owners, common IAM, same hub state, OP04/common without handoff state | PASS offline |
| FR-006 | T004/T006/T007; regional state and producer/conflict/ownership checks | PASS offline; backend live checks pending |
| FR-007 | T007/T008; 13 selected preparations, ORM contract, catalog-derived staged backends | PASS offline; actual execution pending |
| FR-008 | T011; CLI/ORM/private-workflow and producer-publication guides | Documented; live enforcement pending |
| FR-009 | T006/T011; owning setup/runtime/workflow/onboarding guides use existing helpers | PASS documentation review |
| FR-010 | T009; canonical schema-3 JSON/Markdown and production/nonproduction routing | PASS fixture contract; genuine run/deployment pending |
| FR-011 | T009/T010; catalog consumer CLI and six state/source/region rejections | PASS offline; installed consumer mapping pending |
| FR-012 | T004/T009/T010; excluded foundation NSGs and bound INFRA/project-VCN seeds | PASS offline; live NSG lifecycle pending |
| FR-013 | T009/T011; separate routing/states, documented project privilege boundary | PASS contract review; effective IAM/MCCP requests pending |
| FR-014 | T002/T011/T012/T013; current traceability and separate installation list | PASS offline traceability and convergence |
| FR-015 | T003/T012; ignored synthetic artifacts, private execution/public CI boundaries | PASS scope/source verification |

| Scenario | Current evidence | Result |
| --- | --- | --- |
| US1/AC1 | T004/T005 model validation, families, exact repeated revision | PASS offline |
| US1/AC2 | T004 ZIP preservation/provenance/regeneration; T005 literal Studio import/report | PASS synthetic Studio contract; browser export not certified |
| US1/AC3 | T004 missing/duplicate/drifted/unsafe/unsupported export tests | PASS offline |
| US2/AC1 | T004/T006 ownership, catalog and regional/state assertions | PASS offline |
| US2/AC2 | T007/T008 all preparation phases, ORM inputs and staged backend/provider assertions | PASS offline |
| US2/AC3 | T004 conflict/missing/cross-region/duplicate-owner rejection tests | PASS offline |
| US2/AC4 | T011 existing operator procedure and installation checklist | PENDING real installation |
| US3/AC1 | T009 prod/dev canonical packages, state owners, bound NSGs and consumer CLI | PASS synthetic contract; deployed inputs still pending |
| US3/AC2 | T004/T010 wrong source/state/region and undeclared/malformed targets | PASS offline |
| US3/AC3 | T004/T010 synchronized onboarding and isolated retirement/NSG ownership | PASS offline; workload retirement is a live prerequisite |
| US3/AC4 | T011 selected installation mapping, publication and project request path | PENDING real installation |

| Outcome | Evidence | Result |
| --- | --- | --- |
| SC-001 | T004/T005 preservation/regeneration and 19 identical files | PASS offline |
| SC-002 | T006/T007/T008 unique catalog owners and 13 phases | PASS offline |
| SC-003 | T004/T010 published invalid-input cases plus six package rejections | PASS offline |
| SC-004 | T004/T009/T010 production/nonproduction packages and separate NSG owners | PASS offline |
| SC-005 | Full FR/scenario matrix and installation list; final T012/T013 review | PASS complete traceability; live checks separately pending |
| SC-006 | T006/T011 review of existing source -> selected execution -> MCCP publication guides | PASS documented path; actual operator installation acceptance pending |

## Pending real-installation acceptance

US2/AC4 and US3/AC4 require an approved OCI/MCCP test installation. The existing
[validation checklist](../../docs/validation.md#real-installation-acceptance) and
[MCCP integration guide](../../docs/studio-mccp-flow.md#mccp-installation-and-consumer-gate)
own these checks:

- Independent plan/apply review, scoped executor permissions, provider/backend locks,
  regional state placement/availability, successful staged deployment, and live output verification.
- Real firewall bindings and traffic isolation; effective IAM, tags, and observability.
- OP04 and project NSG lifecycle; state migration and rollback where needed.
- Selected MCCP installation command/gate mapping, authentic protected workflow evidence,
  reviewed human/NSG publication, and actual governed project Day 1/Day 2 execution.

No OCI call, Terraform validate/plan/apply, ORM job, live installation change, migration,
GitHub publication, or project deployment is part of this evidence run.

## Follow-up: Contributor Contract Alignment — 2026-10-06

The owner subsequently requested review, correction, and update of `AGENTS.md`.
US4, FR-016 and SC-007 were specified and planned before the guide change; T014–T015
track this documentation-only extension. The preceding 13-task runtime/contract evidence
remains the record of the earlier baseline and is not claimed as a new test execution.

- T014: Reviewed the contributor guide against the constitution, current SDD artifacts,
  design/responsibility matrix, source setup, execution/publication, migration, validation,
  and MCCP integration guides. Updated project purpose and the three upstream references;
  added constitution/current SDD links and the selected-feature continuation rule; clarified
  OP00/regional ownership, OP04/common, selected-stack execution, canonical MCCP handoff and
  catalog consumer gate, project NSG ownership, private publication, and genuine provenance.
  Preserved the upstream/helper maintenance rules and protected execution boundaries.
- Verification prerequisites now require Python 3.10+/Jsonnet 0.20+ and explain using a
  compatible installed interpreter when `python3` is older. Publication retains the full
  unit/model/Studio/catalog/facade/docs/whitespace gate. A documentation correction records
  its actual checks and keeps historical runtime evidence distinct.
- T015: Reviewed the complete `AGENTS.md` diff; no obligation conflicts with the constitution
  or owning docs. `python3.11 scripts/check_docs.py` passed for **45 Markdown files**;
  `git diff --check` and direct local-link/whitespace checks passed. The amended specification
  has **16 FR, 7 SC and 12 acceptance scenarios**, with one Edge Cases section and traceable
  contributor-guide tasks. The existing runtime, tests, workflows and upstream pins remain
  unchanged; this extension did not rerun runtime checks or execute any cloud operation.

| New item | Current evidence | Result |
| --- | --- | --- |
| FR-016 | T014/T015; updated contributor guide and governing/operational contract review | PASS documentation review |
| US4/AC1 | Purpose, governance/SDD links, ownership, handoff, tool and evidence boundaries in AGENTS.md | PASS documentation review |
| SC-007 | Full guide diff review, 45-file link/fence check, whitespace and existing local targets | PASS |

This extension introduces no runtime gap or constitutional exception. Real-installation
acceptance remains pending as recorded above.

## Publication preparation — 2026-10-06

The owner authorized committing and publishing to `main`, with local material excluded.
Fresh publication checks, separate from the earlier evidence, passed:

- `python3.11 -m unittest discover -s tests -v`: **47 tests in 182.033 seconds**, all passing.
- Model generation into the ignored `generated/publication-model-001` directory:
  **11 stacks, 13 phases, 4 seeds and 431 owned keys**; catalog validation passed and
  the pinned upstream family contract accepted **17 documents**.
- Studio fixture import into the ignored `generated/publication-studio-001` directory:
  **5 stacks, 6 phases, 1 seed and 200 owned keys**; catalog validation passed and
  the pinned upstream family contract accepted **7 documents**.
- Documentation links/fences, staged whitespace, and syntax of the six installed
  Spec Kit Bash scripts passed before committing.

The publication includes reusable Spec Kit scripts/templates, the constitution,
contributor guidance and feature artifacts. Installed local skills, installation/refresh
metadata, the feature selector, generated outputs, workdirs, logs and synthetic runtime
handoffs are excluded. The constitution's temporary synchronization report was removed.
This preparation performs no OCI deployment or installed MCCP acceptance; those checks
remain pending above. GitHub publication and its required CI result are recorded by the
resulting commit and pull request, independently of these local acceptance checks.
