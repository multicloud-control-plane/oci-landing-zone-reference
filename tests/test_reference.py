import copy
import json
import os
import tempfile
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import reference as ref


class ProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        upstream = os.environ.get("OE_CHECKOUT")
        if not upstream:
            upstream = ref.locked_checkout("operating_entities", ROOT / ".cache")
        cls.model, cls.documents = ref.evaluate(ROOT / "examples/two-region.jsonnet", upstream)
        cls.catalog = ref.make_catalog(cls.model, cls.documents)

    def test_global_and_regional_boundaries(self):
        self.assertEqual(11, len(self.catalog["stacks"]))
        self.assertGreater(ref.validate(self.catalog, self.documents), 300)
        common = self.documents["common/config.json"]
        self.assertIn("compartments_configuration", common)
        self.assertIn("home_region_events_configuration", common)
        self.assertNotIn("network_configuration", common)
        for path, document in self.documents.items():
            if path != "common/config.json":
                self.assertFalse(set(document) & ref.IAM, path)

    def test_production_and_development_have_separate_state(self):
        states = {s["id"]: s["state_key"] for s in self.catalog["stacks"]}
        self.assertNotEqual(states["workload_prod/eu-frankfurt-1"], states["workload_dev/eu-frankfurt-1"])
        for stack in self.catalog["stacks"]:
            self.assertEqual(stack["region"], stack["state_region"])

    def test_spoke_and_platform_own_their_attachments(self):
        region = "eu-frankfurt-1"
        hub = self.documents[f"lze_shared/{region}/bootstrap/config.json"]
        drg = hub["network_configuration"]["network_configuration_categories"]["0-shared"]["non_vcn_specific_gateways"]["dynamic_routing_gateways"]["DRG-FRA-LZ-HUB-KEY"]
        self.assertEqual(["DRGATT-FRA-LZ-HUB-VCN-KEY"], list(drg["drg_attachments"]))
        self.assertTrue(all(not d["statements"] for d in drg["drg_route_distributions"].values()))
        spoke = self.documents[f"workload_prod/{region}/config.json"]
        category = next(iter(spoke["network_configuration"]["network_configuration_categories"].values()))
        injected = category["non_vcn_specific_gateways"]["inject_into_existing_drgs"]["DRG-FRA-LZ-HUB-KEY"]
        attachment = next(iter(injected["drg_attachments"].values()))
        self.assertIsNone(attachment["drg_route_table_key"])
        self.assertTrue(attachment["drg_route_table_id"].startswith("output://"))

    def test_hub_completion_preserves_exact_routing_match(self):
        final = self.documents["lze_shared/eu-frankfurt-1/final/config.json"]
        drg = final["network_configuration"]["network_configuration_categories"]["0-shared"]["non_vcn_specific_gateways"]["dynamic_routing_gateways"]["DRG-FRA-LZ-HUB-KEY"]
        statements = next(iter(drg["drg_route_distributions"].values()))["statements"]
        self.assertEqual(4, len(statements))
        for statement in statements.values():
            criteria = statement["match_criteria"]
            self.assertEqual("DRG_ATTACHMENT_ID", criteria["match_type"])
            self.assertTrue(criteria["drg_attachment_id"].startswith("output://"))

    def test_platform_observability_is_local_to_its_operation(self):
        document = self.documents["workload_prod/eu-frankfurt-1/platform_data/config.json"]
        self.assertTrue(document["alarms_configuration"]["alarms"])
        self.assertTrue(document["logging_configuration"]["flow_logs"])
        self.assertTrue(document["notifications_configuration"]["topics"])
        for alarm in document["alarms_configuration"]["alarms"].values():
            self.assertEqual("CMP-LZ-PROD-DATA-KEY", alarm["supplied_alarm"]["metric_compartment_id"])

    def test_default_hub_removes_public_lb_and_example_bastion_source(self):
        for stage in ("bootstrap", "final"):
            document = self.documents[f"lze_shared/eu-frankfurt-1/{stage}/config.json"]
            vcns = document["network_configuration"]["network_configuration_categories"]["0-shared"]["vcns"]
            for vcn in vcns.values():
                self.assertFalse(vcn["load_balancers"])
                for sl in vcn["security_lists"].values():
                    self.assertFalse(any(r["description"].startswith("EXAMPLE: Allow inbound traffic from the Bastion") for r in sl["ingress_rules"]))

    def test_cross_region_dependency_is_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        stack = next(s for s in catalog["stacks"] if s["id"] == "workload_prod/eu-amsterdam-1")
        stack["requires"].append("lze_shared/eu-frankfurt-1")
        with self.assertRaisesRegex(ref.ContractError, "cross-region"):
            ref.validate(catalog, self.documents)

    def test_regional_iam_is_rejected(self):
        documents = copy.deepcopy(self.documents)
        documents["workload_prod/eu-frankfurt-1/config.json"]["policies_configuration"] = {}
        with self.assertRaisesRegex(ref.ContractError, "global family"):
            ref.validate(self.catalog, documents)

    def test_resource_with_two_owners_is_rejected(self):
        documents = copy.deepcopy(self.documents)
        documents["workload_dev/eu-frankfurt-1/config.json"]["network_configuration"] = copy.deepcopy(documents["workload_prod/eu-frankfurt-1/config.json"]["network_configuration"])
        with self.assertRaisesRegex(ref.ContractError, "two owners"):
            ref.validate(self.catalog, documents)

    def test_wrong_state_region_is_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["stacks"][0]["state_region"] = "wrong-region"
        with self.assertRaisesRegex(ref.ContractError, "state region"):
            ref.validate(catalog, self.documents)

    def test_onboarding_updates_only_global_iam(self):
        with tempfile.TemporaryDirectory() as directory:
            model = copy.deepcopy(self.model)
            model["projects"]["dev"]["billing"] = {}
            path = Path(directory) / "model.json"
            path.write_text(json.dumps(model))
            upstream = os.environ.get("OE_CHECKOUT") or ref.locked_checkout("operating_entities", ROOT / ".cache")
            _, documents = ref.evaluate(path, upstream)
            self.assertNotEqual(self.documents["common/config.json"], documents["common/config.json"])
            for key in self.documents:
                if key != "common/config.json":
                    self.assertEqual(self.documents[key], documents[key], key)

    def fake_outputs(self, directory):
        common_keys = [key for key in ref.resource_keys(self.documents["common/config.json"]) if key.startswith("CMP-")]
        ref.write_json(Path(directory) / "common/compartments_output.json", {
            "compartments": {key: {"id": "ocid1.compartment.oc1.." + key} for key in common_keys},
        })
        for stack in self.catalog["stacks"]:
            if stack["scope"] == "global":
                continue
            config = self.documents[stack["configurations"].get("bootstrap", stack["configurations"].get("complete"))]
            resources = {"vcns": {}, "subnets": {}, "dynamic_routing_gateways": {}, "drg_route_tables": {}, "drg_attachments": {}}
            def oid(kind, key):
                return f"ocid1.{kind}.oc1.{stack['region']}.{key}"
            for category in config["network_configuration"]["network_configuration_categories"].values():
                for key, vcn in category["vcns"].items():
                    resources["vcns"][key] = {"id": oid("vcn", key)}
                    for skey in vcn.get("subnets", {}):
                        resources["subnets"][skey] = {"id": oid("subnet", skey), "vcn_id": oid("vcn", key)}
                gateways = category.get("non_vcn_specific_gateways", {})
                for field in ("dynamic_routing_gateways", "inject_into_existing_drgs"):
                    for key, drg in gateways.get(field, {}).items():
                        if field == "dynamic_routing_gateways":
                            resources["dynamic_routing_gateways"][key] = {"id": oid("drg", key)}
                        for rkey in drg.get("drg_route_tables", {}):
                            resources["drg_route_tables"][rkey] = {"id": oid("drgroutetable", rkey)}
                        for akey in drg.get("drg_attachments", {}):
                            resources["drg_attachments"][akey] = {"id": oid("drgattachment", akey)}
            ref.write_json(Path(directory) / stack["id"] / "network_output.json", {"network_resources": resources})

    def test_all_runtime_configurations_bind_with_deployed_output_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generated = root / "generated"
            ref.write_json(generated / "catalog.json", self.catalog)
            for path, doc in self.documents.items():
                ref.write_json(generated / path, doc)
            self.fake_outputs(root / "outputs")
            for stack in self.catalog["stacks"]:
                for stage in stack["configurations"]:
                    with self.subTest(stack=stack["id"], stage=stage):
                        dest = root / "runtime" / stack["id"] / stage
                        variables = ref.prepare(generated, stack["id"], stage, root / "outputs", dest, "cli",
                                                bindings={"firewall-private-ip-id": f"ocid1.privateip.oc1.{stack['region']}.test"})
                        self.assertEqual("file", variables["configuration_source"])
                        resolved = (dest / "config.json").read_text()
                        self.assertNotIn("output://", resolved)
                        self.assertNotIn("binding://", resolved)

    def test_orm_prepares_private_bucket_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ref.write_json(root / "generated/catalog.json", self.catalog)
            for path, doc in self.documents.items():
                ref.write_json(root / "generated" / path, doc)
            self.fake_outputs(root / "outputs")
            variables = ref.prepare(root / "generated", "workload_prod/eu-frankfurt-1", "complete",
                                    root / "outputs", root / "runtime", "orm", bucket="private-configs")
            self.assertEqual("ocibucket", variables["configuration_source"])
            self.assertEqual("private-configs", variables["oci_configuration_bucket"])
            self.assertEqual(1, len(variables["oci_dependency_objects"]))


class DependencyTests(unittest.TestCase):
    def test_resolved_configuration_rejects_unknown_key_and_wrong_region(self):
        with self.assertRaisesRegex(ref.ContractError, "logical resource key"):
            ref.check_resolved_config({"compartment_id": "UNKNOWN-KEY"}, {}, "eu-frankfurt-1")
        with self.assertRaisesRegex(ref.ContractError, "region mismatch"):
            ref.check_resolved_config({"network_entity_id": "ocid1.privateip.oc1.eu-amsterdam-1.test"}, {}, "eu-frankfurt-1")

    def test_union_of_disjoint_network_outputs(self):
        first = {"network_resources": {"vcns": {"HUB": {"id": "hub"}}, "subnets": None}}
        second = {"network_resources": {"vcns": {"SPOKE": {"id": "spoke"}}, "subnets": {"SUBNET": {"id": "subnet"}}}}
        merged = ref.merge_documents([first, second])
        self.assertEqual({"HUB", "SPOKE"}, set(merged["network_resources"]["vcns"]))
        self.assertIn("SUBNET", merged["network_resources"]["subnets"])

    def test_conflicting_and_identical_duplicate_values_are_rejected(self):
        original = {"network_resources": {"vcns": {"VCN": {"id": "one"}}}}
        for value in ("one", "two"):
            with self.subTest(value=value), self.assertRaisesRegex(ref.ContractError, "duplicate"):
                ref.merge_documents([original, {"network_resources": {"vcns": {"VCN": {"id": value}}}}])

    def test_missing_output_stops_binding(self):
        with self.assertRaisesRegex(ref.ContractError, "missing producer"):
            ref.resolve({"drg_route_table_id": "output://network_resources/drg_route_tables/RT/id"}, {}, {})

    def test_real_output_and_manual_firewall_binding(self):
        dependencies = {"network_resources": {"drg_route_tables": {"RT": {"id": "ocid1.drgroutetable.oc1.eu-frankfurt-1.test"}}}}
        document = {"route": "output://network_resources/drg_route_tables/RT/id", "firewall": "binding://firewall-private-ip-id"}
        result = ref.resolve(document, dependencies, {"firewall-private-ip-id": "ocid1.privateip.oc1.eu-frankfurt-1.test"})
        self.assertTrue(result["route"].startswith("ocid1.drgroutetable."))
        self.assertTrue(result["firewall"].startswith("ocid1.privateip."))

    def test_bad_firewall_binding_stops_completion(self):
        with self.assertRaisesRegex(ref.ContractError, "private IP"):
            ref.resolve("binding://firewall-private-ip-id", {}, {"firewall-private-ip-id": "0.0.0.0"})

    def test_path_escape_is_rejected(self):
        with self.assertRaisesRegex(ref.ContractError, "unsafe"):
            ref.checked_path(ROOT, "../secrets.json")

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "data.json"
            file.write_text('{"compartments":{},"compartments":{}}')
            with self.assertRaisesRegex(ref.ContractError, "duplicate JSON"):
                ref.read_json(file)


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {"regions": ["eu-frankfurt-1"], "region_codes": {"eu-frankfurt-1": "FRA"},
                        "stacks": [{"id": "common", "scope": "global", "state_key": "common/terraform.tfstate"},
                                   {"id": "workload_prod/eu-frankfurt-1", "operation": "OP02", "region": "eu-frankfurt-1", "state_key": "workload_prod/eu-frankfurt-1/terraform.tfstate"}],
                        "project_onboarding": {"iam_stack": "common", "projects": {"prod": {"shop": {}}}}}
        self.compartments = {"compartments": {"CMP-LZ-PROD-SHOP-KEY": {"id": "ocid1.compartment.oc1..project"}}}
        children = {f'CMP-LZ-PROD-SHOP-{role}-KEY': {} for role in ('APP', 'DB', 'INFRA')}
        for role in ('APP', 'DB', 'INFRA'):
            self.compartments['compartments'][f'CMP-LZ-PROD-SHOP-{role}-KEY'] = {'id': f'ocid1.compartment.oc1..{role}'}
        self.common = {'compartments_configuration': {'compartments': {'CMP-LANDINGZONE-KEY': {'children': {
            'CMP-LZ-PROD-KEY': {'children': {'CMP-LZ-PROD-PROJECTS-KEY': {'children': {'CMP-LZ-PROD-SHOP-KEY': {'children': children}}}}}
        }}}}}
        self.network = {"network_resources": {
            "vcns": {"VCN-FRA-LZ-PROD-PROJECTS-KEY": {"id": "ocid1.vcn.oc1.eu-frankfurt-1.prod"}},
            "subnets": {f'SN-FRA-LZ-PROD-{role}-KEY': {"id": f"ocid1.subnet.oc1.eu-frankfurt-1.{role.lower()}", "vcn_id": "ocid1.vcn.oc1.eu-frankfurt-1.prod"} for role in ('WEB', 'APP', 'DB', 'INFRA')},
        }}
        self.network['network_resources']['subnets']['OTHER'] = {'id': 'ocid1.subnet.oc1.eu-frankfurt-1.other', 'vcn_id': 'different'}
        self.config = {'network_configuration': {'network_configuration_categories': {'prod': {'vcns': {
            'VCN-FRA-LZ-PROD-PROJECTS-KEY': {'display_name': 'prod', 'cidr_blocks': ['10.1.0.0/21'], 'subnets': {
                f'SN-FRA-LZ-PROD-{role}-KEY': {'display_name': role, 'cidr_block': f'10.1.{i}.0/24'} for i, role in enumerate(('WEB', 'APP', 'DB', 'INFRA'))
            }}
        }}}}}
        self.source = {'repository': 'example/foundation', 'workflow': 'test', 'run': '123', 'commit': 'a' * 40}

    def invoke(self, project='shop'):
        return ref.handoff(self.catalog, 'prod', project, 'eu-frankfurt-1', self.compartments, self.network, self.common, self.config, self.source)

    def test_project_handoff_contains_only_assigned_network(self):
        value = self.invoke()
        self.assertNotIn('ocid1.subnet.oc1.eu-frankfurt-1.other', value['subnets'].values())
        self.assertEqual(3, value['schema_version'])
        self.assertEqual("prod-shop", value["target_repository"])
        self.assertNotIn("credential", json.dumps(value).lower())

    def test_unknown_project_cannot_receive_a_handoff(self):
        with self.assertRaisesRegex(ref.ContractError, "not been onboarded"):
            self.invoke('other')

    def test_vcn_from_other_region_cannot_receive_a_handoff(self):
        self.network["network_resources"]["vcns"]["VCN-FRA-LZ-PROD-PROJECTS-KEY"]["id"] = "ocid1.vcn.oc1.eu-amsterdam-1.wrong"
        with self.assertRaisesRegex(ref.ContractError, "region mismatch"):
            self.invoke()

    def test_missing_child_output_and_aliased_targets_are_rejected(self):
        original = copy.deepcopy(self.compartments)
        del self.compartments['compartments']['CMP-LZ-PROD-SHOP-DB-KEY']
        with self.assertRaisesRegex(ref.ContractError, 'missing/invalid'):
            self.invoke()
        self.compartments = original
        self.compartments['compartments']['CMP-LZ-PROD-SHOP-DB-KEY']['id'] = self.compartments['compartments']['CMP-LZ-PROD-SHOP-APP-KEY']['id']
        with self.assertRaisesRegex(ref.ContractError, 'distinct'):
            self.invoke()

    def test_incomplete_or_wrong_vcn_subnets_are_rejected(self):
        key = 'SN-FRA-LZ-PROD-APP-KEY'
        original = self.network['network_resources']['subnets'].pop(key)
        with self.assertRaisesRegex(ref.ContractError, 'missing/invalid'):
            self.invoke()
        self.network['network_resources']['subnets'][key] = original | {'vcn_id': 'different'}
        with self.assertRaisesRegex(ref.ContractError, 'region/VCN'):
            self.invoke()

    def test_handoff_requires_exact_deployment_provenance(self):
        self.source['commit'] = 'main'
        with self.assertRaisesRegex(ref.ContractError, 'provenance'):
            self.invoke()


if __name__ == "__main__":
    unittest.main()
