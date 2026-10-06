# Upstream provenance and updates

[Back to README](../README.md)

Inspected 2026-10-06; immutable pins in [upstream.lock.json](../upstream.lock.json):

| Source | Observed ref | Commit |
| --- | --- | --- |
| Operating Entities | master | aa65ab5cfa2b5e511e736f311bac22f638badf76 |
| Orchestrator | main | 4faa47489242abe056fb5ceb0288c51e29522902 |
| Repository Design | OperationsAdvisory-repository-design | 79e718aa0c70c4a794fb43a7a21a58820a37bb73 |

Pins provide repeatability, not a claim of always being latest. Orchestrator
uses networking v0.8.3; the mutable release-2.1.4 branch is a different ref.
OE owns resource semantics; the local adapter owns tailored operation/state
projection and preparation syntax. Catalog/handoff formats are local contracts.

The existing MCCP oci-landing-zone demonstrates one-region foundation/project
flows. This reference implements the Operations Advisory multi-region ownership
design without depending on that repository's runtime/configuration.

Pin updates need a reviewed change, regeneration/diff, contract tests and
test-tenancy acceptance before customer upgrades. Public checkout/setup actions
are SHA-pinned; CI Jsonnet comes from Ubuntu 24.04. Customer pipelines must
standardize the toolchain image/packages and retain a reviewed provider lock.
