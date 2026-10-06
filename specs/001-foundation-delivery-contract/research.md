# Research: Foundation Delivery Contract

## Decision: Reuse the existing upstream generation and projection

**Rationale**: `gen/project.libsonnet` imports OE's generator; `reference.py` verifies immutable
clean checkouts and assigns operation catalog boundaries. `studio.py` checks complete exported
snapshots, supported scope, original sources, and normalized regeneration. The requested
mission is already represented by these contracts.

**Alternatives considered**: Another generator or duplicated resource HCL would contradict
Constitution I/IV and add maintenance without an observed need.

**Evidence**: [Generation](../../docs/generation-and-dependencies.md),
[Studio import](../../docs/studio-import.md), [upstream provenance](../../docs/upstream.md),
[projection](../../gen/project.libsonnet), [reference helper](../../scripts/reference.py).

## Decision: Verify operation boundaries and runtime staging without deploying

**Rationale**: The catalog owns regional state/output keys and selected stack dependencies.
Hub phases share a state; OP04 targets common. `prepare` resolves one stage and `runtime.py`
stages the complete pinned Orchestrator with provider aliases and a catalog-derived backend.
These functions execute neither Terraform nor OCI.

**Alternatives considered**: An automatic multi-stack deployment controller or hand staging
would duplicate existing preparation and exceed this feature's offline scope.

**Evidence**: [Runtime helper](../../scripts/runtime.py),
[CLI guide](../../docs/terraform-cli.md), [ORM guide](../../docs/resource-manager.md),
[operation tests](../../tests/test_reference.py).

## Decision: Reuse canonical MCCP handoff and the selected catalog consumer gate

**Rationale**: `mccp.py` uses the pinned upstream TBAC adapter and schema-3 machine/Markdown
renderer, with separate INFRA NSG binding and real catalog state provenance. `onboard.py`
synchronizes imported/canonical declarations. An installed older gate can assume different
state keys, so command mapping and genuine deployment/run evidence are installation gates.

**Alternatives considered**: Rewriting schema/Markdown or pretending OP04 has an independent
IAM state would break the consumer contract and duplicate ownership.

**Evidence**: [MCCP flow](../../docs/studio-mccp-flow.md),
[onboarding guide](../../docs/project-onboarding.md), [adapter](../../scripts/mccp.py),
[MCCP tests](../../tests/test_mccp.py).

## Decision: Record current offline evidence and pending live acceptance separately

**Rationale**: Existing CI runs 47 tests plus model/Studio generation, catalog/family validation,
and docs checks. Runtime staging has prior manual evidence but is not directly exercised by
that suite; fresh scoped staging and both environment handoffs will close this evidence gap.
Existing SDD evidence remains historical. Current tests do not prove deployed permissions,
traffic isolation, backend locking, protected-run authenticity, installation mapping, or
actual project Day 1/Day 2 execution.

**Alternatives considered**: Treating generated outputs as a deployed foundation would make
unsupported acceptance claims. Expanding the public CI or adding a new test framework is
not justified by a documentation/evidence baseline.

**Evidence**: [Public CI](../../.github/workflows/reference-ci.yml),
[validation scope](../../docs/validation.md),
[prior acceptance](../../docs/superpowers/plans/2026-10-06-balanced-onboarding.md).

Two read-only research agents inspected implementation contracts and acceptance coverage;
no unresolved design choice or missing runtime feature was found. All technical-context
questions are resolved by the pinned code and owning guides. No extension hooks are registered.
