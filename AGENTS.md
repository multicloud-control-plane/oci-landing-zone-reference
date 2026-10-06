# Reference implementation contributor contract

This is the customer-agnostic reference implementation for the Operations
Advisory Landing Zone repository design. Work in branches and review changes.

- Resource semantics come from the pinned Operating Entities libraries.
- Accepted configuration/dependency families come from the pinned Orchestrator.
- Keep OP00 IAM/global resources non-regional and regional operations independent.
- Keep one resource/state owner. Hub bootstrap/final update the same state.
- Keep platform/environment observability in the owning operation.
- Separate reference source/tests from customer configuration and runtime outputs.
- Do not commit credentials, OCIDs from real installations, states, plans or
  handoffs. Examples and test OCIDs must remain synthetic.
- Never run OCI deployment, Terraform apply, ORM jobs or state migration as part
  of repository development unless explicitly requested for a test installation.
- Public CI is credential-free. Privileged deployment jobs belong in a private,
  protected customer installation with separate identities and approval gates.
- Update docs/tests with adapter, operation or runtime contract changes.
- Verify `python3 -m unittest discover -s tests -v`, generation, catalog validation,
  upstream family contract and documentation links before publishing.

The authoring tool used to prepare a change does not run in the deployment path.
