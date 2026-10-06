# Reference implementation design

This implementation follows the Operations Advisory repository design at commit
`79e718aa0c70c4a794fb43a7a21a58820a37bb73`.

## Scope and acceptance

Implement OP.00 global Landing Zone, OP.01 shared Landing Zone environment,
OP.02 workload environments, OP.03 shared/environment platforms and OP.04
project onboarding. Every execution has one owner, configuration set, state
and review boundary. Regional executions and their state buckets live in the
managed region. Consolidated IAM stays in the home region. Project onboarding
updates the consolidated IAM configuration and publishes a handoff; it does
not create a second owner for those IAM resources.

The initial reference uses one shared Landing Zone environment with a firewalled
Hub B in two commercial OCI regions, prod/dev workload environments, a shared
ops platform and a prod data platform. Platform examples implement their
network and observability footprint; service-specific database/compute
deployments are separate platform extensions. Example values are synthetic.
This is a tailored state projection of the official One-OE generator, not a
replacement blueprint product or a claim of a complete CIS certification.

## Components

- Pinned upstream lock: Operating Entities supplies resources; Orchestrator
  interprets configurations. Immutable commits are verified before use.
- Jsonnet projection: global IAM/governance/Cloud Guard/home events once;
  regional hub, environment and platform networking/scanning/observability in
  their owning stacks. Flow logs and platform alarms remain enabled as modeled.
- Staged networking: hub bootstrap preserves its own DRG attachment and excludes
  statements referencing attachments not yet created; spokes/platforms own their
  attachments; hub completion restores exact attachment-ID statements. Both
  phases update the same hub state. No broad attachment-type rule is substituted.
- Dependency preparation: explicit recursive merge of producer outputs rejects
  conflicts; regional resources can consume only same-region producers.
  Cross-stack DRG route-table references resolve to OCIDs before execution.
- Runtime preparation: complete JSON configuration/dependency sets produce
  rms-facade inputs for local file mode or private Object Storage mode. Operators
  execute the pinned upstream root with ORM or their own controlled Terraform
  CLI workflow. Runtime data, state, plans and handoffs stay outside public Git.
- OP04 handoff: deterministic project boundary derived from reviewed global IAM
  and regional environment outputs. It includes no credentials and is validated
  against the declared environment/region/project. The pinned MCCP adapter
  supplies official TBAC roles and the schema-3 renderer. Separate project NSG
  seeds preserve rules, bind to INFRA and use the existing VCN. Consumer validation
  checks actual catalog state owners; no separate OP04 IAM state is invented.
- CI: credential-free generation and contract tests run on hosted runners.
  The public reference does not run privileged self-hosted jobs on pull requests.
  Customer deployment automation requires private installation and protected
  approval environments.

## Maintenance responsibilities

Retain automation where mistakes affect resource/state ownership or repeated
preparation. Keep simple installation and reviewed publication as operator steps;
add automation when operational repetition pays for its maintenance.

| Owner / mechanism | Responsibility | Reason |
| --- | --- | --- |
| Pinned OE, Orchestrator and MCCP | Resource definitions, execution facade, TBAC and canonical handoff renderer | Reuse upstream semantics and contracts |
| Reference generation/preparation and Studio/schema-3 adapters | Ownership, region/dependency validation, verified Studio projection, bound handoff and project NSG seeds | Enforce operation boundaries and reject inconsistent inputs |
| Existing `runtime.py` (default CLI staging) | New complete pinned workdir, provider alias/Instance Principal overrides, catalog backend | Avoid relative-module, provider and state-key mistakes without duplicate manual HCL |
| Existing `onboard.py` (default OP04 model change) | Synchronize project declarations across the model and imported Studio configs | Avoid divergent copies or project loss at regeneration |
| Cloud Operations, manually | Private repository/runner/bucket/settings setup, saved-plan review, live verification, firewall discovery, producer and handoff/NSG publication | Bounded installation/review steps with explicit evidence |
| Optional protected private workflows | Selected-operation plan/apply and artifact-only handoff generation with real run provenance | Useful repeated orchestration while retaining operator approval/publication |

[Getting started](getting-started.md) owns source setup/promotion;
[private workflows](private-workflows.md) owns template variables/activation.
[Generation and dependencies](generation-and-dependencies.md),
[CLI](terraform-cli.md), [ORM](resource-manager.md) and
[project onboarding](project-onboarding.md) own execution/publication.
[MCCP installation](studio-mccp-flow.md) owns the selected installation's command
and consumer-gate mapping. Installing this reference changes no live installation.

## Security and verification boundaries

Cloud Operations owns IAM. Reviewer ownership is distinct from repository write
isolation. A central team can operate multiple stacks in one private repository;
independent writers require separate repositories and execution identities.
No Terraform, OCI deployment or migration is performed while building this
reference. Local tests prove deterministic projection, resource ownership,
region/state isolation, dependency preparation and handoff constraints. Real
Terraform plan/apply, firewall endpoint completion, traffic isolation and
rollback require a customer-controlled test tenancy.

Audit connectors whose source modules create nested IAM policies are excluded
from the initial projection and documented as an adoption decision: moving
those policies to the governed IAM operation requires an explicit module
contract and test. Security Zone recipes use the official root CIS1 target;
additional targets require NSG lifecycle validation.
