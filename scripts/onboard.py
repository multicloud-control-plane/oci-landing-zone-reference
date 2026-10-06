#!/usr/bin/env python3
"""Prepare an OP04 model change. The resulting IAM change belongs to OP00."""
import argparse
import json
from pathlib import Path
from reference import ContractError, run, write_json
from mccp import validate_project_name


def add_project(model, environment, project):
    validate_project_name(environment, project)
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


def remove_project(model, environment, project):
    """Prepare retirement; the operator first retires project workloads separately."""
    validate_project_name(environment, project)
    if project not in model['projects'].get(environment, {}):
        raise ContractError('project does not exist')
    configs = model.get('studio_configs', {})
    for region, config in configs.items():
        if project not in config['environments'].get(environment, {}).get('projects', {}):
            raise ContractError('Studio retirement project missing in region: ' + region)
    del model['projects'][environment][project]
    for config in configs.values():
        del config['environments'][environment]['projects'][project]
    return model


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("model", "environment", "project", "output"):
        p.add_argument("--" + name, required=True)
    p.add_argument('--operation', choices=['onboarding', 'retirement'], default='onboarding')
    args = p.parse_args()
    try:
        model = json.loads(run(["jsonnet", str(Path(args.model).resolve())]))
        action = remove_project if args.operation == 'retirement' else add_project
        result = action(model, args.environment, args.project)
        write_json(args.output, result)
        scope = "common IAM and project NSG seed; OP02 remains unchanged"
        print(f"OP04 change prepared: {args.output}; regenerate and review {scope}")
    except (ContractError, OSError) as exc:
        p.exit(1, f"ERROR: {exc}\n")
