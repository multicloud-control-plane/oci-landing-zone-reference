#!/usr/bin/env python3
"""Compare generated input families with the locked Orchestrator facade."""
import argparse
import re
from pathlib import Path
from reference import ROOT, ContractError, checked_path, locked_checkout, read_json

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--generated", required=True)
    args = p.parse_args()
    upstream = locked_checkout("orchestrator", ROOT / ".cache")
    source = (upstream / "rms-facade/get_configurations.tf").read_text()
    accepted = set(re.findall(r"local\.merged_input_configs\.([a-z_]+)", source))
    generated = Path(args.generated)
    catalog = read_json(generated / "catalog.json")
    paths = {path for s in catalog["stacks"] for path in s["configurations"].values()}
    for path in paths:
        unsupported = set(read_json(checked_path(generated, path))) - accepted
        if unsupported:
            raise ContractError(f"unsupported facade families in {path}: {unsupported}")
    print(f"Facade family contract passed for {len(paths)} complete configuration sets")
