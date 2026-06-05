"""
Build pipeline: YAML → dist/flous.sqlite + dist/flous-data.json + dist/types.ts

Deterministic: same input YAML = same output byte-for-byte.
"""

from __future__ import annotations

import json
import sqlite3
import sys
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).parent.parent
DIST = ROOT / "dist"
sys.path.insert(0, str(ROOT))

from schemas import Account, Bank, Feature  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _dec(v: Decimal | None) -> float | None:
    return float(v) if v is not None else None


def _new_uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Load + validate
# ---------------------------------------------------------------------------

def load_data() -> tuple[list[Bank], list[Feature], list[Account]]:
    features_raw: list[dict[str, Any]] = load_yaml(ROOT / "data" / "features.yaml")
    features = [Feature(**r) for r in sorted(features_raw, key=lambda x: x["code"])]

    banks = [
        Bank(**load_yaml(p))
        for p in sorted((ROOT / "data" / "banks").glob("*.yaml"))
    ]
    banks.sort(key=lambda b: b.slug)

    accounts = [
        Account(**load_yaml(p))
        for p in sorted((ROOT / "data" / "accounts").glob("*.yaml"))
    ]
    accounts.sort(key=lambda a: a.slug)

    return banks, features, accounts


# ---------------------------------------------------------------------------
# SQLite build
# ---------------------------------------------------------------------------

DDL = """
CREATE TABLE IF NOT EXISTS banks (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    slug        TEXT NOT NULL UNIQUE,
    bic         TEXT NOT NULL,
    abi         TEXT NOT NULL,
    mec_code    TEXT NOT NULL,
    country     TEXT NOT NULL DEFAULT 'IT'
);

CREATE TABLE IF NOT EXISTS features (
    code            TEXT PRIMARY KEY,
    label_it        TEXT NOT NULL,
    category        TEXT NOT NULL,
    product_type    TEXT NOT NULL,
    value_type      TEXT NOT NULL,
    unit            TEXT,
    display_order   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
    id              TEXT PRIMARY KEY,
    bank_id         TEXT NOT NULL REFERENCES banks(id),
    name            TEXT NOT NULL,
    slug            TEXT NOT NULL UNIQUE,
    product_type    TEXT NOT NULL,
    source_url      TEXT NOT NULL,
    last_updated    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS account_features (
    id              TEXT PRIMARY KEY,
    account_id      TEXT NOT NULL REFERENCES accounts(id),
    feature_code    TEXT NOT NULL REFERENCES features(code),
    value_money     REAL,
    value_bool      INTEGER,
    value_text      TEXT,
    free_quota      INTEGER,
    unit_cost       REAL,
    percentage      REAL,
    notes           TEXT,
    effective_from  TEXT NOT NULL,
    effective_to    TEXT
);

CREATE TABLE IF NOT EXISTS feature_prices (
    id                  TEXT PRIMARY KEY,
    account_feature_id  TEXT NOT NULL REFERENCES account_features(id),
    condition_type      TEXT NOT NULL,
    condition_value     REAL,
    price_override      REAL NOT NULL,
    condition_label     TEXT NOT NULL
);
"""


def build_sqlite(
    banks: list[Bank],
    features: list[Feature],
    accounts: list[Account],
    bank_slug_to_id: dict[str, str],
    built_at: str,
) -> Path:
    out = DIST / "flous.sqlite"
    out.unlink(missing_ok=True)
    con = sqlite3.connect(str(out))
    con.executescript(DDL)

    # banks
    con.executemany(
        "INSERT INTO banks VALUES (?,?,?,?,?,?,?)",
        [(b.id, b.name, b.slug, b.bic, b.abi, b.mec_code, b.country) for b in banks],
    )

    # features (ordered by display_order for determinism)
    con.executemany(
        "INSERT INTO features VALUES (?,?,?,?,?,?,?)",
        [
            (
                f.code, f.label_it, f.category, f.product_type,
                f.value_type, f.unit, f.display_order,
            )
            for f in sorted(features, key=lambda x: x.display_order)
        ],
    )

    # accounts + account_features + feature_prices
    for acc in accounts:
        bank_id = bank_slug_to_id[acc.bank]
        con.execute(
            "INSERT INTO accounts VALUES (?,?,?,?,?,?,?)",
            (
                acc.id, bank_id, acc.name, acc.slug,
                acc.product_type, acc.source_url, acc.last_updated,
            ),
        )
        for feat in acc.features:
            af_id = _new_uuid()
            con.execute(
                "INSERT INTO account_features VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    af_id, acc.id, feat.code,
                    _dec(feat.value_money),
                    (1 if feat.value_bool else 0)
                    if feat.value_bool is not None
                    else None,
                    feat.value_text,
                    feat.free_quota,
                    _dec(feat.unit_cost),
                    _dec(feat.percentage),
                    feat.notes,
                    built_at,
                    None,  # effective_to = null = current
                ),
            )
            for cond in feat.conditions:
                con.execute(
                    "INSERT INTO feature_prices VALUES (?,?,?,?,?,?)",
                    (
                        _new_uuid(), af_id,
                        cond.condition_type,
                        _dec(cond.condition_value),
                        _dec(cond.price_override),
                        cond.condition_label,
                    ),
                )

    con.execute("PRAGMA journal_mode=DELETE")
    con.commit()
    con.close()
    return out


# ---------------------------------------------------------------------------
# JSON build
# ---------------------------------------------------------------------------

def build_json(
    banks: list[Bank],
    features: list[Feature],
    accounts: list[Account],
    bank_slug_to_id: dict[str, str],
    version: str,
    built_at: str,
) -> Path:
    def serialize_account(acc: Account) -> dict[str, Any]:
        return {
            "id": acc.id,
            "bank_id": bank_slug_to_id[acc.bank],
            "bank_slug": acc.bank,
            "name": acc.name,
            "slug": acc.slug,
            "product_type": acc.product_type,
            "source_url": acc.source_url,
            "last_updated": acc.last_updated,
            "features": [
                {
                    "feature_code": f.code,
                    "value_money": _dec(f.value_money),
                    "value_bool": f.value_bool,
                    "value_text": f.value_text,
                    "free_quota": f.free_quota,
                    "unit_cost": _dec(f.unit_cost),
                    "percentage": _dec(f.percentage),
                    "notes": f.notes,
                    "effective_from": built_at,
                    "effective_to": None,
                    "conditions": [
                        {
                            "condition_type": c.condition_type,
                            "condition_value": _dec(c.condition_value),
                            "price_override": _dec(c.price_override),
                            "condition_label": c.condition_label,
                        }
                        for c in f.conditions
                    ],
                }
                for f in acc.features
            ],
        }

    payload = {
        "version": version,
        "built_at": built_at,
        "banks": [
            {
                "id": b.id, "name": b.name, "slug": b.slug,
                "bic": b.bic, "abi": b.abi, "mec_code": b.mec_code,
                "country": b.country,
            }
            for b in banks
        ],
        "features": [
            {
                "code": f.code, "label_it": f.label_it, "category": f.category,
                "product_type": f.product_type, "value_type": f.value_type,
                "unit": f.unit, "display_order": f.display_order,
            }
            for f in sorted(features, key=lambda x: x.display_order)
        ],
        "accounts": [serialize_account(a) for a in accounts],
    }

    out = DIST / "flous-data.json"
    out.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            separators=(",", ": "),
        ),
        encoding="utf-8",
    )
    return out


# ---------------------------------------------------------------------------
# TypeScript types
# ---------------------------------------------------------------------------

TS_TYPES = """\
// Auto-generated by scripts/build.py — do not edit manually

export type ProductType = "current_account" | "deposit" | "mortgage" | "credit_card";
export type ValueType =
  | "boolean"
  | "money_fixed"
  | "money_with_quota"
  | "percentage"
  | "text";
export type Category =
  | "management"
  | "cards"
  | "operations"
  | "branch_ops"
  | "withdrawals"
  | "digital"
  | "fx"
  | "extras";
export type ConditionType =
  | "salary_credit"
  | "age_below"
  | "age_above"
  | "min_balance"
  | "min_monthly_transactions"
  | "student_status"
  | "under_30"
  | "under_35";

export interface Bank {
  id: string;
  name: string;
  slug: string;
  bic: string;
  abi: string;
  mec_code: string;
  country: string;
}

export interface Feature {
  code: string;
  label_it: string;
  category: Category;
  product_type: string;
  value_type: ValueType;
  unit: string | null;
  display_order: number;
}

export interface FeaturePrice {
  condition_type: ConditionType;
  condition_value: number | null;
  price_override: number;
  condition_label: string;
}

export interface AccountFeature {
  feature_code: string;
  value_money: number | null;
  value_bool: boolean | null;
  value_text: string | null;
  free_quota: number | null;
  unit_cost: number | null;
  percentage: number | null;
  notes: string | null;
  effective_from: string;
  effective_to: string | null;
  conditions: FeaturePrice[];
}

export interface Account {
  id: string;
  bank_id: string;
  bank_slug: string;
  name: string;
  slug: string;
  product_type: ProductType;
  source_url: string;
  last_updated: string;
  features: AccountFeature[];
}

export interface FlousDataDump {
  version: string;
  built_at: string;
  banks: Bank[];
  features: Feature[];
  accounts: Account[];
}
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    DIST.mkdir(exist_ok=True)

    # read version from pyproject.toml (simple parse, no tomllib dependency dance)
    version = "0.0.0"
    pyproject = ROOT / "pyproject.toml"
    if pyproject.exists():
        for line in pyproject.read_text().splitlines():
            if line.startswith("version"):
                version = line.split("=")[1].strip().strip('"')
                break

    built_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    print("Loading YAML data...")
    banks, features, accounts = load_data()

    bank_slug_to_id = {b.slug: b.id for b in banks}

    print(f"  {len(banks)} banks, {len(features)} features, {len(accounts)} accounts")

    print("Building SQLite...")
    sqlite_path = build_sqlite(banks, features, accounts, bank_slug_to_id, built_at)
    print(f"  → {sqlite_path.relative_to(ROOT)}")

    print("Building JSON...")
    json_path = build_json(
        banks, features, accounts, bank_slug_to_id, version, built_at
    )
    print(f"  → {json_path.relative_to(ROOT)}")

    print("Writing TypeScript types...")
    ts_path = DIST / "types.ts"
    ts_path.write_text(TS_TYPES, encoding="utf-8")
    print(f"  → {ts_path.relative_to(ROOT)}")

    print(f"\nBuild complete (v{version}, built_at={built_at})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
