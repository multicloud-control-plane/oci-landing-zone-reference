#!/usr/bin/env python3
"""Prepare an OP04 model change. The resulting IAM change belongs to OP00."""
import argparse
import json
import re
from pathlib import Path
from reference import ContractError, run, write_json


def add_project(model, environment, project):
    if not re.fullmatch(r"[a-z][a-z0-9]{0,19}", project):
        raise ContractError("project must be a lowercase alphanumeric name of at most 20 characters")
    if environment not in model["projects"]:
        raise ContractError("unknown workload environment")
    if project in model["projects"][environment]:
        raise ContractError("project already exists")
    configs = model.get("studio_configs", {})
    for region, config in configs.items():
        if environment not in config["environments"]:
            raise ContractError("Studio onboarding environment missing in region: " + region)
        if project in config["environments"][environment]["projects"]:
            raise ContractError("project already exists in Studio design: " + region)
    model["projects"][environment][project] = {}
    for config in configs.values():
        config["environments"][environment]["projects"][project] = {}
    return model


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("model", "environment", "project", "output"):
        p.add_argument("--" + name, required=True)
    args = p.parse_args()
    try:
        model = json.loads(run(["jsonnet", str(Path(args.model).resolve())]))
        result = add_project(model, args.environment, args.project)
        write_json(args.output, result)
        scope = "common IAM and affected OP02 project NSGs" if "studio_configs" in result else "common/config.json"
        print(f"OP04 change prepared: {args.output}; regenerate and review {scope}")
    except (ContractError, OSError) as exc:
        p.exit(1, f"ERROR: {exc}\n")
