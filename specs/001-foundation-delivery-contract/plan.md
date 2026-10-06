# Implementation Plan: Foundation Delivery Contract

**Branch**: `codex/constitution-principles` | **Date**: 2026-10-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-foundation-delivery-contract/spec.md`.

## Summary

Formalize and verify the existing Operating Entities/Studio -> OP00–OP04 multi-stack
foundation -> MCCP handoff contract. Reuse the generator, adapters, runtime preparation,
consumer gate, and owning operation guides. The planned implementation is requirement
traceability and fresh offline acceptance evidence, with no new runtime mechanism.
Observed source defects would need a scoped plan/spec amendment before a repair;
installation-only gaps remain explicit external acceptance, not fabricated local completion.

## Technical Context

**Language/Version**: Existing Python 3.10+ standard-library CLIs and Jsonnet 0.20+.

**Primary Dependencies**: Immutable OE, Orchestrator, Repository Design, and MCCP pins
from [upstream.lock.json](../../upstream.lock.json); Git and Jsonnet for local generation.

**Storage**: Public Markdown specification/evidence; ignored generated revisions, caches,
prepared directories, synthetic outputs, and runtime workdirs. Customer states remain private.

**Testing**: Existing `unittest` suite; catalog validator; facade family checker; documentation
link/fence checker; focused synthetic smoke checks of all preparation phases, runtime
provider/backend staging, and production/non-production handoff consumer acceptance.

**Target Platform**: Credential-free local macOS/Linux; existing public Ubuntu CI. Actual
execution is customer-controlled Terraform CLI or ORM behind review and protected identities.

**Project Type**: Existing CLI/reference projection with optional private workflow templates.

**Performance Goals**: Deterministic resource/configuration results and complete reference
phase coverage. No new throughput target is needed for this authoring/evidence change.

**Constraints**: No OCI or Terraform execution, no live installation changes, no real customer
inputs, no new HCL/resources/renderers or deployment-path dependency on Spec Kit. Keep
historical SDD documents and pre-existing `.gitignore` changes intact.

**Scale/Scope**: Reference two-region model: expected 11 stacks, 13 configuration phases,
4 project NSG seeds, 431 owned keys. Studio fixture: expected 5 stacks; count phases/seeds
and owned keys during verification. Counts describe fixtures, not customer deployment limits.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / boundary | Planned compliance | Pre-research | Post-design |
| --- | --- | --- | --- |
| I. Operating Entities Generation | Use pinned libraries and current Studio snapshot checks; no generator replacement | PASS | PASS |
| II. Operations-Based Multi-Stack Deployment | Verify catalog ownership, regional dependencies, same hub state, OP04/common, selected-stack staging | PASS | PASS |
| III. MCCP Handoff and Project Independence | Use canonical renderer/gate; verify routing, INFRA NSGs and truthful fixture provenance | PASS | PASS |
| IV. Minimal Local Automation | Call existing helpers; add authoring/evidence documents only | PASS | PASS |
| V. Evidence-Based Verification | Requirements, scenarios and task results link to current checks; live checks remain pending | PASS | PASS |
| Private execution/data boundaries | Ignored synthetic artifacts; no cloud execution or source-controlled runtime data | PASS | PASS |
| Documentation/review | Owning guides retained; spec quality and artifact analysis precede evidence execution | PASS | PASS |

No constitutional exceptions are proposed. Extension hooks are absent.

## Project Structure

### Documentation (this feature)

```text
specs/001-foundation-delivery-contract/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── delivery.md
├── checklists/
│   └── requirements.md
├── tasks.md
└── acceptance.md         # Created and filled by implementation tasks
```

### Source Code (repository root)

```text
gen/                     # Existing pinned OE projection and MCCP TBAC integration
scripts/
  reference.py           # Generation, catalog checks, dependency prep, handoff CLI/gate
  studio.py              # Verified supported exports and provenance
  runtime.py             # Complete pinned CLI workdir and regional backend staging
  onboard.py             # Canonical/imported project synchronization
  mccp.py                # Pinned handoff adapter and catalog consumer gate
  check_contract.py      # Pinned facade top-level family check
  check_docs.py          # Local Markdown links/fences and lock syntax
examples/two-region.jsonnet
tests/                   # Existing 47 test cases plus synthetic fixtures
docs/                    # Existing source setup, execution, publication, validation guides
```

**Structure Decision**: Keep application source and deployment workflow templates unchanged.
Author Spec Kit artifacts under the selected feature directory and use their links to the
existing guides as the operating instructions. `.specify/feature.json` selects this feature;
its directory name is independent of the current Git branch.

## Complexity Tracking

No additional runtime components, dependencies, or constitutional violations. The design
artifacts describe current entities and interfaces rather than introducing another schema.

## Follow-up: Contributor Contract Alignment — 2026-10-06

The owner requested review, correction, and update of `AGENTS.md`. Extend this feature's
specification with US4, FR-016, and SC-007 before changing the guide. Keep the existing
runtime contracts and historical acceptance records intact.

1. Align the guide with the constitution and explicit OE/Studio -> operations/multi-stack
   deployment -> MCCP handoff purpose. Link current SDD artifacts and preserve legacy specs.
2. Clarify OP00/global versus regional state ownership, OP04/common, the selected catalog
   consumer gate, private publication, existing helpers, and compatible tool prerequisites.
3. Review the resulting diff against owning docs; run documentation links/fences and
   whitespace checks. Record this documentation-only evidence separately from the preceding
   runtime verification. No runtime test rerun is needed for this guide change.

Constitution check: all five principles remain satisfied; no governance amendment or
runtime/deployment change is required. T014–T015 track implementation and acceptance.
