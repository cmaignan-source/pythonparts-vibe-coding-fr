#!/usr/bin/env python
"""Apply .github/model-tiers.json to the `model:` line of every pp-*.agent.md.

Each tier is an ordered fallback list: VS Code tries models in order until one is available.
Optional "overrides": {agent: tier} temporarily replaces the default tier of "agents".
Usage: python tools/sync_models.py [--check]
  (no flag) rewrite the `model:` front-matter lines
  --check   only report: drift between files and config, and tier models missing from `available`
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / ".github"
MODEL_LINE = re.compile(r"^model:.*$", re.MULTILINE)


def format_models(models: list[str]) -> str:
    quoted = ", ".join(f"'{name}'" for name in models)
    return f"model: [{quoted}]"


def main() -> int:
    check_only = "--check" in sys.argv
    config = json.loads((ROOT / "model-tiers.json").read_text(encoding="utf-8"))
    available = {name.lower() for name in config.get("available", [])}
    exit_code = 0

    for tier, models in config["tiers"].items():
        unknown = [m for m in models if re.sub(r"\s*\(copilot\)$", "", m).lower() not in available]
        if available and unknown:
            print(f"[WARN] tier '{tier}': not in 'available' list -> {unknown}")
            if len(unknown) == len(models):
                print(f"[FAIL] tier '{tier}' has no available model")
                exit_code = 1

    overrides = config.get("overrides", {})
    for agent, default_tier in config["agents"].items():
        tier = overrides.get(agent, default_tier)
        if tier not in config["tiers"]:
            print(f"[FAIL] {agent}: unknown tier '{tier}'")
            exit_code = 1
            continue
        path = ROOT / "agents" / f"{agent}.agent.md"
        if not path.exists():
            print(f"[FAIL] missing {path.name}")
            exit_code = 1
            continue
        expected = format_models(config["tiers"][tier])
        text = path.read_text(encoding="utf-8")
        match = MODEL_LINE.search(text)
        current = match.group(0) if match else None
        if current == expected:
            suffix = " (override)" if agent in overrides else ""
            print(f"[ OK ] {agent:18} {tier:6} {expected}{suffix}")
            continue
        if check_only:
            print(f"[DRIFT] {agent}: {current} != {expected}")
            exit_code = 1
            continue
        new_text = MODEL_LINE.sub(expected, text, count=1) if match else text.replace("---\n", f"---\n{expected}\n", 1)
        path.write_text(new_text, encoding="utf-8", newline="")
        print(f"[SYNC] {agent:18} {tier:6} {expected}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
