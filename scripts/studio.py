"""Read Studio exports; resource generation stays in the pinned Jsonnet libraries."""
import hashlib
import json
import re
import stat
import subprocess
import tempfile
import zipfile
from pathlib import Path

from reference import (ROOT, ContractError, evaluate, locked_checkout, read_json,
                       run, write_generation, write_json)

MAX_BYTES = 32 * 1024 * 1024
TOKEN = re.compile(r'''\s+|//[^\n]*|/\*.*?\*/|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?|[A-Za-z_][A-Za-z0-9_]*|[{}\[\]:,]''', re.S)
NAME = re.compile(r'[a-z][a-z0-9]{0,19}')


def literal_config(source, workdir):
    """Allow Studio data literals, not imports, functions or executable expressions."""
    tokens, position = [], 0
    while position < len(source):
        match = TOKEN.match(source, position)
        if match is None:
            raise ContractError('Studio config must be literal-object Jsonnet')
        token = match.group()
        position = match.end()
        if token.isspace() or token.startswith(('//', '/*')):
            continue
        tokens.append(token)
    if not tokens or tokens[0] != '{' or tokens[-1] != '}':
        raise ContractError('Studio config must be literal-object Jsonnet')
    for index, token in enumerate(tokens):
        if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', token):
            if token not in {'true', 'false', 'null'} and (index + 1 == len(tokens) or tokens[index + 1] != ':'):
                raise ContractError('Studio config must be literal-object Jsonnet; imports and expressions are unsupported')
    path = Path(workdir) / 'config.jsonnet'
    path.write_text(source)
    return json.loads(run(['jsonnet', str(path)], timeout=30))


def read_export(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ContractError('Studio source must be a file under 32 MiB')
    contents = {}
    try:
        if path.suffix.lower() == '.zip':
            with zipfile.ZipFile(path) as archive:
                entries = archive.infolist()
                if len(entries) > 64 or sum(e.file_size for e in entries) > MAX_BYTES:
                    raise ContractError('Studio archive exceeds size/file limits')
                for entry in entries:
                    name = entry.filename
                    if (name in contents or '/' in name or '\\' in name or name in {'.', '..'}
                            or stat.S_ISLNK(entry.external_attr >> 16)
                            or (name != 'config.jsonnet' and not re.fullmatch(r'[a-z0-9_]+\.json', name))):
                        raise ContractError('unsafe, duplicate or unsupported Studio archive entry: ' + name)
                    contents[name] = archive.read(entry).decode('utf-8')
            if 'config.jsonnet' not in contents:
                raise ContractError('Studio ZIP requires config.jsonnet')
        elif path.suffix.lower() == '.jsonnet':
            contents['config.jsonnet'] = path.read_bytes().decode('utf-8')
            # A sibling generated set is evidence to verify, not extra input.
            for candidate in path.parent.glob('*.json'):
                if candidate.stat().st_size > MAX_BYTES:
                    raise ContractError('Studio snapshot exceeds size limit')
                contents[candidate.name] = candidate.read_bytes().decode('utf-8')
        else:
            raise ContractError('Studio source must be .zip or .jsonnet')
    except (zipfile.BadZipFile, UnicodeError, RuntimeError, NotImplementedError) as error:
        raise ContractError('invalid Studio export: ' + str(error)) from error
    if sum(len(v.encode()) for v in contents.values()) > MAX_BYTES:
        raise ContractError('Studio export exceeds size limit')
    return contents


def fields(value, allowed, required, label):
    if not isinstance(value, dict):
        raise ContractError(label + ' must be an object')
    unknown, missing = set(value) - set(allowed), set(required) - set(value)
    if unknown or missing:
        raise ContractError(f'unsupported/missing {label} fields: unknown={sorted(unknown)}, missing={sorted(missing)}')


def names(mapping, label):
    if not isinstance(mapping, dict) or any(not NAME.fullmatch(key) for key in mapping):
        raise ContractError(label + ' names must be lowercase alphanumeric, starting with a letter, max 20 characters')


def network(value, label):
    fields(value, {'vcn', 'subnets'}, {'vcn'}, label)
    if not isinstance(value['vcn'], str):
        raise ContractError(label + '.vcn must be a CIDR string')
    if 'subnets' in value and (not isinstance(value['subnets'], dict) or
                              any(not isinstance(v, str) for v in value['subnets'].values())):
        raise ContractError(label + '.subnets must map roles to CIDR strings')


def platforms(value, label):
    names(value, label)
    for key, item in value.items():
        fields(item, {'network'}, {'network'}, label + '.' + key + ' (workload extensions unsupported)')
        network(item['network'], label + '.' + key + '.network')


def supported(config):
    keys = {'realm', 'region', 'region_short_name', 'cis_level', 'hub',
            'environments', 'shared_platforms', 'security_targets'}
    fields(config, keys, keys - {'security_targets'}, 'Studio config')
    if config['realm'] != 'oc1':
        raise ContractError('unsupported realm: initial Studio import requires oc1')
    if type(config['cis_level']) is not int or config['cis_level'] != 1:
        raise ContractError('unsupported cis_level: initial Studio import requires CIS1')
    if config.get('security_targets', []) != []:
        raise ContractError('unsupported security_targets: environment Security Zones need lifecycle validation')
    if not isinstance(config['region'], str) or not re.fullmatch(r'[a-z]{2}-[a-z]+-\d+', config['region']):
        raise ContractError('unsupported region identifier')
    if not isinstance(config['region_short_name'], str) or not re.fullmatch(r'[a-zA-Z0-9]{1,6}', config['region_short_name']):
        raise ContractError('unsupported region_short_name')
    fields(config['hub'], {'kind', 'network'}, {'kind', 'network'}, 'hub')
    if config['hub']['kind'] != 'hub_b':
        raise ContractError('unsupported hub: initial Studio import requires Hub B')
    network(config['hub']['network'], 'hub.network')
    names(config['environments'], 'environment')
    if not config['environments']:
        raise ContractError('Studio import requires at least one environment')
    for key, env in config['environments'].items():
        fields(env, {'project_network', 'projects', 'platforms'}, {'project_network', 'projects', 'platforms'}, 'environment.' + key)
        fields(env['project_network'], {'network'}, {'network'}, 'project_network')
        network(env['project_network']['network'], 'project_network.network')
        names(env['projects'], 'project')
        if any(v != {} for v in env['projects'].values()):
            raise ContractError('unsupported project options: Studio project declarations must be empty objects')
        platforms(env['platforms'], 'platform')
    platforms(config['shared_platforms'], 'shared_platform')


def verify_snapshots(contents, upstream, directory, require_complete):
    source = Path(directory) / 'config.jsonnet'
    expected = json.loads(run(['jsonnet', '--tla-code-file', 'config=' + str(source),
                              str(Path(upstream) / 'gen/landing_zone_multi.jsonnet')], timeout=30))
    actual = {k: v for k, v in contents.items() if k.endswith('.json')}
    if require_complete or actual:
        if set(actual) != set(expected):
            raise ContractError(f'Studio snapshot file set differs from pinned generator: missing={sorted(set(expected)-set(actual))}, unexpected={sorted(set(actual)-set(expected))}')
        for name, text in actual.items():
            path = Path(directory) / name
            path.write_text(text)
            if read_json(path) != expected[name]:
                raise ContractError('Studio snapshot differs from pinned generator: ' + name)
    return bool(actual), expected


def import_studio(args):
    if not NAME.fullmatch(args.landing_zone_environment):
        raise ContractError('landing-zone-environment must be lowercase alphanumeric, max 20 characters')
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', args.notification_email):
        raise ContractError('notification-email must be an explicit valid email address')
    output = Path(args.output).resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ContractError('import into an empty directory; never overwrite a previous design')
    upstream = Path(args.upstream) if args.upstream else locked_checkout('operating_entities', ROOT / '.cache')
    lock = read_json(ROOT / 'upstream.lock.json')
    expected_sha = lock['sources']['operating_entities']['commit']
    if run(['git', '-C', str(upstream), 'rev-parse', 'HEAD']).strip() != expected_sha:
        raise ContractError('Studio import upstream does not match lock')
    if run(['git', '-C', str(upstream), 'status', '--porcelain']).strip():
        raise ContractError('Studio import requires an unmodified upstream checkout')
    regions, configs, originals, evidence = {}, {}, {}, []
    for source in args.source:
        contents = read_export(source)
        with tempfile.TemporaryDirectory() as directory:
            config = literal_config(contents['config.jsonnet'], directory)
            supported(config)
            verified, _ = verify_snapshots(contents, upstream, directory, Path(source).suffix.lower() == '.zip')
        region = config['region']
        if region in configs:
            raise ContractError('duplicate Studio region: ' + region)
        configs[region], originals[region] = config, contents
        regions[region] = {
            'short_name': config['region_short_name'], 'hub': config['hub']['network']['vcn'],
            'shared_platforms': {p: v['network'] for p, v in config['shared_platforms'].items()},
            'environments': {env: {'network': value['project_network']['network']['vcn'],
                'platforms': {p: v['network'] for p, v in value['platforms'].items()}}
                for env, value in config['environments'].items()},
        }
        evidence.append({'region': region, 'source_name': Path(source).name,
            'source_sha256': hashlib.sha256(Path(source).read_bytes()).hexdigest(),
            'config_sha256': hashlib.sha256(contents['config.jsonnet'].encode()).hexdigest(),
            'snapshots_verified': verified,
            'artifact_sha256': {k: hashlib.sha256(v.encode()).hexdigest() for k, v in sorted(contents.items())}})
    if args.home_region not in configs:
        raise ContractError('a Studio export for the home region is required')
    projects = {env: value['projects'] for env, value in configs[args.home_region]['environments'].items()}
    model = {'home_region': args.home_region, 'landing_zone_environment': args.landing_zone_environment,
             'notification_email': args.notification_email, 'projects': projects,
             'regions': regions, 'studio_configs': configs}
    with tempfile.TemporaryDirectory() as directory:
        model_path = Path(directory) / 'model.jsonnet'
        write_json(model_path, model)
        _, documents = evaluate(model_path, upstream)
    provenance = lock | {'studio_import': {'format_version': 1, 'sources': sorted(evidence, key=lambda v: v['region'])}}
    catalog, count = write_generation(model, documents, output, provenance)
    write_json(output / 'model.jsonnet', model)
    for region, contents in originals.items():
        for name, text in contents.items():
            path = output / 'studio-source' / region / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    (output / 'studio-import-report.md').write_text(report(catalog, evidence))
    return catalog, count


def report(catalog, evidence):
    rows = '\n'.join(f"| {v['region']} | {v['source_name']} | {'Verified' if v['snapshots_verified'] else 'Source only; regenerated'} |" for v in sorted(evidence, key=lambda v: v['region']))
    return f'''# Studio import review

Imported {len(catalog['stacks'])} operation states. Home region: {catalog['home_region']}.
Original sources and exports are in studio-source/; hashes are in provenance.json.
model.jsonnet preserves the original config objects and can regenerate this set.

| Region | Source | Exported JSON evidence |
| --- | --- | --- |
{rows}

## Preserved design choices

- Hub B, CIS1, oc1; explicit VCN/subnet allocations and project NSGs.
- Original Studio network definitions, including example LB/Bastion content.
  Review those examples and their real endpoint values before deployment.
- Unsupported hubs, CIS levels, environment Security Zones and workload
  extensions cause import failure; they are never downgraded or dropped.

## Reference operation adjustments to review

- IAM/global governance is consolidated in OP00 in the home region.
- Each spoke/platform owns its attachment; hub owns DRG routing and firewall.
  Exact attachment matches are bound for hub completion in the same hub state.
- Platform networks move to their platform compartments; monitoring/scanning
  are projected into the owning operations. This changes resource placement.
- Notification subscriptions use the explicit import email.
- Audit Service Connectors are excluded by the initial reference baseline
  because their module embeds regional IAM. This is not full CIS certification.
- Preserved project NSGs belong to OP02: adding/removing a Studio project can
  require a reviewed regional change as well as the global IAM update.

## Deployment and MCCP boundary

Run the normal prepare/plan/approval flow in a private installation. Import runs
neither Terraform nor OCI. Deployed outputs and firewall OCIDs are still required.
OCI deployment, connectivity and migration/rollback remain unvalidated here.
MCCP self-service follows the approved OP04 handoff; the current reference
handoff format is not yet a tested MCCP integration contract.
'''
