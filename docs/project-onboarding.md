# OP04 project onboarding

[Back to README](../README.md)

OP04 prepares a reviewed project-management change against consolidated IAM
in common; it does not create a second IAM state owner.

```bash
python3 scripts/onboard.py --model customer/model.jsonnet \
  --environment dev --project billing --output customer/model-next.json
python3 scripts/reference.py generate --model customer/model-next.json \
  --output generated/revision-002
```

Review project compartments/groups/policies in the complete common configuration.
Upstream owns their definitions. The synthetic example removes project NSGs
from OP02 foundation for later project execution. Studio imports preserve
their project NSGs in OP02, so onboarding also changes the affected regional
network configuration: review and deploy those operation changes separately
before handing over the project. Regeneration does not authorize cascading
applies. One NSG must have one state owner; do not let project automation also
manage an NSG owned by OP02.

```bash
python3 scripts/reference.py handoff \
  --generated generated/revision-002 --environment dev --project billing \
  --region eu-frankfurt-1 \
  --compartments private-outputs/common/compartments_output.json \
  --network private-outputs/workload_dev/eu-frankfurt-1/network_output.json \
  --output handoffs/dev-billing-fra/project-foundation-handoff.json
```

The boundary includes the deployed compartment and assigned VCN/subnets, no
credentials, no IAM/hub grant. Review deployment evidence before publication
in the private project repository. It is a reference-owned version-1 contract,
not the MCCP machine handoff or an official Orchestrator output. File publication
has no state. MCCP already defines a schema-3 handoff and project NSGs in INFRA;
the current projection must be adapted to that established contract. See the
[MCCP contract and adaptation gaps](studio-mccp-flow.md).

Use separate prod/non-prod project repositories, executor and workload-state
bucket. Foundation grants effective permissions; JSON constraints do not enforce
IAM. Retirement removes project workload resources first, then common IAM and
handoff access, through separate reviews with recovery evidence.
