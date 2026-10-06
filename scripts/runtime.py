#!/usr/bin/env python3
"""Stage a pinned rms-facade workdir and regional backend. Does not run Terraform."""
import argparse
import json
import shutil
from pathlib import Path
from reference import ContractError, ROOT, locked_checkout, read_json, write_json


def stage_workdir(generated, stack_id, prepared, destination, bucket, namespace, tenancy):
    catalog = read_json(Path(generated) / "catalog.json")
    stack = next((s for s in catalog["stacks"] if s["id"] == stack_id), None)
    if stack is None:
        raise ContractError("unknown stack")
    inputs = read_json(Path(prepared) / "inputs.tfvars.json")
    if inputs.get("configuration_source") != "file" or inputs.get("region") != stack["region"]:
        raise ContractError("runtime inputs do not match selected CLI stack")
    if not tenancy.startswith("ocid1.tenancy.") or not bucket or not namespace:
        raise ContractError("valid tenancy, private state bucket and namespace are required")
    destination = Path(destination).resolve()
    if destination.exists():
        raise ContractError("runtime workdir must be new")
    upstream = locked_checkout("orchestrator", ROOT / ".cache")
    shutil.copytree(upstream, destination, ignore=shutil.ignore_patterns(".git"))
    # Terraform override files preserve upstream provider aliases and region logic.
    (destination / "providers_override.tf").write_text('''provider "oci" {
  auth = "InstancePrincipal"
}
provider "oci" {
  alias = "home"
  auth = "InstancePrincipal"
}
provider "oci" {
  alias = "secondary_region"
  auth = "InstancePrincipal"
}
''')
    facade = destination / "rms-facade"
    (facade / "providers_override.tf").write_text('''provider "oci" {
  auth = "InstancePrincipal"
}
''')
    (facade / "backend.tf").write_text('terraform {\n  backend "oci" {}\n}\n')
    backend = {
        "bucket": bucket, "namespace": namespace, "region": stack["state_region"],
        "key": stack["state_key"], "auth": "InstancePrincipal",
    }
    (facade / "backend.tfbackend").write_text("\n".join(f"{key} = {json.dumps(value)}" for key, value in backend.items()) + "\n")
    write_json(facade / "inputs.tfvars.json", inputs | {"tenancy_ocid": tenancy})
    return facade


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("generated", "stack", "prepared", "destination", "bucket", "namespace", "tenancy"):
        p.add_argument("--" + name, required=True)
    args = p.parse_args()
    try:
        print(stage_workdir(args.generated, args.stack, args.prepared, args.destination,
                            args.bucket, args.namespace, args.tenancy))
    except (ContractError, OSError) as exc:
        p.exit(1, f"ERROR: {exc}\n")
