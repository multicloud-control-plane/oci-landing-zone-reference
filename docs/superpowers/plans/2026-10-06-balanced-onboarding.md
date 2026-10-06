# Balanced onboarding implementation plan

> Execute against the [specification](../specs/2026-10-06-balanced-onboarding.md); keep acceptance evidence tied to AC1–AC8.

## Global constraints

- No runtime code, dependencies, generated-resource changes or new test code.
- Preserve OP00/home region, regional state owners, hub bootstrap/final shared state, schema-3 handoff and project NSGs in INFRA.
- Existing helpers remain the default for repeated/error-prone preparation; private workflows are optional.
- Manual steps state operator, action, expected result and completion check. Real schema-3 workflow provenance is required.
- English reusable docs; examples synthetic; no OCI/Terraform execution.

## Task 1: Implement the guided journey

- [x] README and new docs/getting-started.md: tools/clone, demo-revision-001, expected output, separate private config checkout/source tree and reviewed revision-001; Studio export promotion and model alternative. AC1–AC2.
- [x] docs/generation-and-dependencies.md: common first, IDs/stages for all FRA example operations, bootstrap/final distinction, preparation example, output copy from prepared outputs to declared producer directories, actual bindings JSON and pinned firewall discovery guide. AC3–AC4.
- [x] docs/terraform-cli.md: use common in initial example; explain runner prerequisites/provider lock and existing runtime helper's purpose; move optional workflow variable/setup instructions to new docs/private-workflows.md. AC3/AC5/AC7.
- [x] docs/private-workflows.md: installation location/tree, all template variables with value examples, activation/private/main checks, single shared-path runner and regional selection boundary, saved-plan review, artifact-only handoff/provenance. AC5.
- [x] docs/project-onboarding.md and docs/studio-mccp-flow.md: keep existing helper synchronization, real source-run evidence and canonical renderer; explain manual reviewed handoff/NSG publication and installation-specific consumer-command selection. AC6.
- [x] AGENTS.md, docs/design.md and .gitignore: maintenance matrix/manual-vs-helper rationale and private-outputs exclusion. Route docs without duplicated setup. AC7–AC8.
- [x] Implementer runs docs checks/whitespace and reports exact changed files; commit only owned documentation/ignore changes.

## Task 2: Verify against acceptance and review

- [x] Execute fresh local quickstart with Python 3.10+/Jsonnet 0.20+; validate and facade-check generated demo. AC1.
- [x] Prepare common without any fabricated dependency; prepare all phases with synthetic official output fixtures and verified synthetic private-IP bindings, explicitly labeled offline evidence. AC3–AC4.
- [x] Compare workflow vars against docs, validate shell syntax and local Markdown links/fences. AC5.
- [ ] Verify no runtime source changes, run the existing 47 tests and record remote CI. AC8.
- [ ] Independent task review for spec compliance and documentation quality; fix concrete findings through the implementer. Final whole-branch review covers accepted user judgment/boundaries.

## Task 3: Deliver

- Publish PR with spec/plan/evidence, merge through existing CI gate and verify main.
- Update the owning PKM project with delivery and keep real OCI acceptance pending; SR links delivery without duplicating the guide.

Integration status and remote CI are recorded by
[PR #2](https://github.com/multicloud-control-plane/oci-landing-zone-reference/pull/2),
so this committed plan does not need a post-merge edit to claim its own delivery.

## Acceptance evidence — 2026-10-06

SDD here means **Spec-Driven Development**. Specification and plan were committed
in `71d0fdb` before implementation in `f8a29de`. Acceptance is evaluated against
AC1–AC8, rather than treating documentation syntax as proof of deployment.

| Criteria | Recorded local evidence |
| --- | --- |
| AC1–AC2 | Fresh clone, Python 3.11.15 and Jsonnet 0.22.0: demo and separate private-model generation each produced 11 stacks, 13 configurations, 4 seeds and 431 keys; validation and facade contract passed for 17 documents. Studio promotion instructions are reviewed separately from this model execution. |
| AC3–AC4 | Common prepared before any dependency outputs existed. All 13 configuration phases prepared using synthetic deployed-output fixtures and regional private-IP bindings; no unresolved output/binding references. Runtime staged common/FRA and dev/AMS with catalog state keys and provider regions. This is offline evidence. |
| AC5 | Both unchanged workflow templates compared with documentation: all 13 distinct variables present; 21 Bash fences passed syntax checks and one JSON example parsed. Required private/main/readiness, runner/path, saved-plan review and regional selection constraints are documented. |
| AC6–AC7 | Independent task review confirmed schema-3 provenance, actual state owners, INFRA project NSGs, publication and balanced helper/manual responsibilities. Its provider-lock setup finding was fixed in `ce4219a` and the scoped re-review found no new breakage. Final branch review and CI outcomes are recorded in the integration PR. |
| AC8 | Existing suite: 47 tests passed in 106.652 seconds. Runtime, generator, tests, upstream lock and workflow templates unchanged from main `c31d540`. Documentation links/fences and whitespace checks passed. Remote `reference-contract` remains the merge gate. |

No OCI calls, Terraform validate/plan/apply, customer state migration or live MCCP
installation changes were executed. Test-tenancy acceptance remains governed by
[Validation and scope](../../validation.md#real-installation-acceptance).

## Continue in a new session

1. Read the root [contributor contract](../../../AGENTS.md), this specification
   and plan, then the PR's final acceptance/merge record. Use the latest `main`;
   confirm PR #2 is merged before assuming this delivery is integrated.
2. The implementation already includes Studio import, operation/state projection
   and the MCCP schema-3/INFRA NSG adaptation (PR #1). This change guides adoption
   and preserves those contracts; do not reopen resolved ownership choices.
3. After integration, the remaining acceptance work is the
   [real-installation checklist](../../validation.md#real-installation-acceptance).
   Start by obtaining a test tenancy, approved home/managed regions and CIDRs,
   private source repository, scoped runners/state buckets, a real supported
   Studio export and a test MCCP installation. Deployment needs its own explicit
   authorization; this session executed no cloud operation.
4. The existing MCCP installation has not been changed. Before enabling its
   handoff workflow, select this reference's catalog-based consumer gate/commands
   as described in [MCCP installation](../../studio-mccp-flow.md). Its MVP runner
   scope is per environment; do not infer per-project runner isolation.
5. Keep the agreed maintenance rule: upstream resource definitions/rendering,
   useful existing helpers, optional workflows and simple documented operator
   steps. Record new evidence against a spec and plan; keep real customer inputs,
   states, plans and outputs private.
