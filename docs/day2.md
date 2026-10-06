# Day 2 operations

[Back to README](../README.md)

| Change | Owning operation |
| --- | --- |
| Global IAM/tags | OP00 |
| Shared routing/firewall | OP01 final |
| Environment network/security/monitoring | OP02 |
| Platform resources or platform alerts/logs | OP03 |
| Project onboarding/retirement IAM | OP04 through OP00, then handoff |
| Application resources/patching/backup | Project execution inside handoff |

Identify the owner/state, regenerate complete inputs, review dependencies,
plan, approve independently, apply, verify and publish outputs. Preserve current
keys/effective tags; distinguish infrastructure changes from ephemeral local
output-file changes. Cross-stack changes are separately reviewed steps.

After completion, hub maintenance uses final; bootstrap is not a rollback or
Day 2 mode. Changing a folder path does not move its Terraform state. A second
region needs independent state and available inputs/outputs. Remote peering and
application DR are additional reviewed operations.
