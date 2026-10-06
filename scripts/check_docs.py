#!/usr/bin/env python3
"""Check repository-local Markdown links and JSON source syntax."""
import re
from pathlib import Path
from reference import ROOT, ContractError, read_json

count = 0
for path in ROOT.rglob("*.md"):
    if any(part in {".git", ".cache", "generated", ".runtime"} for part in path.relative_to(ROOT).parts):
        continue
    text = path.read_text()
    if sum(line.startswith("```") for line in text.splitlines()) % 2:
        raise ContractError(f"unbalanced Markdown fences: {path}")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith(("https://", "http://", "#", "mailto:")):
            continue
        if not (path.parent / target.split("#", 1)[0]).exists():
            raise ContractError(f"missing local link in {path}: {target}")
    count += 1
read_json(ROOT / "upstream.lock.json")
print(f"Documentation links/fences passed: {count} Markdown files")
