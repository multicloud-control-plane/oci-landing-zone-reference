# Import from Landing Zone Studio

## Approved scope

Use Studio's exported `config.jsonnet` as the design source. Accept its ZIP or
the source file, verify accompanying generated JSON against the locked OE
generator, then project the supported design into OP00–OP04 configuration sets.
Keep original exports and hashes for review. Never deploy OCI during import.

## Compatibility boundary

Initial support is One-OE Hub B, CIS1, oc1, projects and plain custom platform
networks. Preserve explicit hub/environment/platform CIDRs, subnets and project
NSGs. Reject other hubs, CIS2, environment Security Zones, workload extensions,
unknown config fields and unsafe/duplicate archive entries. Reject source code
that is not Studio's literal-object Jsonnet. No silent conversion of choices.

Require home region, LZ environment and notification email. Multiple exports
may represent distinct regions; require a home-region export and a consistent
global IAM hierarchy. A source file without generated JSON is regenerated;
a ZIP must contain the complete corresponding generated set and no drift.

## Architecture

`reference.py import-studio` delegates input checks/provenance to `studio.py`.
Jsonnet remains responsible for production resource projection. The existing
projection gains a Studio source mode, preserving network details and NSGs;
the example mode retains its existing behavior. Operation-specific monitoring,
global IAM, spoke attachments and routing dependencies follow the reference.

The output includes the normal catalog/configs, reusable `model.jsonnet`,
original Studio sources, provenance and a human-readable import report. The
report documents compartment/attachment ownership, observability projection,
notification subscriptions, postponed exact routing statements and the
baseline exclusion of Audit Service Connectors. It does not certify unchanged
deployment semantics or complete CIS compliance.

## Runtime and verification

The private workflow offers model or Studio input. Both feed the same
prepare/plan/review/apply path. Tests cover real OE generation, snapshot drift,
unsupported choices, archive/source safety, multi-region global consistency,
network/NSG preservation, existing example regression and runtime bindings.
Publish a PR with passing offline CI; retain mandatory independent review.

## MCCP contract review — 2026-10-06

The user approved adapting the reference to the established MCCP contract.
Reuse the pinned public foundation's TBAC adapter and schema-3 renderer.
Project IAM stays in common, with the project root and APP/DB/INFRA children;
remove superseded per-project admin groups/policies. Publish the official TBAC
tag namespace and generic environment policies in common. Runner extensions
reuse the existing fixed three-policy model only for an explicitly configured
existing dynamic group; the reference does not provision a project runner.

Generate project NSG seeds separately from foundation configurations, retaining
original keys, names and rules. Seeds inject into the existing environment VCN
and bind to the project's INFRA OCID at handoff. Generation and validation must
reject multiple state owners. Subsequent onboarding changes common IAM and
project seeds, never OP02. Retirement removes project declarations only after
the separate project workload retirement process.

Handoff generation requires declared project/region, deployed common and OP02
outputs, exact four subnet roles and source repository/workflow/run/commit.
Emit schema-3 JSON, canonical Markdown path and a separately reviewed project
NSG manifest into an empty package directory. Record actual common/regional
state keys. Reject missing/aliased children, wrong-region/mismatched VCN/subnets,
unreviewed hierarchy, malformed provenance and overwriting existing artifacts.
No cloud execution occurs during generation.

The installed MCCP Cloud Operator validator currently hard-codes the earlier
foundation's state paths. Consumer adaptation must validate expected state
owners from the selected installation; never falsify state provenance to pass
the earlier validator. The deployed end-to-end connection requires a private
installation and OCI acceptance. See [the contract](../../studio-mccp-flow.md).
