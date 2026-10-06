# Balanced onboarding and maintenance specification

## Intent

Apply the owner's preference for minimal custom code using engineering judgment:
automate repeated or error-prone work and document simple one-time setup and
publication steps. Improve the clean-checkout customer journey without changing
generated resources or introducing another deployment framework.

## Decisions

- Upstream OE, Orchestrator and MCCP own resource definitions, TBAC and rendering.
- Keep reference generation, ownership/region/dependency validation, Studio
  verification and schema-3 binding: these enforce the required operation model.
- Retain the existing runtime/onboarding helpers where they prevent state-key,
  provider-alias and imported-model synchronization mistakes. Use them in the
  default execution path; document their limited responsibilities.
- Install repositories, scoped executors, buckets and workflow settings manually.
  Review plans, verify live resources, discover firewall bindings and publish
  producer outputs/handoffs explicitly. Automate these only when operational
  repetition warrants it.
- Keep private workflows optional. A schema-3 handoff must retain real workflow
  provenance; use an existing protected job or the artifact-only handoff template
  for installations that need that evidence. Manual publication follows validation.
- No runtime code, dependencies, generated-resource changes or new test code.

## Acceptance criteria

| ID | Requirement | Evidence |
| --- | --- | --- |
| AC1 | A clean clone can check tool versions, generate a synthetic demo and validate it using consistent paths | Execute documented local commands; model yields 11 stacks, 13 configs, 4 seeds and 431 keys |
| AC2 | A new user can create/promote a private source model without confusing demo and deployment revisions | Explicit private repo tree and model/Studio promotion instructions |
| AC3 | First execution starts at common; every regional phase names its correct ID/stage and completion outputs | Prepare common locally; inspect sequence/catalog; synthetic deployed-output preparation for all phases |
| AC4 | Official output publication and real firewall bindings are documented as bounded operator steps | Concrete copy/inspection commands, binding JSON and pinned upstream discovery link |
| AC5 | Optional workflows document paths, all variables, activation flags and runner/approval prerequisites | Compare documented variable names with both workflow templates, including FOUNDATION_AUTOMATION_READY |
| AC6 | MCCP instructions preserve schema 3, actual state owners, real provenance, project NSGs in INFRA and reviewed publication | Document commands/gate and distinguish existing installation configuration from reference capability |
| AC7 | Maintenance rule justifies retained adapters/helpers and favors simple manual steps without requiring all-manual execution | AGENTS/design responsibility matrix and consistent customer guide wording |
| AC8 | Existing resource/state contracts stay unchanged | Runtime/generator/tests/workflows byte unchanged; required 47 tests/CI pass; documentation links/fences pass |

## Delivery boundary

Document local verification separately from test-tenancy acceptance. No Terraform
validate/plan/apply, OCI calls, customer state migration, live MCCP installation
change or project creation is part of this documentation delivery.
