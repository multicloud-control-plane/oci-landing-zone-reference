# Offline Validation: Foundation Delivery Contract

Run from the repository root with Git, Python 3.10+, Jsonnet 0.20+, and access to the
immutable upstream pins. No OCI credentials are needed. Use new empty revision/workdir
paths for each run; the example paths below are synthetic and ignored by Git.

## Existing contract suite

```bash
python3 -m unittest discover -s tests -v
```

Expected: the existing 47 tests pass, including verified Studio ZIP import/regeneration,
invalid inputs, every model preparation phase, ORM inputs, and MCCP boundary/lifecycle checks.

## Model and Studio revisions

```bash
python3 scripts/reference.py generate --output generated/sdd-model-001
python3 scripts/reference.py validate --generated generated/sdd-model-001
python3 scripts/check_contract.py --generated generated/sdd-model-001
python3 scripts/reference.py generate --output generated/sdd-repeat-001
python3 scripts/reference.py import-studio --source tests/fixtures/studio-hub-b.jsonnet --home-region eu-frankfurt-1 --landing-zone-environment shared --notification-email operations@example.com --output generated/sdd-studio-001
python3 scripts/reference.py validate --generated generated/sdd-studio-001
python3 scripts/check_contract.py --generated generated/sdd-studio-001
```

The model must yield 11 stacks, 13 phases, 4 project seeds, and 431 owned keys; facade
validation covers 17 documents. Compare the generated model/catalog and every operation
configuration/project seed with the repeated revision. The synthetic Studio fixture has
5 stacks; record its phase/seed/key counts and verify the source report/hashes. The ZIP
and source-preservation cases are exercised by the existing Studio suite.

## Synthetic preparation, staging, and handoff smoke checks

Use [the existing output fixture](../../tests/output_fixtures.py) to build synthetic
common/network outputs for the model revision, entirely under `.runtime/sdd-smoke-001`.
Call the existing `reference.prepare` for common before any outputs exist, then for all
13 phases using those fixtures and a per-region synthetic private-IP binding. Assert no
unresolved `output://` or `binding://` in prepared configurations. Check ORM mode supplies
private-bucket/object variables, using the existing contract test.

Call `runtime.stage_workdir` for prepared common/FRA and dev/AMS with a synthetic tenancy,
bucket, and namespace. Assert the staged backend key/region equals the selected catalog
entry, and the root `home`/`secondary_region` OCI provider aliases are preserved. These
calls only copy/stage files: do not run Terraform.

The following local smoke invocation uses only existing preparation, fixture, runtime,
and handoff functions. It creates no live resources:

```bash
python3 - <<'PYCODE'
from pathlib import Path
import sys
sys.path[:0] = ['scripts', 'tests']
import reference as ref
from output_fixtures import synthetic_outputs
from runtime import stage_workdir
from mccp import write_handoff, validate_handoff
revision, work = Path('generated/sdd-model-001'), Path('.runtime/sdd-smoke-001')
catalog = ref.read_json(revision / 'catalog.json')
paths = {p for stack in catalog['stacks'] for p in stack['configurations'].values()}
paths.update(catalog['project_onboarding']['baselines'])
documents = {p: ref.read_json(revision / p) for p in paths}
ref.prepare(revision, 'common', 'complete', work / 'not-yet-published', work / 'common-first', 'cli')
synthetic_outputs(catalog, documents, work / 'outputs')
for stack in catalog['stacks']:
    for phase in stack['configurations']:
        ref.prepare(revision, stack['id'], phase, work / 'outputs', work / 'prepared' / stack['id'] / phase, 'cli', bindings={'firewall-private-ip-id': 'ocid1.privateip.oc1.' + stack['region'] + '.synthetic'})
for sid, label in [('common', 'common'), ('workload_dev/eu-amsterdam-1', 'dev-ams')]:
    stage_workdir(revision, sid, work / 'prepared' / sid / 'complete', work / 'staged' / label, 'synthetic-state', 'synthetic', 'ocid1.tenancy.oc1..synthetic')
source = {'repository': 'example/foundation', 'workflow': 'Offline acceptance fixture', 'run': '123', 'commit': 'a' * 40}
for env in ['prod', 'dev']:
    package = work / ('handoff-' + env)
    machine = write_handoff(revision, env, 'shop', 'eu-frankfurt-1', work / 'outputs/common/compartments_output.json', work / 'outputs' / ('workload_' + env) / 'eu-frankfurt-1/network_output.json', source, package)
    validate_handoff(catalog, machine, (package / 'environments' / env / 'environment_information.md').read_text(), 'example/foundation')
    print(env, machine['target_repository'], machine['op04_state_key'], machine['op02_state_key'])
print('Prepared phases:', sum(len(s['configurations']) for s in catalog['stacks']))
PYCODE
```

For prod-shop and dev-shop in FRA, call the existing `mccp.write_handoff` using the fixture
outputs and explicitly synthetic source `example/foundation`, workflow `Offline acceptance
fixture`, run `123`, and commit forty `a` characters. Call `mccp.validate_handoff` with the
matching catalog/Markdown/source. Assert production/non-production routing, common/OP02
state owners, and bound INFRA/project-VCN NSG manifests. Reject wrong state/source/region
packages. A CLI acceptance invocation for each produced package is:

```bash
python3 scripts/reference.py validate-handoff --generated generated/sdd-model-001 --handoff-json .runtime/sdd-smoke-001/handoff-prod/project-foundation-handoff.json --handoff-markdown .runtime/sdd-smoke-001/handoff-prod/environments/prod/environment_information.md --source-repository example/foundation
python3 scripts/reference.py validate-handoff --generated generated/sdd-model-001 --handoff-json .runtime/sdd-smoke-001/handoff-dev/project-foundation-handoff.json --handoff-markdown .runtime/sdd-smoke-001/handoff-dev/environments/dev/environment_information.md --source-repository example/foundation
python3 scripts/check_docs.py
```

Record commands/results and FR/SC/scenario mappings in `acceptance.md`, keeping generated
outputs and workdirs out of source control. Interface details are in
[delivery contracts](contracts/delivery.md) and [entities](data-model.md).

## Real-installation boundary

The [existing validation guide](../../docs/validation.md#real-installation-acceptance)
owns the pending checklist for reviewed deploys, IAM, regional state locking, firewall
traffic, project lifecycle, migration/rollback, and effective MCCP consumption. Synthetic
local results do not complete those scenarios or authorize installation changes.
