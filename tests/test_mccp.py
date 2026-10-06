"""MCCP contracts: real upstream projection, synthetic deployed OCI evidence."""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import reference as ref
from output_fixtures import synthetic_outputs


class MCCPProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upstream = os.environ.get('OE_CHECKOUT') or ref.locked_checkout('operating_entities', ROOT / '.cache')
        cls.model, cls.documents = ref.evaluate(ROOT / 'examples/two-region.jsonnet', cls.upstream)
        cls.catalog = ref.make_catalog(cls.model, cls.documents)

    def test_project_hierarchy_and_groups_use_official_tbac(self):
        common = self.documents['common/config.json']
        root = common['compartments_configuration']['compartments']['CMP-LANDINGZONE-KEY']
        project = root['children']['CMP-LZ-PROD-KEY']['children']['CMP-LZ-PROD-PROJECTS-KEY']['children']['CMP-LZ-PROD-SHOP-KEY']
        self.assertEqual({'CMP-LZ-PROD-SHOP-' + r + '-KEY' for r in ('APP', 'DB', 'INFRA')}, set(project.get('children', {})))
        self.assertIn('tn-lzp-proj-role.proj-admin', project['defined_tags'])
        groups = common['identity_domain_groups_configuration']['groups']
        self.assertIn('GRP-LZ-PROD-SHOP-INFRA-ADMINS-KEY', groups)
        self.assertNotIn('GRP-LZ-PROD-SHOP-ADMIN-KEY', groups)
        policies = common['policies_configuration']['supplied_policies']
        self.assertNotIn('PCY-LZ-PROD-SHOP-ADMIN-KEY', policies)
        self.assertIn('PCY-LZ-PROD-PROJECTS-INFRASTRUCTURE-ADMINISTRATION-KEY', policies)
        self.assertIn('TAGNS-PROJ-ROLE-KEY', common['tags_configuration']['namespaces'])

    def test_foundation_excludes_project_nsgs_and_emits_project_seed(self):
        for stack in self.catalog['stacks']:
            for path in stack['configurations'].values():
                self.assertFalse(any(k.startswith('NSG-') and '-SHOP-' in k for k in ref.resource_keys(self.documents[path])), path)
        path = 'projects/prod-shop/eu-frankfurt-1/project-nsgs.json'
        self.assertIn(path, list(self.documents))
        self.assertIn(path, self.catalog['project_onboarding']['baselines'])
        categories = self.documents[path]['network_configuration']['network_configuration_categories']
        injected = next(iter(categories.values()))['inject_into_existing_vcns']
        vcn = injected['VCN-FRA-LZ-PROD-PROJECTS-KEY']
        self.assertEqual('binding://project-vcn-id', vcn['vcn_id'])
        self.assertEqual(3, len(vcn['network_security_groups']))
        for nsg in vcn['network_security_groups'].values():
            self.assertEqual('binding://project-infra-compartment-id', nsg['compartment_id'])

    def test_project_seed_cannot_have_a_second_foundation_owner(self):
        documents = copy.deepcopy(self.documents)
        baseline = documents['projects/prod-shop/eu-frankfurt-1/project-nsgs.json']
        nsgs = next(iter(next(iter(baseline['network_configuration']['network_configuration_categories'].values()))['inject_into_existing_vcns'].values()))['network_security_groups']
        category = next(iter(documents['workload_prod/eu-frankfurt-1/config.json']['network_configuration']['network_configuration_categories'].values()))
        next(iter(category['vcns'].values()))['network_security_groups'] = nsgs
        with self.assertRaisesRegex(ref.ContractError, 'two owners'):
            ref.validate(self.catalog, documents)

    def test_project_compartment_keys_cannot_collide_with_foundation_keys(self):
        documents = copy.deepcopy(self.documents)
        root = documents['common/config.json']['compartments_configuration']['compartments']['CMP-LANDINGZONE-KEY']
        project = root['children']['CMP-LZ-PROD-KEY']['children']['CMP-LZ-PROD-PROJECTS-KEY']['children']['CMP-LZ-PROD-SHOP-KEY']
        project['children']['CMP-LZ-PROD-NETWORK-KEY'] = {'name': 'collision'}
        with self.assertRaisesRegex(ref.ContractError, 'duplicate compartment'):
            ref.validate(self.catalog, documents)

    def test_runner_policies_are_opt_in_fixed_per_environment_and_constrained(self):
        self.assertFalse(any('-GITOPS-' in key for key in self.documents['common/config.json']['policies_configuration']['supplied_policies']))
        model = copy.deepcopy(self.model)
        model['project_runner_dynamic_group'] = 'dg-mccp-platform-runner'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'model.jsonnet'
            ref.write_json(path, model)
            _, documents = ref.evaluate(path, self.upstream)
        policies = documents['common/config.json']['policies_configuration']['supplied_policies']
        self.assertEqual(6, len([key for key in policies if '-GITOPS-' in key]))
        network = policies['PCY-LZ-PROD-GITOPS-NETWORK-KEY']['statements']
        manage = [s for s in network if 'to manage vcns' in s]
        self.assertEqual(1, len(manage))
        self.assertIn("request.operation = 'CreateNetworkSecurityGroup'", manage[0])
        self.assertIn("request.operation = 'DeleteNetworkSecurityGroup'", manage[0])

    def test_retirement_preserves_foundation_and_other_environment(self):
        from onboard import remove_project
        model = remove_project(copy.deepcopy(self.model), 'dev', 'shop')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'model.jsonnet'
            ref.write_json(path, model)
            _, documents = ref.evaluate(path, self.upstream)
        self.assertNotIn('CMP-LZ-DEV-SHOP-KEY', ref.resource_keys(documents['common/config.json']))
        self.assertIn('CMP-LZ-PROD-SHOP-INFRA-KEY', ref.resource_keys(documents['common/config.json']))
        for key, value in self.documents.items():
            if key != 'common/config.json' and not key.startswith('projects/dev-shop/'):
                self.assertEqual(value, documents[key], key)
            self.assertFalse(any(key.startswith('projects/dev-shop/') for key in documents))


    def test_handoff_package_uses_schema_three_and_real_state_owners(self):
        from mccp import write_handoff, validate_handoff
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ref.write_generation(self.model, self.documents, root / 'generated', {})
            synthetic_outputs(self.catalog, self.documents, root / 'outputs')
            machine = write_handoff(root / 'generated', 'prod', 'shop', 'eu-frankfurt-1',
                root / 'outputs/common/compartments_output.json',
                root / 'outputs/workload_prod/eu-frankfurt-1/network_output.json',
                {'repository': 'example/foundation', 'workflow': 'One foundation operation', 'run': '123', 'commit': 'a' * 40}, root / 'handoff')
            self.assertEqual(3, machine['schema_version'])
            self.assertEqual('common/terraform.tfstate', machine['op04_state_key'])
            self.assertEqual('workload_prod/eu-frankfurt-1/terraform.tfstate', machine['op02_state_key'])
            self.assertEqual('prod-shop', machine['target_repository'])
            self.assertEqual('production', machine['repository_layout'])
            self.assertEqual(4, len({machine[k] for k in ('project_root_compartment', 'app_compartment', 'database_compartment', 'infrastructure_compartment')}))
            self.assertEqual({'web', 'app', 'database', 'infrastructure'}, set(machine['subnets']))
            manifest = ref.read_json(root / 'handoff/oci/prod/eu-frankfurt-1/network/project-nsgs.json')
            text = json.dumps(manifest)
            self.assertNotIn('binding://', text)
            self.assertIn(machine['infrastructure_compartment'], text)
            self.assertIn(machine['vcn'], text)
            self.assertTrue((root / 'handoff/environments/prod/environment_information.md').is_file())
            markdown = (root / 'handoff/environments/prod/environment_information.md').read_text()
            checked = validate_handoff(self.catalog, machine, markdown, 'example/foundation')
            self.assertEqual('common/terraform.tfstate', checked['op04_state_key'])
            wrong = machine | {'op04_state_key': 'op04_manage_project/prod/prod-shop/terraform.tfstate'}
            with self.assertRaisesRegex(ref.ContractError, 'state provenance'):
                validate_handoff(self.catalog, wrong, markdown, 'example/foundation')
            with self.assertRaisesRegex(ref.ContractError, 'selected installation'):
                validate_handoff(self.catalog, machine, markdown, 'other/foundation')
            with self.assertRaisesRegex(ref.ContractError, 'empty directory'):
                write_handoff(root / 'generated', 'prod', 'shop', 'eu-frankfurt-1',
                    root / 'outputs/common/compartments_output.json',
                    root / 'outputs/workload_prod/eu-frankfurt-1/network_output.json',
                    {'repository': 'example/foundation', 'workflow': 'test', 'run': '123', 'commit': 'a' * 40}, root / 'handoff')


class MCCPModelTests(unittest.TestCase):
    def test_imported_project_declaration_cannot_diverge_from_canonical_model(self):
        from mccp import validate_model
        model = {'projects': {'dev': {'billing': {}}}, 'studio_configs': {
            'eu-frankfurt-1': {'environments': {'dev': {'projects': {'shop': {}}}}}
        }}
        with self.assertRaisesRegex(ref.ContractError, 'projects differ'):
            validate_model(model)
