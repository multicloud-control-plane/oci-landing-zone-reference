# Validation and scope

[Back to README](../README.md)

Offline tests cover generation, ownership, global/regional separation,
state/output uniqueness, same-region dependencies, conflict rejection, binding
and handoff constraints. A separate check verifies generated top-level families
against the pinned facade. This does not validate every resource schema in OCI.

## Initial supported scope

- Realm oc1, one LZ environment, multiple regions with one global hierarchy.
- One-OE Hub B, consolidated IAM, root CIS1 Security Zone and Cloud Guard.
- Regional scanning and operation-owned logs/topics/alarms/events.
- Hub bootstrap/final share state; public example LB and guessed Bastion SSH
  source are removed. Real bastion/ingress are reviewed extensions.
- Platform network/observability footprints; database/compute/OKE services
  require explicit service extensions.
- Extra Security Zones require NSG lifecycle tests before adoption.
- Audit Service Connectors are excluded because the module embeds regional IAM
  policy creation. Add them with an explicit governed IAM contract and test.

This baseline is not a complete CIS certification. Terraform validate/plan/apply,
traffic isolation and migration/rollback remain pending in an OCI test tenancy.

## Real-installation acceptance

- [ ] Review/check gates and executor permissions enforced.
- [ ] Terraform/provider locks and regional backend locking verified.
- [ ] One home-region global apply; regional states in their own regions.
- [ ] Hub bootstrap, environments/platforms and hub final successfully deployed.
- [ ] Real firewall binding, policy and prod/dev traffic isolation tested.
- [ ] Operation-specific scanning/logs/topics/alarms/events verified.
- [ ] Regional execution works with a local replica of global outputs.
- [ ] OP04 and project NSG create/update/delete/retirement verified.
- [ ] No-change plans and effective tags reviewed.
- [ ] State migration and coherent rollback pass in test.

Record real OCI evidence separately. Offline CI does not certify quotas,
service availability, effective IAM or customer topology.
