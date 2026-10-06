# Upstream provenance and updates

[Back to README](../README.md)

Inspected 2026-10-06; immutable pins in [upstream.lock.json](../upstream.lock.json):

| Source | Observed ref | Commit |
| --- | --- | --- |
| Operating Entities | master | aa65ab5cfa2b5e511e736f311bac22f638badf76 |
| Orchestrator | main | 4faa47489242abe056fb5ceb0288c51e29522902 |
| Repository Design | OperationsAdvisory-repository-design | 79e718aa0c70c4a794fb43a7a21a58820a37bb73 |
| MCCP foundation contract/TBAC adapter | main | 9b4033267af881e65fe8c2b212f220b2804cac09 |

Pins provide repeatability, not a claim of always being latest. Orchestrator
uses networking v0.8.3; the mutable release-2.1.4 branch is a different ref.
OE owns resource semantics; the local adapter owns tailored operation/state
projection and preparation syntax. The catalog is reference-owned; the machine
handoff reuses MCCP schema 3. The imported TBAC add-on files at the pinned OE
revision are identical to those at MCCP's recorded OE revision
`dab13856ba6701c45baafc163780bb76562c039a`.

The existing MCCP oci-landing-zone demonstrates one-region foundation/project
flows. This reference implements the Operations Advisory multi-region ownership
design. It reuses the pinned public TBAC adapter and handoff renderer, without
running the older foundation's workflows or adopting its state layout.

Pin updates need a reviewed change, regeneration/diff, contract tests and
test-tenancy acceptance before customer upgrades. Public checkout/setup actions
are SHA-pinned; CI Jsonnet comes from Ubuntu 24.04. Customer pipelines must
standardize the toolchain image/packages and retain a reviewed provider lock.
