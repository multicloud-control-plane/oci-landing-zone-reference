# Generation and dependencies

[Back to README](../README.md)

`gen/project.libsonnet` calls the pinned official `landing_zone.libsonnet`.
It projects state ownership and baseline scope; upstream owns resource semantics.

Follow [Getting started](getting-started.md) for the reviewed private source at
`customer/config/model.jsonnet` and `generated/revision-001`. Generation rejects
nonempty directories to prevent stale configuration retention. All regions
must share one global hierarchy; IAM outside policy statements must agree.
Regional service-policy statements are combined in the single IAM configuration.

The emitted `catalog.json` (version 2) is reference-owned orchestration metadata, not an
Orchestrator configuration family. Each `config.json` is a complete input set.

Use [Studio import](studio-import.md) for exported Studio designs. Its normalized
model retains original network choices and project NSGs. Both source modes
emit NSG seeds outside foundation states under `projects/`, for the project's
schema-3 handoff and reviewed workload deployment. Catalog validation includes
seed ownership; project NSGs cannot also belong to a foundation configuration.

## Initial order: Frankfurt example

Each row is one selected execution followed by live verification and output
publication. Use [CLI](terraform-cli.md) or [Resource Manager](resource-manager.md)
for execution. Start at common in the home region; OP04 later updates that same
IAM state and publishes an artifact, with no separate handoff state.

| Order | Operation / stack ID | Stage | Required published producers | Publish after verification |
| --- | --- | --- | --- | --- |
| 1 | OP00 `common` | `complete` | None | `common/compartments_output.json` |
| 2 | OP01 `lze_shared/eu-frankfurt-1` | `bootstrap` | common | Hub `network_output.json` |
| 3 | OP02 `workload_dev/eu-frankfurt-1` | `complete` | common, hub bootstrap | Dev `network_output.json` |
| 3 | OP02 `workload_prod/eu-frankfurt-1` | `complete` | common, hub bootstrap | Prod `network_output.json` |
| 3 | OP03 `lze_shared/eu-frankfurt-1/platform_ops` | `complete` | common, hub bootstrap | Shared ops `network_output.json` |
| 4 | OP03 `workload_prod/eu-frankfurt-1/platform_data` | `complete` | common, hub bootstrap, prod | Prod data `network_output.json` |
| 5 | OP01 `lze_shared/eu-frankfurt-1` | `final` | common, hub bootstrap, dev, prod, shared ops, prod data | Updated hub `network_output.json` |
| 6 | OP04 IAM change / handoff | `common/complete`, then artifact | Applied common IAM and selected OP02 outputs | [Reviewed project package](project-onboarding.md) |

Repeat regional rows in Amsterdam using `eu-amsterdam-1` IDs and that region's
outputs/bindings. Common is applied once in the home region. Inspect `requires`
and `completion_requires` in the private revision's `catalog.json` for the actual
model. Every declared completion producer must exist: deploying dev alone cannot
complete the full example's hub. To use a smaller topology, review a smaller
source model and generate a new revision first.

Bootstrap is not a finished production network. Never rerun bootstrap after
completion: it would remove final routing. Hub Day 2 uses the full final
configuration with `--stage final`.

Prepare the first operation locally; common has no producer dependency:

```bash
python3 scripts/reference.py prepare \
  --generated generated/revision-001 --stack common --stage complete \
  --outputs private-outputs --destination .runtime/common-inputs --runtime cli
python3 -m json.tool .runtime/common-inputs/inputs.tfvars.json
```

Expected: resolved `config.json`, `dependencies.json` and `inputs.tfvars.json` in
the preparation directory, with the home region and an absolute
`output_folder_path` ending in `.runtime/common-inputs/outputs`. Preparation runs
neither Terraform nor OCI. Use a distinct preparation/workdir for each reviewed
execution so saved plans retain their exact inputs.

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

## Publish deployed outputs

After approved apply, Cloud Operations verifies live resources and the official
JSON produced at the prepared `output_folder_path`. From the reference checkout,
inspect and copy the first producer:

```bash
python3 -m json.tool .runtime/common-inputs/outputs/compartments_output.json
mkdir -p private-outputs/common
cp .runtime/common-inputs/outputs/compartments_output.json \
  private-outputs/common/compartments_output.json
```

For a regional execution, use its exact stack ID as the producer directory. For
example, after preparing/executing hub bootstrap with destination
`.runtime/hub-fra-bootstrap-inputs`:

```bash
python3 -m json.tool .runtime/hub-fra-bootstrap-inputs/outputs/network_output.json
mkdir -p private-outputs/lze_shared/eu-frankfurt-1
cp .runtime/hub-fra-bootstrap-inputs/outputs/network_output.json \
  private-outputs/lze_shared/eu-frankfurt-1/network_output.json
```

Apply this mapping to every producer row, including platform subdirectories.
Inspect OCIDs, region, source revision and successful apply evidence before
replacing a published file. Retain the prior artifact/evidence privately for
recovery. Publish final hub outputs to the same producer directory after final
verification. Mirror this tree to the approved regional private store before
dispatching consumers; replicate common outputs where regional independence
requires it. ORM downloads use the catalog's `outputs/<stack-id>/` object prefix.
Completion means the verified producer file is available at the declared path.

Preparation loads declared producers. Hub final also reads the bootstrap hub
and same-region spoke/platform outputs. Global outputs can be local replicas.
The recursive union accepts disjoint maps and rejects duplicate values,
including identical duplicate IDs. Null/empty sections do not erase resources.
The facade receives one aggregate document; no facade deep merge is assumed.

Spokes resolve the DRG by key, but their external DRG route table by OCID.
Hub completion preserves exact attachment-ID distribution matches/priorities.
Internal `output://...` and `binding://...` markers must resolve before deployment;
they are reference preparation syntax, not native Orchestrator input syntax.

## Discover and bind the firewall private IP

After hub bootstrap, Cloud Operations uses the
[pinned official firewall discovery guide](https://github.com/oci-landing-zones/oci-landing-zone-operating-entities/blob/aa65ab5cfa2b5e511e736f311bac22f638badf76/commons/content/howto_identify_private_ip_ocid_network_firewall.md)
in the approved OCI session. Its lookup selects the firewall's IP address and
subnet; inspect the returned private-IP `id` and verify the managed region and
hub firewall subnet. The binding is the **private-IP OCID**, not the firewall
OCID or IP address.

Store the result in `customer/config/firewall-bindings.json`. This example is
synthetic; replace the entire value with the verified Frankfurt private-IP OCID:

```json
{
  "firewall-private-ip-id": "ocid1.privateip.oc1.eu-frankfurt-1.REPLACE_WITH_VERIFIED_PRIVATE_IP"
}
```

With all declared producer outputs published, prepare final:

```bash
python3 scripts/reference.py prepare \
  --generated generated/revision-001 --stack lze_shared/eu-frankfurt-1 \
  --stage final --outputs private-outputs \
  --bindings customer/config/firewall-bindings.json \
  --destination .runtime/hub-fra-final-inputs --runtime cli
```

Review the resolved routing/firewall configuration, then use the runtime helper
and the **same hub state key** for final execution. Completion requires approved
apply, live traffic/isolation checks and updated producer publication. For
Amsterdam, use its verified binding in a separately reviewed regional file;
the optional workflow reads the fixed `config/firewall-bindings.json`, so select
the correct regional installation/source before dispatch. Missing outputs,
conflicting keys, bad regions and invalid bindings stop preparation.
