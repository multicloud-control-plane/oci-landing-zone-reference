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
