#!/usr/bin/env python3
"""Generate, validate and bind operation inputs. Never runs Terraform or OCI."""
import argparse
import copy
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IAM = {
    "compartments_configuration", "groups_configuration", "dynamic_groups_configuration",
    "policies_configuration", "identity_domains_configuration",
    "identity_domain_groups_configuration", "identity_domain_dynamic_groups_configuration",
    "identity_domain_identity_providers_configuration", "identity_domain_applications_configuration",
    "tags_configuration", "budgets_configuration", "home_region_events_configuration",
    "cloud_guard_configuration", "security_zones_configuration",
}
ALLOWED = IAM | {
    "network_configuration", "nlb_configuration", "streams_configuration",
    "logging_configuration", "notifications_configuration", "events_configuration",
    "alarms_configuration", "scanning_configuration", "vaults_configuration",
    "bastions_configuration", "zpr_configuration", "object_storage_configuration",
    "instances_configuration", "storage_configuration", "oke_clusters_configuration",
    "oke_workers_configuration", "ocvs_configuration", "cloud_exadata_database_configuration",
    "autonomous_databases_configuration", "autonomous_recovery_service_configuration",
}


class ContractError(ValueError):
    pass


def read_json(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ContractError(f"duplicate JSON key: {key}")
            out[key] = value
        return out
    return json.loads(Path(path).read_text(), object_pairs_hook=unique)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def checked_path(root, relative):
    p = Path(relative)
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise ContractError(f"unsafe relative path: {relative}")
    target = (Path(root) / p).resolve()
    if not target.is_relative_to(Path(root).resolve()):
        raise ContractError(f"path escapes root: {relative}")
    return target


def run(args, **kwargs):
    return subprocess.check_output(args, text=True, **kwargs)


def locked_checkout(name, cache):
    source = read_json(ROOT / "upstream.lock.json")["sources"][name]
    sha = source["commit"]
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ContractError("upstream commit must be an immutable SHA")
    target = Path(cache).resolve() / f"{name}-{sha}"
    if not target.exists():
        target.mkdir(parents=True)
        subprocess.run(["git", "init", "--quiet", str(target)], check=True)
        subprocess.run(["git", "-C", str(target), "remote", "add", "origin", source["repository"]], check=True)
        subprocess.run(["git", "-C", str(target), "fetch", "--quiet", "--depth", "1", "origin", sha], check=True)
        subprocess.run(["git", "-C", str(target), "checkout", "--quiet", "--detach", "FETCH_HEAD"], check=True)
    if run(["git", "-C", str(target), "rev-parse", "HEAD"]).strip() != sha:
        raise ContractError(f"unexpected upstream revision: {target}")
    if run(["git", "-C", str(target), "status", "--porcelain"]).strip():
        raise ContractError(f"modified upstream checkout: {target}")
    return target


def evaluate(model_path, upstream):
    model_path = Path(model_path).resolve()
    model = json.loads(run(["jsonnet", str(model_path)]))
    result = json.loads(run([
        "jsonnet", "-J", str(ROOT / "gen"), "-J", str(Path(upstream) / "gen"),
        "--tla-code-file", f"model={model_path}", str(ROOT / "gen/main.jsonnet"),
    ]))
    return model, result


def make_catalog(model, documents):
    stacks = {}
    for file_path in sorted(documents):
        parts = Path(file_path).parts
        if parts[0] == "common":
            stack_id, operation, region, environment = "common", "OP00", model["home_region"], None
            stage = "complete"
        else:
            region, environment = parts[1], parts[0].removeprefix("workload_") if parts[0].startswith("workload_") else None
            if parts[2] in {"bootstrap", "final"}:
                stack_id, operation, stage = "/".join(parts[:2]), "OP01", parts[2]
            else:
                stack_id, stage = "/".join(parts[:-1]), "complete"
                operation = "OP03" if parts[2].startswith("platform_") else "OP02"
        reviewer = {"OP00": "iam-governance", "OP01": "network-security", "OP02": f"environment-{environment}", "OP03": "platform-operations"}[operation]
        role = {"OP00": "global-iam", "OP01": "shared-network-security", "OP02": "environment-network-security", "OP03": "platform-network-observability"}[operation]
        if stack_id not in stacks:
            stacks[stack_id] = {
                "id": stack_id, "operation": operation, "region": region,
                "environment": environment, "scope": "global" if operation == "OP00" else "regional",
                "writer_team": "cloud-operations", "reviewer_team": reviewer,
                "execution_role": role, "state_key": stack_id + "/terraform.tfstate",
                "state_region": region, "output_prefix": "outputs/" + stack_id,
                "configurations": {},
            }
        stacks[stack_id]["configurations"][stage] = file_path
    for stack in stacks.values():
        if stack["operation"] == "OP00":
            stack["requires"] = []
        else:
            hub = f"lze_{model['landing_zone_environment']}/{stack['region']}"
            stack["requires"] = ["common"] + ([hub] if stack["operation"] != "OP01" else [])
            if stack["operation"] == "OP03" and stack["environment"]:
                stack["requires"].append(f"workload_{stack['environment']}/{stack['region']}")
        if stack["operation"] == "OP01":
            stack["completion_requires"] = [
                s["id"] for s in stacks.values()
                if s["region"] == stack["region"] and s["operation"] in {"OP02", "OP03"}
            ]
    return {
        "format_version": 1, "iam_pattern": "consolidated", "home_region": model["home_region"],
        "regions": sorted(model["regions"]),
        "region_codes": {r: model["regions"][r]["short_name"].upper() for r in model["regions"]},
        "stacks": list(stacks.values()),
        "project_onboarding": {
            "operation": "OP04", "writer_team": "cloud-operations", "iam_stack": "common",
            "projects": model["projects"], "handoff_state": None,
        },
    }


def resource_keys(document):
    result = set()
    def visit(value, parent=None):
        if isinstance(value, dict):
            for key, child in value.items():
                if key.endswith("-KEY") and isinstance(child, dict) and parent != "inject_into_existing_drgs":
                    result.add(key)
                visit(child, key)
        elif isinstance(value, list):
            for child in value:
                visit(child, parent)
    visit(document)
    return result


def validate(catalog, documents):
    errors, owned, keys, prefixes, stack_ids = [], {}, set(), set(), set()
    if catalog.get("iam_pattern") != "consolidated":
        errors.append("this implementation requires consolidated IAM")
    for stack in catalog["stacks"]:
        sid = stack["id"]
        if sid in stack_ids:
            errors.append(f"duplicate stack: {sid}")
        stack_ids.add(sid)
        if stack["state_region"] != stack["region"]:
            errors.append(f"state region mismatch: {sid}")
        if stack["state_key"] in keys or stack["output_prefix"] in prefixes:
            errors.append(f"duplicate state key/output prefix: {sid}")
        keys.add(stack["state_key"])
        prefixes.add(stack["output_prefix"])
        if not stack["writer_team"] or not stack["reviewer_team"] or not stack["execution_role"]:
            errors.append(f"missing what/who execution boundary: {sid}")
        if stack["operation"] == "OP00" and stack["region"] != catalog["home_region"]:
            errors.append("OP00 must run in home region")
        for stage, path in stack["configurations"].items():
            checked_path(ROOT, path)
            document = documents[path]
            if not document or set(document) - ALLOWED:
                errors.append(f"empty/unknown configuration family: {path}")
            if stack["scope"] == "regional" and set(document) & IAM:
                errors.append(f"global family in regional stack: {path}")
            if "service_connectors_configuration" in document:
                errors.append(f"nested IAM needs a separate governed contract: {path}")
        canonical = documents[stack["configurations"].get("final", stack["configurations"].get("complete"))]
        for key in resource_keys(canonical):
            token = (stack["scope"] if stack["scope"] == "global" else stack["region"], key)
            if token in owned:
                errors.append(f"resource key has two owners: {key}: {owned[token]} and {sid}")
            owned[token] = sid
    by_id = {s["id"]: s for s in catalog["stacks"]}
    for stack in catalog["stacks"]:
        for dependency in stack["requires"] + stack.get("completion_requires", []):
            if dependency not in by_id:
                errors.append(f"missing dependency: {dependency}")
            elif by_id[dependency]["scope"] == "regional" and by_id[dependency]["region"] != stack["region"]:
                errors.append(f"cross-region runtime dependency: {stack['id']} -> {dependency}")
    if errors:
        raise ContractError("\n".join(errors))
    return len(owned)


def merge_documents(documents):
    def merge(left, right, path):
        if right is None:
            return copy.deepcopy(left)
        if left is None:
            return copy.deepcopy(right)
        if isinstance(left, dict) and isinstance(right, dict):
            result = copy.deepcopy(left)
            for key, value in right.items():
                result[key] = merge(result.get(key), value, path + [key])
            return result
        raise ContractError("duplicate dependency value: " + "/".join(path))
    result = {}
    for doc in documents:
        if not isinstance(doc, dict):
            raise ContractError("dependency must be an object")
        result = merge(result, doc, [])
    return result


def resolve(document, dependencies, bindings):
    if isinstance(document, dict):
        return {key: resolve(value, dependencies, bindings) for key, value in document.items()}
    if isinstance(document, list):
        return [resolve(value, dependencies, bindings) for value in document]
    if isinstance(document, str) and document.startswith("output://"):
        value = dependencies
        for key in document.removeprefix("output://").split("/"):
            if not isinstance(value, dict) or key not in value:
                raise ContractError("missing producer output: " + document)
            value = value[key]
        if not isinstance(value, str) or not value.startswith("ocid1."):
            raise ContractError("output reference must resolve to an OCID: " + document)
        return value
    if isinstance(document, str) and document.startswith("binding://"):
        key = document.removeprefix("binding://")
        value = bindings.get(key)
        if not isinstance(value, str) or not value.startswith("ocid1.privateip."):
            raise ContractError("missing/invalid private IP OCID binding: " + key)
        return value
    if isinstance(document, str) and ("OCI NFW PRIVATE IP OCID" in document or re.search(r"__[A-Z0-9_]+__", document)):
        raise ContractError("unresolved upstream placeholder")
    return document


def check_resolved_config(document, dependencies, region):
    known = resource_keys(document) | resource_keys(dependencies)
    def visit(value):
        if isinstance(value, dict):
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
        elif isinstance(value, str):
            if not value.startswith("ocid1.") and value.endswith("-KEY") and value not in known:
                raise ContractError("unresolved logical resource key: " + value)
            if value.startswith("ocid1."):
                parts = value.split(".")
                if len(parts) < 5 or (parts[3] and parts[3] != region):
                    raise ContractError("resolved configuration OCID region mismatch")
    visit(document)


def output_documents(catalog, stack, stage, output_root):
    by_id = {s["id"]: s for s in catalog["stacks"]}
    producers = list(stack["requires"])
    if stage == "final":
        producers += [stack["id"]] + stack.get("completion_requires", [])
    docs = []
    for sid in producers:
        producer = by_id[sid]
        files = ["compartments_output.json"] if producer["scope"] == "global" else ["network_output.json"]
        for name in files:
            path = checked_path(output_root, sid + "/" + name)
            if not path.is_file():
                raise ContractError(f"missing reviewed output: {path}")
            value = read_json(path)
            if producer["scope"] == "regional":
                def check_ids(item):
                    if isinstance(item, dict):
                        for key, child in item.items():
                            if key == "id" and isinstance(child, str) and child.startswith("ocid1."):
                                pieces = child.split(".")
                                if len(pieces) > 3 and pieces[3] and pieces[3] != producer["region"]:
                                    raise ContractError(f"output OCID region mismatch: {path}")
                            check_ids(child)
                    elif isinstance(item, list):
                        for child in item:
                            check_ids(child)
                check_ids(value)
            docs.append(value)
    return merge_documents(docs)


def prepare(generated, stack_id, stage, output_root, destination, runtime, bucket=None, bindings=None):
    generated = Path(generated).resolve()
    catalog = read_json(generated / "catalog.json")
    documents = {p: read_json(checked_path(generated, p)) for s in catalog["stacks"] for p in s["configurations"].values()}
    validate(catalog, documents)
    stacks = {s["id"]: s for s in catalog["stacks"]}
    if stack_id not in stacks:
        raise ContractError("unknown stack: " + stack_id)
    stack = stacks[stack_id]
    if stage not in stack["configurations"]:
        raise ContractError(f"invalid stage {stage} for {stack_id}")
    document = documents[stack["configurations"][stage]]
    dependencies = output_documents(catalog, stack, stage, output_root)
    config = resolve(document, dependencies, bindings or {})
    check_resolved_config(config, dependencies, stack["region"])
    destination = Path(destination).resolve()
    if destination == generated or destination.is_relative_to(generated):
        raise ContractError("prepared runtime directory must be separate from generated source")
    write_json(destination / "config.json", config)
    write_json(destination / "dependencies.json", dependencies)
    variables = {"region": stack["region"], "save_output": True, "output_format": "json"}
    if runtime == "cli":
        variables.update({"configuration_source": "file", "local_config_file_paths": [str(destination / "config.json")],
                          "local_dependency_file_paths": [str(destination / "dependencies.json")],
                          "output_folder_path": str(destination / "outputs")})
    elif runtime == "orm":
        if not bucket:
            raise ContractError("ORM requires a customer-controlled private configuration bucket")
        prefix = "inputs/" + stack_id + "/" + stage
        variables.update({"configuration_source": "ocibucket", "oci_configuration_bucket": bucket,
                          "oci_configuration_objects": [prefix + "/config.json"],
                          "oci_dependency_objects": [prefix + "/dependencies.json"],
                          "oci_object_prefix": stack["output_prefix"]})
        for name in ("config.json", "dependencies.json"):
            if (destination / name).stat().st_size >= 1_000_000:
                raise ContractError("facade remote content exceeds conservative 1 MB limit: " + name)
    else:
        raise ContractError("unknown runtime")
    write_json(destination / "inputs.tfvars.json", variables)
    return variables


def handoff(catalog, environment, project, region, compartments, network):
    declaration = catalog["project_onboarding"]
    if project not in declaration["projects"].get(environment, {}):
        raise ContractError("project has not been onboarded in the reviewed model")
    if region not in catalog["regions"]:
        raise ContractError("unknown handoff region")
    region_code = catalog["region_codes"].get(region)
    if not region_code:
        raise ContractError("region code must be declared in handoff catalog")
    project_key = "CMP-LZ-" + environment.upper() + "-" + project.upper() + "-KEY"
    try:
        compartment_id = compartments["compartments"][project_key]["id"]
        vcn_key = f"VCN-{region_code}-LZ-{environment.upper()}-PROJECTS-KEY"
        vcn = network["network_resources"]["vcns"][vcn_key]
    except KeyError as exc:
        raise ContractError("missing deployed handoff resource: " + str(exc)) from exc
    if not compartment_id.startswith("ocid1.compartment.") or not vcn["id"].startswith("ocid1.vcn."):
        raise ContractError("invalid handoff OCIDs")
    if vcn["id"].split(".")[3] != region:
        raise ContractError("handoff VCN region mismatch")
    subnet_map = network["network_resources"].get("subnets", {})
    subnet_ids = [s["id"] for s in subnet_map.values() if s.get("vcn_id") == vcn["id"]]
    if not subnet_ids:
        raise ContractError("handoff requires at least one deployed subnet on the assigned VCN")
    if any(not sid.startswith("ocid1.subnet.") or sid.split(".")[3] != region for sid in subnet_ids):
        raise ContractError("handoff subnet region/type mismatch")
    return {"reference_handoff_version": 1, "project": project, "environment": environment,
            "region": region, "compartment_id": compartment_id, "vcn_id": vcn["id"],
            "subnet_ids": sorted(subnet_ids), "iam_owner": "cloud-operations",
            "workload_repository": ("prod-" if environment == "prod" else "nonprod-") + project,
            "workload_state_key": f"oci/{environment}/{region}/terraform.tfstate",
            "constraints": {"may_manage_iam": False, "may_manage_hub": False}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("fetch")
    fetch.add_argument("source", choices=["operating_entities", "orchestrator"])
    fetch.add_argument("--cache", default=str(ROOT / ".cache"))
    gen = sub.add_parser("generate")
    gen.add_argument("--model", default=str(ROOT / "examples/two-region.jsonnet"))
    gen.add_argument("--output", required=True)
    gen.add_argument("--upstream")
    val = sub.add_parser("validate")
    val.add_argument("--generated", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--generated", required=True)
    prep.add_argument("--stack", required=True)
    prep.add_argument("--stage", default="complete")
    prep.add_argument("--outputs", required=True)
    prep.add_argument("--destination", required=True)
    prep.add_argument("--runtime", choices=["cli", "orm"], required=True)
    prep.add_argument("--bucket")
    prep.add_argument("--bindings")
    ho = sub.add_parser("handoff")
    ho.add_argument("--generated", required=True)
    ho.add_argument("--environment", required=True)
    ho.add_argument("--project", required=True)
    ho.add_argument("--region", required=True)
    ho.add_argument("--compartments", required=True)
    ho.add_argument("--network", required=True)
    ho.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command == "fetch":
        print(locked_checkout(args.source, args.cache))
    elif args.command == "generate":
        upstream = Path(args.upstream) if args.upstream else locked_checkout("operating_entities", ROOT / ".cache")
        expected = read_json(ROOT / "upstream.lock.json")["sources"]["operating_entities"]["commit"]
        if run(["git", "-C", str(upstream), "rev-parse", "HEAD"]).strip() != expected:
            raise ContractError("generator upstream does not match lock")
        model, documents = evaluate(args.model, upstream)
        catalog = make_catalog(model, documents)
        count = validate(catalog, documents)
        output = Path(args.output).resolve()
        if output.exists() and any(output.iterdir()):
            raise ContractError("generate into an empty directory; never retain stale operation files")
        for path, document in documents.items():
            write_json(checked_path(output, path), document)
        write_json(output / "catalog.json", catalog)
        write_json(output / "provenance.json", read_json(ROOT / "upstream.lock.json"))
        print(f"Generated {len(catalog['stacks'])} stacks, {len(documents)} configurations, {count} owned keys")
    elif args.command == "validate":
        generated = Path(args.generated)
        catalog = read_json(generated / "catalog.json")
        documents = {p: read_json(checked_path(generated, p)) for s in catalog["stacks"] for p in s["configurations"].values()}
        count = validate(catalog, documents)
        print(f"Valid operation boundaries: {len(catalog['stacks'])} stacks, {count} owned keys")
    elif args.command == "prepare":
        variables = prepare(args.generated, args.stack, args.stage, args.outputs, args.destination,
                            args.runtime, args.bucket, read_json(args.bindings) if args.bindings else {})
        print(f"Prepared {args.runtime} inputs in {args.destination}; resource region {variables['region']}")
    elif args.command == "handoff":
        catalog = read_json(Path(args.generated) / "catalog.json")
        value = handoff(catalog, args.environment, args.project, args.region,
                        read_json(args.compartments), read_json(args.network))
        write_json(args.output, value)
        print(f"Prepared reference handoff: {args.output}")


if __name__ == "__main__":
    try:
        main()
    except (ContractError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
