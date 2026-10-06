import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import reference as ref
from output_fixtures import synthetic_outputs
from onboard import add_project


class StudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upstream = os.environ.get('OE_CHECKOUT') or ref.locked_checkout('operating_entities', ROOT / '.cache')
        cls.source = (ROOT / 'tests/fixtures/studio-hub-b.jsonnet').read_text()
        cls.config = json.loads(ref.run(['jsonnet', str(ROOT / 'tests/fixtures/studio-hub-b.jsonnet')]))
        cls.snapshots = json.loads(ref.run(['jsonnet', '--tla-code-file',
            'config=' + str(ROOT / 'tests/fixtures/studio-hub-b.jsonnet'),
            str(Path(cls.upstream) / 'gen/landing_zone_multi.jsonnet')]))

    def bundle(self, path, source=None, snapshots=None, extra=None):
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('config.jsonnet', self.source if source is None else source)
            for name, body in (self.snapshots if snapshots is None else snapshots).items():
                archive.writestr(name, json.dumps(body))
            for name, body in (extra or {}).items():
                archive.writestr(name, body)

    def invoke(self, sources, output, home='eu-frankfurt-1'):
        args = [sys.executable, str(ROOT / 'scripts/reference.py'), 'import-studio',
            '--home-region', home, '--landing-zone-environment', 'shared',
            '--notification-email', 'operations@example.com', '--output', str(output),
            '--upstream', str(self.upstream)]
        for source in sources:
            args += ['--source', str(source)]
        return subprocess.run(args, capture_output=True, text=True)

    def test_zip_import_preserves_networks_nsgs_and_source_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.bundle(root / 'studio.zip')
            result = self.invoke([root / 'studio.zip'], root / 'generated')
            self.assertEqual(0, result.returncode, result.stderr)
            out = root / 'generated'
            catalog = ref.read_json(out / 'catalog.json')
            documents = ref.load_documents(out, catalog)
            self.assertEqual(5, len(catalog['stacks']))
            self.assertGreater(ref.validate(catalog, documents), 100)
            original = self.snapshots['network.json']['network_configuration']['network_configuration_categories']
            actual_vcns = {}
            for s in catalog['stacks']:
                if s['scope'] == 'regional':
                    path = s['configurations'].get('final', s['configurations'].get('complete'))
                    categories = documents[path]['network_configuration']['network_configuration_categories']
                    for category in categories.values():
                        actual_vcns.update(category['vcns'])
            project_nsgs = []
            delegated = {}
            for path in catalog['project_onboarding']['baselines']:
                for category in documents[path]['network_configuration']['network_configuration_categories'].values():
                    for key, vcn in category['inject_into_existing_vcns'].items():
                        delegated.setdefault(key, {}).update(vcn['network_security_groups'])
            for category in original.values():
                for key, vcn in category['vcns'].items():
                    with self.subTest(vcn=key):
                        self.assertEqual(vcn['cidr_blocks'], actual_vcns[key]['cidr_blocks'])
                        self.assertEqual(vcn['subnets'], actual_vcns[key]['subnets'])
                        expected = vcn.get('network_security_groups', {})
                        if key in delegated:
                            self.assertFalse(actual_vcns[key]['network_security_groups'])
                            self.assertEqual(set(expected), set(delegated[key]))
                            for nkey, nsg in expected.items():
                                self.assertEqual(nsg | {'compartment_id': 'binding://project-infra-compartment-id'}, delegated[key][nkey])
                        else:
                            self.assertEqual(expected, actual_vcns[key].get('network_security_groups', {}))
                        project_nsgs += list(vcn.get('network_security_groups', {}))
            self.assertTrue(project_nsgs)
            self.assertEqual(self.source, (out / 'studio-source/eu-frankfurt-1/config.jsonnet').read_text())
            provenance = ref.read_json(out / 'provenance.json')['studio_import']
            self.assertEqual(hashlib.sha256(self.source.encode()).hexdigest(), provenance['sources'][0]['config_sha256'])
            self.assertIn('MCCP', (out / 'studio-import-report.md').read_text())
            model, regenerated = ref.evaluate(out / 'model.jsonnet', self.upstream)
            self.assertEqual(documents, regenerated)
            self.assertEqual(self.config, model['studio_configs']['eu-frankfurt-1'])
            updated_model = add_project(copy.deepcopy(model), 'prod', 'billing')
            ref.write_json(root / 'onboarded.jsonnet', updated_model)
            _, onboarded = ref.evaluate(root / 'onboarded.jsonnet', self.upstream)
            self.assertIn('CMP-LZ-PROD-BILLING-KEY', ref.resource_keys(onboarded['common/config.json']))
            spoke_keys = ref.resource_keys(onboarded['workload_prod/eu-frankfurt-1/config.json'])
            self.assertFalse(any(k.startswith('NSG-') and 'BILLING' in k for k in spoke_keys))
            self.assertEqual(documents['workload_prod/eu-frankfurt-1/config.json'], onboarded['workload_prod/eu-frankfurt-1/config.json'])
            self.assertIn('projects/prod-billing/eu-frankfurt-1/project-nsgs.json', onboarded)
            for stack in catalog['stacks']:
                if stack['scope'] == 'regional':
                    for path in stack['configurations'].values():
                        self.assertEqual(documents[path], onboarded[path], path)
            synthetic_outputs(catalog, documents, root / 'outputs')
            for stack in catalog['stacks']:
                for stage in stack['configurations']:
                    variables = ref.prepare(out, stack['id'], stage, root / 'outputs',
                        root / 'runtime' / stack['id'] / stage, 'cli',
                        bindings={'firewall-private-ip-id': 'ocid1.privateip.oc1.eu-frankfurt-1.synthetic'})
                    self.assertEqual('file', variables['configuration_source'])

    def test_onboarding_updates_the_imported_design_and_project_nsgs(self):
        model = {'projects': {'prod': {'shop': {}}}, 'studio_configs': {'eu-frankfurt-1': copy.deepcopy(self.config)}}
        add_project(model, 'prod', 'billing')
        self.assertIn('billing', model['studio_configs']['eu-frankfurt-1']['environments']['prod']['projects'])

    def test_duplicate_archive_entries_are_rejected(self):
        import warnings
        with tempfile.TemporaryDirectory() as directory, warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            root = Path(directory)
            self.bundle(root / 'duplicate.zip', extra={'config.jsonnet': self.source})
            result = self.invoke([root / 'duplicate.zip'], root / 'generated')
            self.assertNotEqual(0, result.returncode)
            self.assertIn('duplicate', result.stderr)

    def test_standalone_source_preserves_original_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = self.source.replace('\n', '\r\n').encode()
            (root / 'config.jsonnet').write_bytes(data)
            result = self.invoke([root / 'config.jsonnet'], root / 'generated')
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(data, (root / 'generated/studio-source/eu-frankfurt-1/config.jsonnet').read_bytes())

    def test_modified_export_snapshot_is_rejected_before_writing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshots = copy.deepcopy(self.snapshots)
            snapshots['network.json']['network_configuration']['default_compartment_id'] = 'DIFFERENT-KEY'
            self.bundle(root / 'drift.zip', snapshots=snapshots)
            result = self.invoke([root / 'drift.zip'], root / 'generated')
            self.assertNotEqual(0, result.returncode)
            self.assertIn('snapshot differs', result.stderr)
            self.assertFalse((root / 'generated').exists())

    def test_incomplete_zip_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.bundle(root / 'missing.zip', snapshots={'network.json': self.snapshots['network.json']})
            result = self.invoke([root / 'missing.zip'], root / 'generated')
            self.assertNotEqual(0, result.returncode)
            self.assertIn('snapshot file set', result.stderr)

    def test_archive_traversal_is_rejected_without_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.bundle(root / 'unsafe.zip', extra={'../escaped.json': '{}'})
            result = self.invoke([root / 'unsafe.zip'], root / 'generated')
            self.assertNotEqual(0, result.returncode)
            self.assertIn('archive entry', result.stderr)
            self.assertFalse((root.parent / 'escaped.json').exists())

    def test_unsupported_choices_are_rejected_explicitly(self):
        cases = [('cis_level', 2), ('realm', 'oc19'), ('security_targets', ['prod']),
                 ('unknown_choice', True)]
        for field, value in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                config = copy.deepcopy(self.config)
                config[field] = value
                ref.write_json(root / 'config.jsonnet', config)
                result = self.invoke([root / 'config.jsonnet'], root / 'generated')
                self.assertNotEqual(0, result.returncode)
                self.assertIn(field, result.stderr)
                self.assertFalse((root / 'generated').exists())

    def test_other_hub_and_workload_extensions_are_rejected(self):
        for mode in ('hub', 'extension'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                config = copy.deepcopy(self.config)
                if mode == 'hub':
                    config['hub']['kind'] = 'hub_a'
                else:
                    config['environments']['prod']['platforms']['data']['extension'] = {'type': 'oke_simple'}
                ref.write_json(root / 'config.jsonnet', config)
                result = self.invoke([root / 'config.jsonnet'], root / 'generated')
                self.assertNotEqual(0, result.returncode)
                self.assertIn('unsupported', result.stderr)

    def test_source_imports_cannot_read_local_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'config.jsonnet').write_text('importstr "/etc/passwd"')
            result = self.invoke([root / 'config.jsonnet'], root / 'generated')
            self.assertNotEqual(0, result.returncode)
            self.assertIn('literal', result.stderr)
            self.assertNotIn('root:', result.stdout + result.stderr)

    def test_two_regions_share_global_iam_but_have_independent_states(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'fra.jsonnet').write_text(self.source)
            ams = copy.deepcopy(self.config)
            ams.update(region='eu-amsterdam-1', region_short_name='ams')
            ref.write_json(root / 'ams.jsonnet', ams)
            result = self.invoke([root / 'fra.jsonnet', root / 'ams.jsonnet'], root / 'generated')
            self.assertEqual(0, result.returncode, result.stderr)
            catalog = ref.read_json(root / 'generated/catalog.json')
            self.assertEqual(9, len(catalog['stacks']))
            self.assertEqual(1, sum(s['scope'] == 'global' for s in catalog['stacks']))
            self.assertEqual({'eu-frankfurt-1', 'eu-amsterdam-1'}, set(catalog['regions']))

    def test_home_region_export_is_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'fra.jsonnet').write_text(self.source)
            result = self.invoke([root / 'fra.jsonnet'], root / 'generated', home='eu-amsterdam-1')
            self.assertNotEqual(0, result.returncode)
            self.assertIn('home region', result.stderr)


if __name__ == '__main__':
    unittest.main()
