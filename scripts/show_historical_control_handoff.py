#!/usr/bin/env python3
"""Print the synthetic metadata-only control handoff as readable JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.historical_control_handoff import build_historical_control_handoff  # noqa: E402


FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "historical-acceptance"


def reject_float(value: str) -> object:
    raise ValueError(f"fixture contains binary floating-point value {value}")


def load_json(name: str) -> dict:
    with (FIXTURE_ROOT / name).open(encoding="utf-8") as handle:
        return json.load(handle, parse_float=reject_float)


def main() -> int:
    intake_suite = load_json("historical-intake-control-cases.json")
    label_suite = load_json("historical-expected-label-control-cases.json")
    manifest_suite = load_json("historical-corpus-manifest-cases.json")
    report = build_historical_control_handoff(
        intake_suite["valid_template"],
        label_suite["valid_template"],
        manifest_suite["valid_template"],
        label_suite["evaluated_at"],
        allow_synthetic_template=True,
    )
    print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
