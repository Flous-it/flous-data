# flous-data

Source-of-truth dataset for **Flous** — Italian banks and current accounts.

The data is authored as **YAML**, validated, and built into distributable
artifacts. It is distributed through **one channel only: a CDN** (Cloudflare R2,
served at `data.flous.it`). There are **no PyPI or npm packages**.

```
data/banks/*.yaml      ─┐
data/accounts/*.yaml    ├─ scripts/build.py ─► dist/flous-data.json   (→ CDN: data.flous.it/v1/dump.json)
data/features.yaml     ─┘                    ─► dist/flous.sqlite     (→ CDN: data.flous.it/v1/flous.sqlite)
                                              ─► dist/types.ts
```

## Who consumes it

- **flous-api (BE)** fetches the data from the CDN and runs the bank-comparison
  logic, exposing a REST API.
- **flous-web (FE)** calls **flous-api only** — it never reads the CDN directly.

## Commands

```bash
python3.12 -m venv .venv && pip install -e ".[dev]"

python scripts/validate.py   # validate YAML schemas + cross-references (CI)
python scripts/build.py      # build dist/ artifacts
ruff check schemas/ scripts/
mypy schemas/ scripts/
pytest
```

## Adding data

- **New bank** → `data/banks/{slug}.yaml` (see `schemas/bank.py`).
- **New account** → `data/accounts/{slug}.yaml` (see `schemas/account.py`); reference
  existing feature codes from `data/features.yaml`.
- **New feature** → add to `data/features.yaml` first, then reference it.

`dist/` is generated — never edit it by hand.

## Publishing

On push to `main`, CI builds the artifacts and uploads them to Cloudflare R2,
then pings `flous-api` to refresh. See `.github/workflows/build-publish.yml`.
Required GitHub secrets: `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ENDPOINT`,
and (optional) `FLOUS_WEBHOOK_URL` / `FLOUS_WEBHOOK_SECRET`.
