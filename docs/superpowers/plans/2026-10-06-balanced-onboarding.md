# Balanced onboarding implementation plan

> Execute against the [specification](../specs/2026-10-06-balanced-onboarding.md); keep acceptance evidence tied to AC1–AC8.

## Global constraints

- No runtime code, dependencies, generated-resource changes or new test code.
- Preserve OP00/home region, regional state owners, hub bootstrap/final shared state, schema-3 handoff and project NSGs in INFRA.
- Existing helpers remain the default for repeated/error-prone preparation; private workflows are optional.
- Manual steps state operator, action, expected result and completion check. Real schema-3 workflow provenance is required.
- English reusable docs; examples synthetic; no OCI/Terraform execution.

## Task 1: Implement the guided journey

- [ ] README and new docs/getting-started.md: tools/clone, demo-revision-001, expected output, separate private config checkout/source tree and reviewed revision-001; Studio export promotion and model alternative. AC1–AC2.
- [ ] docs/generation-and-dependencies.md: common first, IDs/stages for all FRA example operations, bootstrap/final distinction, preparation example, output copy from prepared outputs to declared producer directories, actual bindings JSON and pinned firewall discovery guide. AC3–AC4.
- [ ] docs/terraform-cli.md: use common in initial example; explain runner prerequisites/provider lock and existing runtime helper's purpose; move optional workflow variable/setup instructions to new docs/private-workflows.md. AC3/AC5/AC7.
- [ ] docs/private-workflows.md: installation location/tree, all template variables with value examples, activation/private/main checks, single shared-path runner and regional selection boundary, saved-plan review, artifact-only handoff/provenance. AC5.
- [ ] docs/project-onboarding.md and docs/studio-mccp-flow.md: keep existing helper synchronization, real source-run evidence and canonical renderer; explain manual reviewed handoff/NSG publication and installation-specific consumer-command selection. AC6.
- [ ] AGENTS.md, docs/design.md and .gitignore: maintenance matrix/manual-vs-helper rationale and private-outputs exclusion. Route docs without duplicated setup. AC7–AC8.
- [ ] Implementer runs docs checks/whitespace and reports exact changed files; commit only owned documentation/ignore changes.

## Task 2: Verify against acceptance and review

- [ ] Execute fresh local quickstart with Python 3.10+/Jsonnet 0.20+; validate and facade-check generated demo. AC1.
- [ ] Prepare common without any fabricated dependency; prepare all phases with synthetic official output fixtures and verified synthetic private-IP bindings, explicitly labeled offline evidence. AC3–AC4.
- [ ] Compare workflow vars against docs, validate shell syntax and local Markdown links/fences. AC5.
- [ ] Verify no runtime source changes, run the existing 47 tests and record remote CI. AC8.
- [ ] Independent task review for spec compliance and documentation quality; fix concrete findings through the implementer. Final whole-branch review covers accepted user judgment/boundaries.

## Task 3: Deliver

- [ ] Publish PR with spec/plan/evidence, merge through existing CI gate and verify main.
- [ ] Update the owning PKM project with delivery and keep real OCI acceptance pending; SR links delivery without duplicating the guide.
