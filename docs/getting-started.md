# Getting started

[Back to README](../README.md)

## Check tools and clone

Install Git, Python 3.10+ and Jsonnet 0.20+ using your approved package manager.
The local generation steps require GitHub access to fetch the immutable commits
in [upstream.lock.json](../upstream.lock.json); they require no OCI credentials.

```bash
git --version
python3 --version
jsonnet --version
git clone https://github.com/multicloud-control-plane/oci-landing-zone-reference.git
cd oci-landing-zone-reference
```

Use an approved reference revision. All following commands run from this source
checkout unless a step explicitly changes directory.

## Run the offline demo

```bash
python3 scripts/reference.py generate --output generated/demo-revision-001
python3 scripts/reference.py validate --generated generated/demo-revision-001
python3 scripts/check_contract.py --generated generated/demo-revision-001
```

Expected: **11 foundation stacks, 13 configurations, 4 project NSG seeds and
431 owned keys**, valid operation boundaries and a passed Orchestrator family
contract check. Inspect `generated/demo-revision-001/catalog.json`: common owns
global IAM; each hub has bootstrap/final configurations sharing one state.
This synthetic example is for offline inspection. A repeated generation needs
a new empty revision directory.

## Establish the private source

Cloud Operations creates a private configuration repository with reviewed write
access. Set `PRIVATE_CONFIG_REPOSITORY_URL` to that repository's clone URL:

```bash
git clone "$PRIVATE_CONFIG_REPOSITORY_URL" customer
mkdir -p customer/config
```

`customer/` is a separate Git checkout ignored by this reference. Keep customer
commits in that repository. Generated revisions and runtime outputs remain
outside its source tree:

```text
oci-landing-zone-reference/          # reference code checkout
  customer/                        # separate private configuration checkout
    config/
      model.jsonnet                # reviewed canonical deployment source
      studio/                      # original ZIP evidence if Studio is used
  generated/
    demo-revision-001/              # synthetic offline example
    revision-001/                   # reviewed private configuration set
  private-outputs/                  # verified deployed producer artifacts
  .runtime/                        # prepared inputs, pinned workdirs and plans
```

Choose one initial authoring mode, then keep `customer/config/model.jsonnet` as
the source of truth for subsequent Git changes.

### Studio design and promotion

Use the supported scope in [Studio import](studio-import.md): Hub B, CIS1, oc1,
no environment Security Zones or OKE/OCVS extensions. Save one export ZIP per
region to `customer/config/studio/`, including the home region. Replace the email
with the approved operations address before running:

```bash
python3 scripts/reference.py import-studio \
  --source customer/config/studio/studio-fra.zip \
  --source customer/config/studio/studio-ams.zip \
  --home-region eu-frankfurt-1 --landing-zone-environment shared \
  --notification-email operations@example.com \
  --output generated/revision-001
python3 scripts/reference.py validate --generated generated/revision-001
python3 scripts/check_contract.py --generated generated/revision-001
```

Cloud Operations reviews `studio-import-report.md`, provenance and the generated
ownership/network changes. After that review, promote the normalized source:

```bash
cp generated/revision-001/model.jsonnet customer/config/model.jsonnet
```

Commit the promoted model and original ZIPs through the private repository's
review process. `studio-source/` inside the generated revision is import evidence.
Later generation uses the promoted model and a new revision directory; later
Studio edits must preserve projects added since the initial export.

### Model alternative

For initial model authoring, copy the synthetic example as a starting point:

```bash
cp examples/two-region.jsonnet customer/config/model.jsonnet
```

Review/edit home region, regional CIDRs, environments, platforms, projects and
notification address for the installation. Commit the approved source in the
private repository, then generate into the new private revision:

```bash
python3 scripts/reference.py generate \
  --model customer/config/model.jsonnet --output generated/revision-001
python3 scripts/reference.py validate --generated generated/revision-001
python3 scripts/check_contract.py --generated generated/revision-001
```

For either mode, completion means a reviewed canonical model, a matching generated
revision and passing local validation. Customer changes can alter demo counts.
Continue with [generation and dependencies](generation-and-dependencies.md),
starting at `common/complete`. Deployment prerequisites and execution belong to
[Terraform CLI](terraform-cli.md) or [Resource Manager](resource-manager.md);
optional workflow installation belongs to [private workflows](private-workflows.md).
