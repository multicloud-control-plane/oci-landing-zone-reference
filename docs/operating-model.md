# Operating model and operational security

[Back to README](../README.md)

Agree the repeatable operation (what), requester/writer/reviewer/executor (who),
home/regional location, state and dependency contract before assigning resources.
OP numbering follows the Operations Advisory asset; Multi-OE uses other names.

The default example has one central Cloud Operations configuration writer,
with IAM, networking, environment and platform reviewers. The catalog records
execution roles; installation maps them to scoped ORM or runner identities.
A role label is not an OCI permission grant.

| Operation | Execution scope |
| --- | --- |
| OP00 | Governed IAM and global services, home region |
| OP01 | Shared hub/DRG/routing/firewall and regional controls |
| OP02 | Assigned environment network/attachment/scanning/monitoring |
| OP03 | Assigned platform footprint and monitoring |
| OP04 | Project IAM change through OP00, then handoff |

Exact policies remain in official generated IAM; review effective permissions
during installation. Platform and project teams do not acquire policy-writing
permission by operating their resources. CODEOWNERS routes reviewers; repository
write access is repository-wide. Independent configuration writers need separate
repositories and executor identities. Preserve state keys when moving folders.

The implemented consolidated IAM pattern stores all levels in `common/`.
IAM per operation is a design alternative requiring non-regional IAM stacks and
explicit compartments-output aggregation; it is not a mode of this adapter.

OP02 owns the environment spoke and monitoring. OP03 owns its dedicated VCN in
the platform compartment, attachment, scanning, logs, topic and network alarms.
Projects manage approved resources within their handoff, such as NSGs on the
assigned network, using separate workload state/access boundaries.

The example shares one hub between prod/dev. Workload states are independent;
changes to their shared hub still share an operation. Separate LZ environments
when the security/availability model requires independent hubs. This initial
adapter supports one LZ environment per installation.

Regional states live in private, versioned buckets in their managed region.
Global state lives in home region. Project workload buckets are isolated from
foundation state. Replicate reviewed global outputs into each region's private
dependency store; regional operations consume local copies and same-region hubs.
