# Reference implementation contributor contract

This is a customer-agnostic OCI foundation reference implementation. Its delivery
path is **Operating Entities/Studio generation -> reviewed operations-based
multi-stack deployment -> MCCP project handoff**:

- [Operating Entities / Landing Zone Studio](https://oci-landing-zones.github.io/oci-landing-zone-operating-entities/)
  supplies the blueprint generator and supported design exports.
- This project verifies and projects the generated design, then prepares and
  governs deployment through the pinned Orchestrator using Terraform CLI or
  Oracle Resource Manager, following the
  [Operations Advisory Repository Design](https://github.com/oracle-devrel/technology-engineering/tree/OperationsAdvisory-repository-design/oci-and-db/foundation/operations-advisory/multi-cloud-operating-models/landing-zone-repository-design).
- Cloud Operations publishes the reviewed project boundary consumed by
  [MCCP](https://github.com/oracle-devrel/technology-engineering/tree/main/oci-and-db/foundation/operations-advisory/multi-cloud-operating-models/multi-cloud-control-plane)
  for governed Project Team Day 1 and Day 2 requests.

Work in branches and review changes.

## Spec-Driven Development (SDD)

For meaningful changes, use SDD internally: define intent, contracts/boundaries
and acceptance criteria, plan the implementation, implement, and verify
acceptance evidence before publication. Match the detail to the change and
keep pending installation checks distinct from offline evidence.

Keep the constitution, specs, plans, tasks, research and working evidence local
and outside the public Git history. SDD and its authoring tools remain outside
the deployment path; they add no runtime framework or replacement generator,
renderer or executor.

## Operation and handoff boundaries

- Resource semantics come from the pinned Operating Entities libraries.
- Accepted configuration/dependency families come from the pinned Orchestrator.
- Verify Studio exports against the pinned generator, preserve supported source
  choices and source evidence, report projection adjustments, and reject unsupported
  designs explicitly. Keep upstream revisions in `upstream.lock.json`.
- Keep OP00 IAM/global resources non-regional and regional operations independent.
- Manage global resources from the home region. Keep each regional stack's state
  in its managed region; regional resource dependencies must remain same-region.
  Use reviewed local replicas of global outputs where regional execution needs them.
- Keep one resource/state owner. Hub bootstrap/final update the same state.
- Keep platform/environment observability in the owning operation.
- Execute one selected stack/stage with explicit dependencies and review boundaries;
  do not introduce cascading applies. Match repository and execution-identity
  boundaries to independent writers.
- OP04 updates IAM in the existing `common` state and publishes an artifact. It
  creates neither a separate OP04 IAM state nor a handoff Terraform state.
- Reuse MCCP's pinned TBAC and canonical schema-3 machine/Markdown renderer.
  Validate handoffs with the selected foundation's catalog-based consumer gate,
  actual state owners, assigned targets, repository routing and source provenance.
- Project Teams use separate production/non-production repositories and workload
  states inside their handoff. Keep project NSG seeds in project-owned INFRA and
  exclude them from foundation ownership; retain the foundation privilege boundary.
- Review migration and compatibility before changing ownership or consumer contracts
  for an existing installation. Follow `docs/migration.md`.

## Data and execution boundaries

- Separate reference source/tests from customer configuration and runtime outputs.
- Never commit credentials, Terraform states or saved plans. Keep customer
  configuration, real installation OCIDs and runtime outputs/handoffs outside
  this public reference. Examples and test OCIDs must remain synthetic. Publish
  approved project handoffs only through the reviewed private installation
  process in `docs/project-onboarding.md`.
- Never run OCI deployment, Terraform apply, ORM jobs or state migration as part
  of repository development unless explicitly requested for a test installation.
- Public CI is credential-free. Privileged deployment jobs belong in a private,
  protected customer installation with separate identities and approval gates.
- Verify deployed resources and permissions before producer or handoff publication.
  Handoffs retain genuine protected workflow provenance even when deployment and
  publication are manual. Installing a workflow template does not connect MCCP.
- Label generation/import/preparation/staging and synthetic consumer checks as
  offline evidence. Track live deployment, effective IAM, traffic, state locking,
  lifecycle and rollback acceptance in `docs/validation.md` separately.

## Maintenance and documentation

- Update docs/tests with adapter, operation or runtime contract changes.
- Favor minimal custom maintenance: manually install repositories, scoped runners,
  buckets/settings, review plans, verify live resources and publish outputs/handoffs.
- Keep existing helpers as defaults for repeated/error-prone work: `reference.py`
  generation/ownership/region/dependency checks, Studio verification and schema-3
  binding; `runtime.py` complete pinned workdir/provider aliases/catalog backend;
  `onboard.py` synchronization of canonical and imported Studio project declarations.
- Do not duplicate upstream HCL/resources, MCCP rendering or runtime staging.
  Add automation for simple operator steps only when repetition justifies its
  maintenance. Private workflows remain optional.
- Keep setup in `docs/getting-started.md`, workflow installation/variables in
  `docs/private-workflows.md`, execution/publication in their existing owning docs.
  See the responsibility matrix in `docs/design.md`.

## Verification

Check tools before running the local path: Python 3.10+ and Jsonnet 0.20+ are
required. If `python3` selects an older interpreter, use an installed compatible
one, such as `python3.11`, consistently and record its version in the evidence.

Before publishing, verify the full suite (`python3 -m unittest discover -s tests -v`
with the compatible interpreter), model and Studio generation, catalog validation,
pinned upstream family contracts, documentation links/fences
(`python3 scripts/check_docs.py`) and whitespace (`git diff --check`). Use fresh
empty revision/workdir paths and keep outputs ignored. Follow
[the validation guide](docs/validation.md) for offline and installation checks.

For a documentation-only correction, run the relevant link/fence/whitespace and
contract review checks. The full publication gate still applies before publishing;
record results from the checks actually run and keep earlier runtime evidence dated.
