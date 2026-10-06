# Existing Entities: Foundation Delivery Contract

This document describes the existing data contract; it introduces no new runtime schema.

| Entity | Existing fields / relationships | Validation / lifecycle |
| --- | --- | --- |
| Canonical model | Home region, regions, LZ environment, workload environments, platforms, projects, optional imported `studio_configs` | Supported scope; imported/canonical projects must agree; approved source -> new generated revision |
| Generated revision | `catalog.json`, operation configurations, `model.jsonnet`, `provenance.json`, optional original Studio sources/report, separate project NSG seeds | New/empty destination; pinned generation; no overwrite; import report reviewed before promotion |
| Stack catalog entry | `id`, `operation`, `scope`, `region`, `state_region`, `state_key`, `configurations`, `requires`, outputs and execution/review boundaries | Unique state/output owner; regional state region equals managed region; same-region producers; one OP01 entry contains bootstrap/final |
| OP04 declaration | Project/environment, common IAM operation target, handoff metadata and project baselines | No handoff state; synchronize canonical/imported project declaration; retirement follows workload retirement |
| Producer outputs | Compartment keys/IDs and regional network resources with IDs; linked to producer paths in the catalog | Required outputs present; producer merges must be disjoint; bindings resolve to appropriate same-region identifiers |
| Prepared operation | Selected stack/stage, resolved configuration/dependencies, `inputs.tfvars.json`, CLI file mode or private OCI bucket mode | No unresolved output/binding placeholders; no cloud execution; selected stack region retained |
| CLI workdir | Complete pinned Orchestrator tree, existing provider aliases with Instance Principal overrides, catalog backend region/key | New destination; local prepared source and region must match selected stack; staging only |
| MCCP package | `project-foundation-handoff.json` schema 3, canonical environment Markdown, bound project NSG manifest | Declared project; four distinct compartments; VCN and four subnet roles; expected source repo; schema/routing/state/Markdown consistency |
| Provenance | Upstream hashes; imported source hashes; source repository/workflow/run/commit on handoff | Pins and input structure can be checked offline; actual deployment and protected-run authenticity require operator evidence |
| Acceptance record | Requirement/scenario IDs, task IDs, command results, owning code/docs, pending installation checks | Current results distinct from historical evidence; synthetic outputs never labeled deployed evidence |

Approved source -> generation/import -> reviewed revision -> selected operation preparation
-> reviewed plan -> approved deployment -> live verification -> producer publication
-> rendered/validated handoff -> reviewed project publication -> MCCP requests.
Only the source, preparation, and local package-validation transitions are exercised here.
