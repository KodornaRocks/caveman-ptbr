#!/usr/bin/env python3
"""Locale parity verification for caveman-ptbr i18n contract (ADR-003)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = ROOT / "locales"


class CheckFailure(RuntimeError):
    pass


def section(title: str) -> None:
    print(f"\n== {title} ==")


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def load_json_strict(path: Path) -> object:
    """Load JSON and raise CheckFailure with path info on error."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise CheckFailure(f"File not found: {path}")
    except OSError as e:
        raise CheckFailure(f"Cannot read {path}: {e}")
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise CheckFailure(f"Invalid JSON in {path}: {e}")


def extract_placeholders(s: str) -> frozenset:
    """Return the set of {name} placeholders found in string s."""
    return frozenset(re.findall(r'\{(\w+)\}', s))


def get_nested(obj: dict, key: str):
    """Resolve dot-notation key into nested dict."""
    parts = key.split('.')
    current = obj
    for part in parts:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
        if current is None:
            return None
    return current


def verify_json_valid() -> tuple[dict, dict, list]:
    section("JSON Validity")

    pt_br = load_json_strict(LOCALES_DIR / "pt-br.json")
    en = load_json_strict(LOCALES_DIR / "en.json")
    required_data = load_json_strict(LOCALES_DIR / "required_keys.json")

    ensure(isinstance(pt_br, dict), "pt-br.json must be a JSON object")
    ensure(isinstance(en, dict), "en.json must be a JSON object")
    ensure(isinstance(required_data, dict), "required_keys.json must be a JSON object")
    ensure("required" in required_data, "required_keys.json must have a 'required' key")
    ensure(isinstance(required_data["required"], list), "required_keys.json 'required' must be an array")

    required_keys = required_data["required"]
    ensure(
        len(required_keys) == len(set(required_keys)),
        "required_keys.json contains duplicate keys"
    )

    print(f"JSON valid: pt-br.json, en.json, required_keys.json ({len(required_keys)} required keys)")
    return pt_br, en, required_keys


def verify_required_keys_present(pt_br: dict, en: dict, required_keys: list) -> None:
    section("Required Keys Presence")

    missing_ptbr = []
    missing_en = []

    for key in required_keys:
        if get_nested(pt_br, key) is None:
            missing_ptbr.append(key)
        if get_nested(en, key) is None:
            missing_en.append(key)

    if missing_ptbr:
        raise CheckFailure(
            f"Keys missing from pt-br.json: {', '.join(missing_ptbr)}"
        )
    if missing_en:
        raise CheckFailure(
            f"Keys missing from en.json: {', '.join(missing_en)}"
        )

    print(f"All {len(required_keys)} required keys present in both locales")


def verify_placeholder_parity(pt_br: dict, en: dict, required_keys: list) -> None:
    section("Placeholder Parity")

    mismatches = []

    for key in required_keys:
        pt_val = get_nested(pt_br, key)
        en_val = get_nested(en, key)

        # Both must exist (already checked above, but guard anyway)
        if pt_val is None or en_val is None:
            continue

        pt_placeholders = extract_placeholders(str(pt_val))
        en_placeholders = extract_placeholders(str(en_val))

        if pt_placeholders != en_placeholders:
            mismatches.append(
                f"  {key}: pt-br={sorted(pt_placeholders)} vs en={sorted(en_placeholders)}"
            )

    if mismatches:
        raise CheckFailure(
            "Placeholder mismatch between locales:\n" + "\n".join(mismatches)
        )

    print(f"Placeholders identical across {len(required_keys)} required keys in both locales")


def main() -> int:
    checks_passed = 0

    try:
        pt_br, en, required_keys = verify_json_valid()
        checks_passed += 1

        verify_required_keys_present(pt_br, en, required_keys)
        checks_passed += 1

        verify_placeholder_parity(pt_br, en, required_keys)
        checks_passed += 1

    except CheckFailure as exc:
        print(f"\nFAIL: {exc}", file=sys.stderr)
        return 1

    print(f"\nAll locale verification checks passed ({checks_passed}/3)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
