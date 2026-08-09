#!/usr/bin/env python3
"""Print the checked-in historical corpus no-data preflight as readable JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rules.historical_corpus_preflight import build_no_data_preflight  # noqa: E402


MANIFEST_PATH = ROOT / "tests" / "fixtures" / "historical-acceptance" / "historical-corpus-manifest.json"


def reject_float(value: str) -> object:
    raise ValueError(f"manifest contains binary floating-point value {value}")


def main() -> int:
    with MANIFEST_PATH.open(encoding="utf-8") as handle:
        manifest = json.load(handle, parse_float=reject_float)
    report = build_no_data_preflight(manifest)
    print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
