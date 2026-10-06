# Generation and dependencies

[Back to README](../README.md)

`gen/project.libsonnet` calls the pinned official `landing_zone.libsonnet`.
It projects state ownership and baseline scope; upstream owns resource semantics.

```bash
python3 scripts/reference.py generate --model customer/model.jsonnet --output generated/revision-001
python3 scripts/reference.py validate --generated generated/revision-001
python3 scripts/check_contract.py --generated generated/revision-001
```

Use a private reviewed model and a new output directory. Generation rejects
nonempty directories to prevent stale configuration retention. All regions
must share one global hierarchy; IAM outside policy statements must agree.
Regional service-policy statements are combined in the single IAM configuration.

The emitted `catalog.json` is reference-owned orchestration metadata, not an
Orchestrator configuration family. Each `config.json` is a complete input set.

## Initial order

1. OP00 common in home region; save compartments output.
2. OP01 bootstrap per region: hub, DRG and shared controls.
3. OP02 environments and OP03 shared platforms.
4. OP03 environment platforms after their OP02.
5. OP01 final in the same hub state, binding actual firewall private IP and
   attachment outputs. Review firewall policy and test traffic/isolation.
6. OP04 handoffs after corresponding IAM and environment deployment.

Bootstrap is not a finished production network. Never rerun bootstrap after
completion: it would remove final routing. Day 2 uses complete final inputs.

## Output contract

Maintain actual files outside public Git:

```text
private-outputs/
  common/compartments_output.json
  lze_shared/eu-frankfurt-1/network_output.json
  workload_prod/eu-frankfurt-1/network_output.json
  workload_dev/eu-frankfurt-1/network_output.json
  lze_shared/eu-frankfurt-1/platform_ops/network_output.json
  workload_prod/eu-frankfurt-1/platform_data/network_output.json
  ...same-region Amsterdam producers...
```

Preparation loads declared producers. Hub final also reads the bootstrap hub
and same-region spoke/platform outputs. Global outputs can be local replicas.
The recursive union accepts disjoint maps and rejects duplicate values,
including identical duplicate IDs. Null/empty sections do not erase resources.
The facade receives one aggregate document; no facade deep merge is assumed.

Spokes resolve the DRG by key, but their external DRG route table by OCID.
Hub completion preserves exact attachment-ID distribution matches/priorities.
Internal `output://...` and `binding://...` markers must resolve before deployment;
they are reference preparation syntax, not native Orchestrator input syntax.

For final, use a private bindings file containing the actual
`firewall-private-ip-id` OCID. Retrieve and verify it against the managed region
and hub subnet using the selected upstream Hub B deployment guide. Missing
outputs, conflicting keys, bad regions and invalid bindings stop preparation.
