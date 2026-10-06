"""Adapt the reference's state ownership to the established MCCP contracts."""
import importlib.util
import re
from functools import lru_cache
from pathlib import Path

from reference import (ROOT, ContractError, checked_path, locked_checkout,
                       read_json, resource_keys, write_json)

PROJECT = re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*')
ENVIRONMENTS = {'dev', 'test', 'uat', 'prod'}


def validate_project_name(environment, project):
    if environment not in ENVIRONMENTS or not PROJECT.fullmatch(project) or len(project) > 30:
        raise ContractError('MCCP requires dev/test/uat/prod and a DNS project name of at most 30 characters')
    if project.startswith('prod-' if environment == 'prod' else 'nonprod-'):
        raise ContractError('project name must omit the derived repository prefix')


def validate_model(model):
    for environment, projects in model['projects'].items():
        if environment not in ENVIRONMENTS:
            raise ContractError('unsupported MCCP workload environment: ' + environment)
        for project in projects:
            validate_project_name(environment, project)
    for region, config in model.get('studio_configs', {}).items():
        projects = {env: value['projects'] for env, value in config['environments'].items()}
        if projects != model['projects']:
            raise ContractError('Studio projects differ from canonical model in region: ' + region)
    runner = model.get('project_runner_dynamic_group')
    if runner is not None and (not isinstance(runner, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,99}', runner)):
        raise ContractError('project_runner_dynamic_group must name an approved existing dynamic group')


def baseline_parts(catalog, path, document):
    parts = Path(path).parts
    if len(parts) != 4 or parts[0] != 'projects' or parts[-1] != 'project-nsgs.json':
        raise ContractError('invalid project baseline path: ' + path)
    environment, project = parts[1].split('-', 1)
    validate_project_name(environment, project)
    region = parts[2]
    if project not in catalog['project_onboarding']['projects'].get(environment, {}) or region not in catalog['regions']:
        raise ContractError('undeclared project baseline: ' + path)
    if set(document) != {'network_configuration'}:
        raise ContractError('project seed must contain only network configuration')
    network = document['network_configuration']
    if set(network) != {'default_enable_cis_checks', 'network_configuration_categories'} or network['default_enable_cis_checks'] is not False:
        raise ContractError('invalid project seed network settings')
    categories = network['network_configuration_categories']
    if set(categories) != {parts[1]} or set(categories[parts[1]]) != {'inject_into_existing_vcns'}:
        raise ContractError('project seed must only inject NSGs into the assigned VCN')
    vcn_key = f"VCN-{catalog['region_codes'][region]}-LZ-{environment.upper()}-PROJECTS-KEY"
    injected = categories[parts[1]]['inject_into_existing_vcns']
    if set(injected) != {vcn_key}:
        raise ContractError('project seed references an unassigned VCN')
    vcn = injected[vcn_key]
    if set(vcn) != {'vcn_id', 'network_security_groups'} or vcn['vcn_id'] != 'binding://project-vcn-id':
        raise ContractError('project seed VCN must bind to deployed evidence')
    groups = vcn['network_security_groups']
    if not isinstance(groups, dict) or not groups:
        raise ContractError('project seed NSGs are missing')
    for key, nsg in groups.items():
        prefix = f"NSG-{catalog['region_codes'][region]}-LZ-{environment.upper()}-{project.upper()}-"
        if not key.startswith(prefix) or not key.endswith('-KEY') or nsg.get('compartment_id') != 'binding://project-infra-compartment-id':
            raise ContractError('project NSG must belong to its project INFRA target')
    return environment, project, region, vcn


def validate_baselines(catalog, documents, owned, errors):
    declared = catalog['project_onboarding'].get('baselines', [])
    expected = {f'projects/{env}-{project}/{region}/project-nsgs.json'
                for env, projects in catalog['project_onboarding']['projects'].items()
                for project in projects for region in catalog['regions']}
    if set(declared) != expected or len(declared) != len(expected):
        errors.append('project baseline catalog is incomplete or duplicated')
    for path in declared:
        try:
            checked_path(ROOT, path)
            _, _, region, _ = baseline_parts(catalog, path, documents[path])
            for key in resource_keys(documents[path]):
                token = (region, key)
                if token in owned:
                    errors.append(f'resource key has two owners: {key}: {owned[token]} and {path}')
                owned[token] = path
        except (ContractError, KeyError, TypeError, ValueError) as exc:
            errors.append('invalid project baseline: ' + path + ': ' + str(exc))


@lru_cache(maxsize=1)
def renderer():
    upstream = locked_checkout('mccp_foundation', ROOT / '.cache')
    spec = importlib.util.spec_from_file_location('mccp_upstream_handoff', upstream / 'scripts/render_project_handoff.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def project_node(common, environment, key):
    try:
        return common['compartments_configuration']['compartments']['CMP-LANDINGZONE-KEY']['children'][
            f'CMP-LZ-{environment.upper()}-KEY']['children'][f'CMP-LZ-{environment.upper()}-PROJECTS-KEY']['children'][key]
    except KeyError as exc:
        raise ContractError('project missing from governed common IAM')


def render_handoff(catalog, environment, project, region, compartments, network, common, network_config, source):
    validate_project_name(environment, project)
    if project not in catalog['project_onboarding']['projects'].get(environment, {}):
        raise ContractError('project has not been onboarded in the reviewed model')
    if region not in catalog['regions']:
        raise ContractError('unknown handoff region')
    if not isinstance(source.get('repository'), str) or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', source['repository']):
        raise ContractError('invalid source repository provenance')
    upstream = renderer()
    project_key = f'CMP-LZ-{environment.upper()}-{project.upper()}-KEY'
    vcn_key = f"VCN-{catalog['region_codes'][region]}-LZ-{environment.upper()}-PROJECTS-KEY"
    try:
        resources = network['network_resources']
        vcn_id = upstream.require_ocid(resources['vcns'], vcn_key, 'vcn', 'VCN')
        if vcn_id.split('.')[3] != region:
            raise ContractError('handoff VCN region mismatch')
        categories = network_config['network_configuration']['network_configuration_categories']
        vcns = [c['vcns'][vcn_key] for c in categories.values() if vcn_key in c.get('vcns', {})]
        if len(vcns) != 1:
            raise ContractError('assigned VCN definition is ambiguous or missing')
        definition = vcns[0]
        vcn = {'key': vcn_key, 'name': definition['display_name'], 'cidr': definition['cidr_blocks'][0], 'ocid': vcn_id}
        subnets = {}
        for role, suffix in {'web': 'WEB', 'app': 'APP', 'database': 'DB', 'infrastructure': 'INFRA'}.items():
            key = f"SN-{catalog['region_codes'][region]}-LZ-{environment.upper()}-{suffix}-KEY"
            subnet_id = upstream.require_ocid(resources['subnets'], key, 'subnet', role)
            if subnet_id.split('.')[3] != region or resources['subnets'][key].get('vcn_id') != vcn_id:
                raise ContractError('handoff subnet region/VCN mismatch')
            subnet = definition['subnets'][key]
            subnets[role] = {'key': key, 'name': subnet['display_name'], 'cidr': subnet['cidr_block'], 'ocid': subnet_id}
        if len({s['ocid'] for s in subnets.values()}) != 4:
            raise ContractError('handoff subnet roles must have distinct OCIDs')
        project_config = {'compartments_configuration': {'compartments': {project_key: project_node(common, environment, project_key)}}}
        data = upstream.build_handoff_data(f'{environment}-{project}', project_config,
            {'iam_resources': compartments}, {'schema_version': 2, 'environment': environment, 'region': region, 'network': {'vcn': vcn, 'subnets': subnets}})
        if len({data['project_root']['ocid']} | {v['ocid'] for v in data['compartments'].values()}) != 4:
            raise ContractError('TBAC project compartment targets must be distinct')
        stacks = {s['id']: s for s in catalog['stacks']}
        iam = stacks[catalog['project_onboarding']['iam_stack']]
        regional = stacks[f'workload_{environment}/{region}']
        if iam['scope'] != 'global' or regional['operation'] != 'OP02' or regional['region'] != region:
            raise ContractError('handoff state ownership is invalid')
        target = ('prod-' if environment == 'prod' else 'nonprod-') + project
        machine = upstream.build_machine_handoff(data, source, regional['state_key'], iam['state_key'], target,
                                                f'environments/{environment}/environment_information.md')
        return data, machine, upstream.render_markdown(data)
    except (upstream.HandoffError, KeyError, TypeError, IndexError) as exc:
        raise ContractError('missing/invalid deployed handoff evidence: ' + str(exc)) from exc


def write_handoff(generated, environment, project, region, compartments_path, network_path, source, output):
    from reference import check_resolved_config, load_documents, validate
    generated, output = Path(generated).resolve(), Path(output).resolve()
    if output == generated or output.is_relative_to(generated):
        raise ContractError('handoff package must be separate from generated source')
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ContractError('handoff requires an empty directory; never overwrite project configuration')
    catalog = read_json(generated / 'catalog.json')
    documents = load_documents(generated, catalog)
    validate(catalog, documents)
    stacks = {s['id']: s for s in catalog['stacks']}
    sid = f'workload_{environment}/{region}'
    if sid not in stacks:
        raise ContractError('missing OP02 stack for project environment/region')
    compartments, network = read_json(compartments_path), read_json(network_path)
    data, machine, markdown = render_handoff(catalog, environment, project, region, compartments, network,
        documents['common/config.json'], documents[stacks[sid]['configurations']['complete']], source)
    baseline = documents[f'projects/{environment}-{project}/{region}/project-nsgs.json']
    bindings = {'binding://project-vcn-id': machine['vcn'], 'binding://project-infra-compartment-id': machine['infrastructure_compartment']}
    def bind(value):
        if isinstance(value, dict):
            return {k: bind(v) for k, v in value.items()}
        if isinstance(value, list):
            return [bind(v) for v in value]
        if isinstance(value, str) and value.startswith('binding://'):
            if value not in bindings:
                raise ContractError('unknown project binding: ' + value)
            return bindings[value]
        return value
    manifest = bind(baseline)
    check_resolved_config(manifest, network, region)
    write_json(output / 'project-foundation-handoff.json', machine)
    path = checked_path(output, machine['handoff_path'])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown)
    write_json(output / f'oci/{environment}/{region}/network/project-nsgs.json', manifest)
    return machine


def validate_handoff(catalog, machine, markdown, source_repository):
    """Consumer gate with state owners taken from the selected foundation catalog."""
    upstream = renderer()
    try:
        environment, region = machine['environment'], machine['region']
        target = machine['target_repository']
        prefix = 'prod-' if environment == 'prod' else 'nonprod-'
        if not target.startswith(prefix):
            raise ContractError('invalid handoff repository routing')
        project = target.removeprefix(prefix)
        validate_project_name(environment, project)
        if project not in catalog['project_onboarding']['projects'].get(environment, {}) or region not in catalog['regions']:
            raise ContractError('undeclared handoff project/region')
        stacks = {s['id']: s for s in catalog['stacks']}
        common = stacks[catalog['project_onboarding']['iam_stack']]
        network = stacks[f'workload_{environment}/{region}']
        if common['scope'] != 'global' or network['operation'] != 'OP02':
            raise ContractError('invalid catalog state ownership')
        roles = ('app', 'database', 'infrastructure')
        compartments = {role: {'ocid': machine[role + '_compartment']} for role in roles}
        ids = [machine['project_root_compartment']] + [v['ocid'] for v in compartments.values()]
        if len(set(ids)) != 4:
            raise ContractError('TBAC project compartment targets must be distinct')
        for ocid in ids:
            upstream.require_ocid({'key': {'id': ocid}}, 'key', 'compartment', 'project compartment')
        vcn = upstream.require_ocid({'key': {'id': machine['vcn']}}, 'key', 'vcn', 'project VCN')
        if vcn.split('.')[3] != region:
            raise ContractError('handoff VCN region mismatch')
        if set(machine['subnets']) != {'web', 'app', 'database', 'infrastructure'} or len(set(machine['subnets'].values())) != 4:
            raise ContractError('invalid handoff subnet roles')
        for ocid in machine['subnets'].values():
            upstream.require_ocid({'key': {'id': ocid}}, 'key', 'subnet', 'project subnet')
            if ocid.split('.')[3] != region:
                raise ContractError('handoff subnet region mismatch')
        if machine['source_repository'] != source_repository or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', source_repository):
            raise ContractError('handoff source repository does not match the selected installation')
        source = {key: machine['source_' + key] for key in ('repository', 'workflow', 'run', 'commit')}
        data = {'project': f'{environment}-{project}', 'environment': environment, 'region': region,
                'project_root': {'ocid': ids[0]}, 'compartments': compartments,
                'vcn': {'ocid': vcn}, 'subnets': {k: {'ocid': v} for k, v in machine['subnets'].items()}}
        expected = upstream.build_machine_handoff(data, source, network['state_key'], common['state_key'], target,
                                                  f'environments/{environment}/environment_information.md')
        if machine != expected:
            raise ContractError('handoff fields/state provenance do not match schema 3 and the foundation catalog')
        if any(str(value) not in markdown for value in [project, environment, region, vcn] + ids + list(machine['subnets'].values())):
            raise ContractError('Markdown and machine handoff are inconsistent')
        return {'schema_version': 3, 'project': f'{environment}-{project}', 'target_repository': target,
                'handoff_path': machine['handoff_path'], 'op02_state_key': network['state_key'], 'op04_state_key': common['state_key']}
    except (upstream.HandoffError, KeyError, TypeError, IndexError) as exc:
        raise ContractError('invalid MCCP handoff: ' + str(exc)) from exc
