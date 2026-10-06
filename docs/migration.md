# Adoption from an existing state

[Back to README](../README.md)

This procedure requires a complete test before customer migration. It has not
been executed against real state by offline CI. The inspected upstream adoption
guide also documents that validation boundary.

1. Inventory OCID, full address, current/target state, operation/owner,
   environment/region, effective tags and dependencies. One owner per resource.
2. Agree operation/IAM/monitoring boundaries. Preserve topology and customer
   keys; synthetic reference keys do not justify renaming existing resources.
3. Trial a low-risk non-prod operation using customer versions and entrypoint.
   Keep upgrades, IAM consolidation and runtime changes in separate windows.
4. Freeze both configurations/states, confirm no drift, and back up privately.
   Prepare complete residual/target configs. Never apply reduced config against
   the complete original state.
5. Use `terraform state mv` between local copies with exact address mapping.
   Facade/root changes require prefix mapping. If importing is necessary,
   import into the target before removing from the original.
6. Plan both states with refresh. Stop unexpected infrastructure destroy,
   replace or update. Preserve routing matches, attachment IDs and monitoring.
7. Under the same freeze, load coherent configs/states through ORM Import state
   or approved backend process, verify both plans and ownership.
8. Test connectivity/isolation/monitoring, unfreeze, and repeat one operation
   per window. Keep shared hub residual; critical platforms follow the pilot.

Rollback restores both states/configs coherently. A partial restore creates
double ownership. Test recovery before production. Injected attachments have
different tag inheritance from DRG-owned attachments; compare effective values.
Compartment-depth changes need explicit address mapping. Keep state/plan files
out of public Git and PKM.

## Earlier reference to MCCP contracts

Regenerate with catalog version 2; the schema-3 handoff requires separate
APP/DB/INFRA targets. Retain project root OCIDs. Inventory memberships before
replacing the earlier per-project admin groups/policies with the four TBAC
groups and generic policies; review access continuity separately.

Imported project NSGs previously managed by OP02 now belong to project GitOps.
Transfer ownership under a coordinated freeze before deploying their seed.
The seed targets INFRA rather than the earlier project root compartment:
state transfer alone does not move an OCI resource. Verify the supported
compartment-change behavior and both plans in test; stop unexpected replacement.
Changing resource placement and transferring state are separate decisions.
Keep keys and rules intact; never apply the reduced OP02 config while it still
owns those NSGs in state. Existing project manifests remain the editable source
after the initial handoff and must not be overwritten by regenerated seeds.
