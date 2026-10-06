# Feature Specification: Foundation Delivery Contract

**Feature Branch**: `codex/constitution-principles`

**Created**: 2026-10-06

**Status**: Verified offline; real-installation acceptance pending

**Input**: User description: "Formalize and assess Operating Entities/Studio generation,
operations-based multi-stack foundation deployment, and the handoff to MCCP. Reuse the
existing implementation and SDD documents, complete justified gaps, and record evidence."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate and review a supported foundation design (Priority: P1)

Cloud Operations uses Operating Entities or a supported Studio export to produce a
reviewable foundation revision. The revision retains the supported network design,
identifies each resource owner, and can be regenerated from its approved source.

**Why this priority**: All deployment and handoff decisions depend on trustworthy design
and ownership evidence.

**Independent Test**: Generate the reference design and import a synthetic Studio export;
compare regenerated resources, ownership, source evidence, and preserved network choices.

**Acceptance Scenarios**:

1. **Given** an approved supported design, **When** a new foundation revision is generated,
   **Then** its ownership and upstream compatibility pass validation and repeating the same
   source produces identical resource configurations.
2. **Given** a supported Studio export, **When** it is imported, **Then** supported network
   choices are preserved, original source evidence is retained, and projection adjustments
   are reported for review before source promotion.
3. **Given** an unsupported or modified Studio export, **When** import is attempted,
   **Then** the input is rejected with a reason before a usable revision is published.

### User Story 2 - Prepare and operate independent foundation stacks (Priority: P1)

Cloud Operations prepares a selected foundation operation with a known owner, region,
state, and dependencies. A reviewed deployment can target that stack through an approved
runtime while unrelated regions and environments retain their own states.

**Why this priority**: Independent operation boundaries are the project's deployment model
and protect production, regional recovery, and IAM governance.

**Independent Test**: Inspect the operation catalog and prepare every reference phase
with synthetic producer outputs; verify selected state and region without deploying.

**Acceptance Scenarios**:

1. **Given** the reference revision, **When** operation ownership is inspected,
   **Then** global IAM has one owner, regional resources have independent states,
   hub bootstrap and completion share their owning state, and OP04 reuses global IAM state.
2. **Given** a selected operation and compatible producer outputs, **When** it is prepared,
   **Then** only that operation's inputs are prepared, required references are resolved,
   and the runtime retains its assigned state and managed region.
3. **Given** conflicting or missing producer outputs, cross-region bindings, or duplicate
   owners, **When** preparation or validation is attempted, **Then** execution is blocked.
4. **Given** an installation ready for deployment, **When** the documented operator path
   is followed, **Then** the selected saved plan is reviewed, execution uses the approved
   identity, and live verification precedes output publication. This scenario requires
   separate real-installation acceptance; offline preparation is insufficient evidence.

### User Story 3 - Hand a deployed project boundary to MCCP (Priority: P1)

Cloud Operations onboards a project in the foundation and publishes the reviewed boundary
that MCCP consumes. Project Teams request Day 1 and Day 2 changes in separate production
and non-production repositories inside their assigned scope.

**Why this priority**: The foundation must become usable by project self-service with
clear ownership and without transferring foundation executor privileges.

**Independent Test**: Produce and validate a project package from synthetic deployed-output
fixtures; verify scope, repository routing, state provenance, and separate project NSG ownership.

**Acceptance Scenarios**:

1. **Given** a declared project and verified deployed outputs, **When** its handoff is
   rendered, **Then** MCCP receives consistent machine and human boundary information,
   assigned compartments and network, correct routing, and actual foundation state owners.
2. **Given** a package for the wrong source repository, state owner, environment, or region,
   **When** the selected foundation's consumer gate runs, **Then** it rejects the package.
3. **Given** onboarding or retirement, **When** the canonical source is updated,
   **Then** imported source declarations stay synchronized, regional foundation resources
   remain unchanged, and project NSGs remain owned by the project rather than the foundation.
4. **Given** a selected MCCP installation, **When** its approved command mapping and
   consumer gate are installed and the reviewed package is published, **Then** the project
   can request supported Day 1 and Day 2 changes inside its boundary. This scenario requires
   installation evidence and is not satisfied by local fixture validation.

### User Story 4 - Follow the current contributor contract (Priority: P2)

A contributor reads `AGENTS.md` and can identify the project's delivery purpose,
governing principles, current SDD process, operation ownership, verification prerequisites,
and the distinction between offline evidence and real-installation acceptance.

**Why this priority**: Consistent contributor instructions preserve the delivery contracts
when work continues across sessions.

**Independent Test**: Review the contributor guide against the constitution, this
specification, and the owning operation guides; validate all repository-local links.

**Acceptance Scenarios**:

1. **Given** a contributor starting or continuing work, **When** they read the guide,
   **Then** it links the governing and SDD documents, explains generation/deployment/MCCP
   responsibilities, states the existing ownership and execution boundaries, and identifies
   compatible tools and required publication checks without implying live acceptance.

### Edge Cases

- Studio archives with missing, duplicated, modified, or unsafe entries are rejected.
- Unsupported hub/security/service choices are rejected rather than silently converted.
- A second resource/state owner, regional IAM, conflicting producers, or a wrong-region
  resource reference blocks validation or preparation.
- Hub completion requires explicit producer attachment and firewall binding evidence.
- An undeclared project, mismatched network, inconsistent handoff, or obsolete consumer
  state assumptions block package acceptance.
- Regeneration after onboarding must retain projects added since the original Studio export.
- Existing resources require a reviewed migration before changing their state owner.
- Synthetic outputs or workflow provenance must never be presented as live deployment evidence.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Foundation generation MUST use Operating Entities as the authoritative
  resource generator, through supported Studio exports or the approved canonical model.
- **FR-002**: Studio import MUST preserve supported source choices, retain source evidence,
  report projection adjustments, and reject unsupported or inconsistent exports.
- **FR-003**: The approved canonical source MUST reproduce its resource configurations;
  onboarding and retirement MUST synchronize canonical and imported project declarations.
- **FR-004**: The foundation MUST expose repeatable OP00–OP04 operation boundaries with
  explicit owners, configurations, state assignments, regions, and producer dependencies.
- **FR-005**: Each resource MUST have one state owner; global IAM MUST remain in OP00,
  hub phases MUST share one state, and OP04 MUST reuse OP00 without a handoff state.
- **FR-006**: Regional states MUST reside in the managed region; validation MUST reject
  cross-region resource dependencies, conflicting producers, and duplicate ownership.
- **FR-007**: Operators MUST be able to prepare one selected stack for either approved
  runtime while preserving its catalog state and region, without cascading deployment.
- **FR-008**: The operator path MUST require saved-plan review, an approved execution
  identity, live verification, and reviewed producer publication before consumer use.
- **FR-009**: Documentation MUST identify source setup, operation execution, optional
  workflow installation, and publication responsibilities using the existing helpers.
- **FR-010**: The project MUST produce the established MCCP machine and human handoff
  describing project compartments, assigned network, environment, region, repository
  routing, real state owners, and genuine protected workflow provenance.
- **FR-011**: The selected foundation consumer gate MUST reject a package inconsistent
  with its project boundary, source repository, catalog ownership, or human information.
- **FR-012**: Project NSGs MUST have separate project-owned seeds bound to project
  infrastructure scope and MUST be excluded from foundation-owned configurations.
- **FR-013**: The handoff MUST support separate production and non-production project
  repositories and states; project requests MUST retain the foundation privilege boundary.
- **FR-014**: Acceptance evidence MUST map requirements and scenarios to existing checks
  and distinguish current offline evidence from pending real-installation acceptance.
- **FR-015**: Reference examples and checks MUST remain synthetic and credential-free;
  customer configuration, credentials, real identifiers, states, plans, and runtime
  handoffs MUST remain outside public source control.
- **FR-016**: The contributor guide MUST reflect the governing constitution, delivery
  purpose, current SDD workflow, operation/state/handoff contracts, private execution/data
  boundaries, existing helper responsibilities, and compatible verification prerequisites.

### Key Entities *(include if feature involves data)*

- **Approved design**: Supported source choices, upstream revision, imported evidence,
  canonical project declarations, and the review approving their use.
- **Foundation revision**: Reproducible operation configurations and project seeds with
  source provenance and a catalog assigning ownership, regions, states, and dependencies.
- **Operation instance**: A repeatable scoped change against an owning stack, including
  preparation stage, execution owner, review boundary, and assigned state.
- **Producer publication**: Verified applied resource information used by dependent stacks
  or project handoffs, tied to the owning foundation revision and installation.
- **Project handoff**: The reviewed project boundary and evidence consumed by MCCP, with
  machine and human information and separate project-owned resource seeds.
- **Acceptance record**: Requirement-to-evidence mapping recording check results and
  remaining installation acceptance without treating synthetic data as deployed resources.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Repeating the approved reference source produces identical resource
  configurations and ownership; every supported imported network choice remains preserved.
- **SC-002**: Every reference operation phase can be prepared independently with a resolved
  dependency set, and every resource has exactly one owning state in the assigned region.
- **SC-003**: Every documented invalid-input acceptance case is rejected before execution
  or package acceptance, with a reason identifying the violated boundary.
- **SC-004**: Both production and non-production project packages carry consistent boundary
  information, correct repository routing, and the actual foundation state owners, while
  all project NSGs remain separately owned.
- **SC-005**: All functional requirements and acceptance scenarios have traceable evidence
  or an explicitly pending real-installation check; no offline result is labeled live acceptance.
- **SC-006**: An operator can follow the existing documentation from source selection
  through selected-stack execution and MCCP publication without a second generator,
  runtime preparation mechanism, or handoff renderer.
- **SC-007**: Contributor-guide review finds no conflicting obligation against the
  constitution or owning operation guides, and every local governance/SDD/documentation
  link resolves to its existing artifact.

## Assumptions

- This feature formalizes and assesses the implemented delivery contract. Existing SDD
  documents remain historical evidence and source material; they are not rewritten.
- The supported initial scope remains oc1, One-OE Hub B, consolidated IAM, one Landing
  Zone environment with multiple regions, root CIS1, and platform network/observability.
- Pinned Operating Entities, Orchestrator, Repository Design, and MCCP contracts remain
  the dependencies; broadening their supported scope is a separate feature.
- The current offline delivery records runnable verification and documented installation
  gates. OCI deployment, Terraform execution, migrations, live MCCP changes, and project
  publication require a separately authorized test installation and are outside this change.
- Cloud Operations controls foundation configuration and execution; independent project
  writers use the reviewed MCCP boundary and their own project repositories and states.
- Existing validation and preparation helpers remain the default. New runtime automation
  is justified only by an observed contract gap, not by adoption of Spec Kit.
