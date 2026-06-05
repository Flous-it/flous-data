"""
Validate all YAML data against Pydantic schemas + cross-reference checks.
Exit 0 = all good. Exit 1 = validation errors found.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from schemas import Account, Bank, Feature  # noqa: E402


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> int:
    errors: list[str] = []

    # --- features ---
    features_raw: list[dict[str, Any]] = load_yaml(ROOT / "data" / "features.yaml")
    features: dict[str, Feature] = {}
    for raw in features_raw:
        try:
            f = Feature(**raw)
            features[f.code] = f
        except ValidationError as e:
            errors.append(f"features.yaml [{raw.get('code', '?')}]: {e}")

    # --- banks ---
    banks: dict[str, Bank] = {}
    for path in sorted((ROOT / "data" / "banks").glob("*.yaml")):
        raw = load_yaml(path)
        try:
            b = Bank(**raw)
            banks[b.slug] = b
        except ValidationError as e:
            errors.append(f"{path.name}: {e}")

    # --- accounts ---
    for path in sorted((ROOT / "data" / "accounts").glob("*.yaml")):
        raw = load_yaml(path)
        try:
            acc = Account(**raw)
        except ValidationError as e:
            errors.append(f"{path.name}: {e}")
            continue

        # cross-check: bank slug must exist
        if acc.bank not in banks:
            errors.append(
                f"{path.name}: bank slug {acc.bank!r} not found in data/banks/"
            )

        # cross-check: all feature codes must exist in catalog
        for feat in acc.features:
            if feat.code not in features:
                errors.append(
                    f"{path.name}: feature code {feat.code!r} not in features.yaml"
                )
            else:
                _check_value_type_consistency(
                    path.name, feat, features[feat.code], errors
                )

    if errors:
        print(f"VALIDATION FAILED — {len(errors)} error(s):\n")
        for err in errors:
            print(f"  ✗ {err}")
        return 1

    print(
        f"OK — {len(banks)} bank(s), "
        f"{len(features)} feature(s), "
        f"accounts validated."
    )
    return 0


def _check_value_type_consistency(
    filename: str,
    feat: object,
    catalog_feature: Feature,
    errors: list[str],
) -> None:
    from schemas import ValueType

    vt = catalog_feature.value_type
    code = catalog_feature.code

    def has(field: str) -> bool:
        return getattr(feat, field, None) is not None

    mismatch: str | None = None
    if vt == ValueType.boolean and not has("value_bool"):
        mismatch = "value_type=boolean requires value_bool"
    elif vt == ValueType.money_fixed and not has("value_money"):
        mismatch = "value_type=money_fixed requires value_money"
    elif vt == ValueType.money_with_quota and not (
        has("free_quota") or has("unit_cost")
    ):
        mismatch = "value_type=money_with_quota requires free_quota or unit_cost"
    elif vt == ValueType.percentage and not has("percentage"):
        mismatch = "value_type=percentage requires percentage"
    elif vt == ValueType.text and not has("value_text"):
        mismatch = "value_type=text requires value_text"

    if mismatch:
        errors.append(f"{filename} [{code}]: {mismatch}")


if __name__ == "__main__":
    sys.exit(main())
