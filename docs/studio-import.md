# Import from Landing Zone Studio

[Back to README](../README.md)

Studio is the visual authoring tool. The reference translates a supported
export into governed operation boundaries; Orchestrator/Terraform performs
deployment in the customer's private installation.

## Export and import

1. In Studio, choose Hub B, CIS1 and oc1; do not enable environment Security Zones
   or OKE/OCVS extensions for this initial adapter. Projects and plain custom
   platform networks are supported. Studio's default design may be outside this
   scope: import fails explicitly rather than changing those choices.
2. Download the deployment ZIP. Keep it in a private configuration repository.
3. Run import with explicit operating metadata:

```bash
python3 scripts/reference.py import-studio \
  --source customer/studio-fra.zip --source customer/studio-ams.zip \
  --home-region eu-frankfurt-1 --landing-zone-environment shared \
  --notification-email operations@example.com \
  --output generated/studio-revision-001
python3 scripts/reference.py validate --generated generated/studio-revision-001
python3 scripts/check_contract.py --generated generated/studio-revision-001
```

Replace the example email. One export represents one region. Supply the home
region export too; every region must describe the same global IAM hierarchy.
Regional addresses remain regional; review their connectivity and overlap
requirements. The initial ownership model uses Cloud Operations as the writer
with operation-specific reviewers and execution roles.

`--source path/config.jsonnet` also works. If its directory has JSON snapshots,
all must match the complete pinned generator set. A source without JSON is
regenerated and marked as source-only evidence. Only Studio's literal-object
Jsonnet is accepted: executable expressions and imports are rejected.

## Verification and outputs

ZIPs are read without extraction. Import rejects duplicate/unsafe entries,
archives over 32 MiB expanded/64 files, invalid data and unexpected artifacts.
Exported JSON is compared semantically with the locked OE generator. Drift or
a generator-version mismatch fails import; investigate and update the reviewed
lock/adapter rather than bypassing the comparison.

The normal catalog/configuration files are supplemented by:

| Output | Responsibility |
| --- | --- |
| `model.jsonnet` | Editable canonical model for subsequent reviewed Git changes; retains the original Studio config objects |
| `studio-source/<region>/` | Original source and exported JSON; evidence, not a second editable deployment source |
| `provenance.json` | Source/export hashes and pinned upstream revisions |
| `studio-import-report.md` | Preserved choices, snapshot checks and reference adjustments to review |

The adapter preserves VCN/subnet CIDRs and definitions, project NSGs and hub
network content. The reference changes state ownership: global IAM in common,
spoke-owned attachments, exact hub routing bindings and monitoring/scanning in
the owning operation. Platform networks move into platform compartments.
Notification subscriptions use the supplied email. Audit Service Connectors
remain excluded by the initial baseline because their module embeds regional
IAM. Review these changes; this is not a byte-for-byte deployment or a complete
CIS certification. Original LB/Bastion examples also need endpoint review.

## Deployment and subsequent changes

Use the normal [generation/dependency order](generation-and-dependencies.md)
and [private CLI](terraform-cli.md) or [Resource Manager](resource-manager.md)
flow. Hub bootstrap/final share state; private IP bindings and deployed output
files are still required. Import does not run Terraform or OCI.

The private workflow has a `configuration` choice:

- `studio`: put one ZIP per region under `config/studio/`; set `HOME_REGION`,
  `LANDING_ZONE_ENVIRONMENT` and `NOTIFICATION_EMAIL` in addition to the normal
  runtime variables. Each run verifies and imports those exports before planning
  the selected operation.
- `model`: promote the reviewed imported `model.jsonnet` to `config/model.jsonnet`
  and maintain it through Git after the initial import. Historical ZIPs remain
  evidence. The adapter's resource projection is retained during regeneration.

For later Studio edits, export/import a fresh revision and review the delta
against the canonical model before promotion. Do not overwrite later project
changes by blindly reimporting an older Studio snapshot.

The current importer places project NSGs in OP02; that is a compatibility gap
with MCCP's established project ownership in INFRA. Its handoff also requires
schema 3 and APP/DB/INFRA targets. These decisions are already made in the
existing MCCP foundation; this reference must reuse them. See
[the contract and adaptation gaps](studio-mccp-flow.md) before connecting project
self-service. [Project onboarding](project-onboarding.md) describes the current
reference behavior.

Offline tests validate import/projection/runtime-input contracts. OCI deployment,
effective IAM, traffic and migration acceptance remain pending in a test tenancy.
