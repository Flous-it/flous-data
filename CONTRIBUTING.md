# Contributing to flous-data

First off — **thank you!** `flous-data` is an open, community-maintained dataset
of Italian banks and their financial products (current accounts today; deposits,
mortgages and cards over time). Every correction, new bank, or new account makes
the data more useful for everyone who builds on it.

You do **not** need to be a programmer to contribute. If you can read a bank's
fee sheet and edit a text file, you can help. This guide explains how.

- [Code of Conduct](#code-of-conduct)
- [Ways to contribute](#ways-to-contribute)
- [How the project works](#how-the-project-works)
- [Where the data comes from](#where-the-data-comes-from)
- [Project layout](#project-layout)
- [Local setup](#local-setup)
- [Adding or editing data](#adding-or-editing-data)
  - [Add a new bank](#add-a-new-bank)
  - [Add a new account](#add-a-new-account)
  - [Add a new feature](#add-a-new-feature)
- [Data quality standards](#data-quality-standards)
- [The contribution workflow](#the-contribution-workflow)
- [Commit & PR conventions](#commit--pr-conventions)
- [Versioning](#versioning)
- [Getting help](#getting-help)

---

## Code of Conduct

This project follows the [Contributor Covenant](./CODE_OF_CONDUCT.md). By
participating, you agree to uphold it. Report unacceptable behavior to the
contacts listed in that document.

## Ways to contribute

- 🐞 **Report incorrect data** — a fee changed, a condition is wrong, a bank
  merged. Open a *Data correction* issue (no coding needed).
- 🏦 **Add a bank or account** — submit a YAML file via Pull Request, or open a
  *New bank / account* issue with the source and we'll help.
- 🧩 **Add a feature to the catalog** — a comparable attribute not yet modelled.
- 🛠️ **Improve the tooling** — the build/validate scripts, schemas, CI, docs.
- 📖 **Improve docs** — clarify anything in this guide or the README.

Browse [open issues](https://github.com/Flous-it/flous-data/issues) — anything
labelled `good first issue` is a great place to start.

## How the project works

The single most important rule:

> **YAML in `data/` is the source of truth.** Everything in `dist/` (the
> SQLite file, JSON dump, and TypeScript types) is **generated** by
> `scripts/build.py`. Never edit `dist/` by hand — your changes would be
> overwritten on the next build, and `dist/` is git-ignored anyway.

```
data/banks/*.yaml      ─┐
data/accounts/*.yaml    ├─ scripts/build.py ─► dist/flous-data.json  (→ CDN: data.flous.it/v1/dump.json)
data/features.yaml     ─┘                    ─► dist/flous.sqlite    (→ CDN: data.flous.it/v1/flous.sqlite)
                                              ─► dist/types.ts
```

On every Pull Request, CI runs `scripts/validate.py`, `ruff`, and `mypy`. When a
PR is merged to `main`, CI rebuilds the artifacts and publishes them to the CDN
(`data.flous.it`). Consumers (such as `flous-api`) read from the CDN.

## Where the data comes from

Every account **must** cite a public, verifiable source. We only accept data
that anyone can check:

- ✅ The bank's **official website**: the product page, fee sheet
  (*Foglio Informativo*), or *Documento di Sintesi*.
- ✅ Official regulatory documents (e.g. published by the bank per Banca d'Italia
  transparency rules).
- ❌ Hearsay, screenshots without a URL, paywalled third-party comparison sites,
  or "a friend told me".

The URL goes in the account's `source_url` field, and the date you verified it
goes in `last_updated`. This keeps the dataset auditable and fixable.

## Project layout

```
flous-data/
├── data/                 # ← source of truth (edit these)
│   ├── banks/*.yaml      #   one file per bank
│   ├── accounts/*.yaml   #   one file per account/product
│   └── features.yaml     #   the catalog of comparable features
├── schemas/              # Pydantic models that define & validate the shapes
│   ├── bank.py
│   ├── account.py
│   └── feature.py
├── scripts/
│   ├── validate.py       # schema + cross-reference checks (runs in CI)
│   └── build.py          # YAML → dist/ artifacts
├── dist/                 # generated, git-ignored — DO NOT EDIT
├── tests/
└── .github/workflows/    # CI: validate on PR, build+publish on merge
```

## Local setup

You need **Python 3.12+** and `git`.

```bash
git clone https://github.com/Flous-it/flous-data.git
cd flous-data
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Verify everything works:

```bash
python scripts/validate.py    # validates all YAML + cross-references
python scripts/build.py       # builds dist/ locally (so you can inspect output)
ruff check schemas/ scripts/  # lint
mypy schemas/ scripts/        # type-check
pytest                        # tests
```

If `validate.py` prints `OK — N bank(s), M feature(s), accounts validated.`
you're good to go.

> 💡 If you only changed data, you mostly care about `validate.py`. Run it before
> every push — it catches the vast majority of mistakes.

## Adding or editing data

All three data types are plain YAML. Filenames use **kebab-case slugs** and must
match the `slug` inside the file. Every record needs a stable `id` — generate one
with:

```bash
python -c "import uuid; print(uuid.uuid4())"
```

Once created, **never change an existing `id`** — downstream consumers key off it.

### Add a new bank

Create `data/banks/<slug>.yaml` matching `schemas/bank.py`:

```yaml
id: f4ff0c48-5a31-5118-9ce2-19714832fac8   # generate with the uuid command above
name: "Bunq"                                # display name
slug: bunq                                  # kebab-case, matches the filename
bic: BUNQITM2                               # 8 or 11 chars (AAAABBCC[DDD])
abi: "03647"                                # exactly 5 digits — keep the quotes
mec_code: "03647"                           # exactly 5 digits — keep the quotes
country: IT                                 # defaults to IT
```

> ⚠️ `abi` and `mec_code` must be **5-digit strings** — always quote them so
> YAML doesn't strip a leading zero (`"03647"`, not `03647`).

### Add a new account

Create `data/accounts/<slug>.yaml` matching `schemas/account.py`:

```yaml
id: 640aa4fa-8786-52c0-a06b-2cc41c9d08e0
bank: bunq                  # must match an existing bank slug in data/banks/
name: "Bunq Free"
slug: bunq-free             # kebab-case, matches the filename
product_type: current_account   # current_account | deposit | mortgage | credit_card
source_url: https://www.bunq.com   # the official page you took the data from
last_updated: "2026-06-02"          # ISO date you verified the data

features:
  - code: monthly_fee       # must exist in data/features.yaml
    value_money: 0.00       # which value field you set depends on the feature's value_type
    notes: "Sempre gratuito"
  - code: joint_account_allowed
    value_bool: false
```

**Which value field do I set?** It depends on the feature's `value_type` in
`features.yaml` — validation enforces this match:

| Feature `value_type` | Field you populate on the account                      |
|----------------------|--------------------------------------------------------|
| `boolean`            | `value_bool: true \| false`                            |
| `money_fixed`        | `value_money: 9.90`                                     |
| `money_with_quota`   | `free_quota: 3` and/or `unit_cost: 1.50`               |
| `percentage`         | `percentage: 1.25`                                      |
| `text`               | `value_text: "..."`                                    |

You may set **only one** value field per feature (quota fields are the
exception, and they cannot be combined with `value_bool`). `notes` is always
optional and free-text (Italian).

**Conditional pricing** — when a fee changes under a condition (e.g. *free with
salary credit ≥ €1.000*), add `conditions`:

```yaml
  - code: monthly_fee
    value_money: 9.90                 # the standard price
    conditions:
      - condition_type: salary_credit # see ConditionType in schemas/account.py
        condition_value: 1000
        price_override: 0.00          # price when the condition is met
        condition_label: "Gratuito con accredito stipendio ≥ €1.000"
```

Valid `condition_type` values: `salary_credit`, `age_below`, `age_above`,
`min_balance`, `min_monthly_transactions`, `student_status`, `under_30`,
`under_35`. An account with no conditional pricing simply omits `conditions`.

### Add a new feature

Only add a feature when an existing one doesn't fit. Add it to
`data/features.yaml` **first**, then reference its `code` from accounts:

```yaml
- code: my_new_feature        # snake_case, unique, stable
  label_it: Etichetta in italiano
  category: management         # management|cards|operations|branch_ops|withdrawals|digital|fx|extras
  product_type: current_account
  value_type: money_fixed      # boolean|money_fixed|money_with_quota|percentage|text
  unit: EUR                    # optional (e.g. EUR); omit for booleans/text
  display_order: 40            # controls ordering in the comparison UI
```

Never **remove** a feature that an account still references, and never repurpose
an existing `code` to mean something different.

## Data quality standards

A data PR is ready when:

- [ ] `source_url` points to the **official** bank page and `last_updated`
      reflects when you checked it.
- [ ] Money values use a dot decimal (`9.90`, not `9,90`) and no currency symbol.
- [ ] Italian-facing text (`name`, `label_it`, `notes`, `condition_label`) is in
      **Italian** and matches how the bank describes it.
- [ ] `python scripts/validate.py` passes locally.
- [ ] You didn't touch anything in `dist/`.

## The contribution workflow

We use a **fork + Pull Request** workflow. **Direct pushes to `main` are
disabled** — all changes land through PRs that pass CI.

1. **Fork** the repo and clone your fork.
2. **Branch** off `main` with a descriptive name:
   ```bash
   git checkout -b data/add-bank-fineco
   ```
   Suggested prefixes: `data/…` (data changes), `fix/…`, `feat/…`, `docs/…`,
   `ci/…`.
3. **Make your change** and run the checks locally (`validate.py` at minimum).
4. **Commit** following the [conventions below](#commit--pr-conventions).
5. **Push** to your fork and **open a Pull Request** against `Flous-it:main`,
   filling in the PR template.
6. **CI runs** validate + lint + type-check. Green is required to merge.
7. A maintainer reviews; once approved it's merged (squash) and the data is
   published to the CDN automatically.

Keep PRs focused — one bank, one account, or one logical change per PR is much
easier to review than a giant batch.

## Commit & PR conventions

We loosely follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

type:  feat | fix | data | docs | ci | refactor | test | chore
```

Examples:

```
data: add Fineco FincoOne current account
fix(bunq-free): correct monthly_fee to 0.00
feat(schema): add product_type "deposit"
docs: clarify how conditional pricing works
```

Write commit messages and code in **English**; user-facing data stays in
Italian. Keep the summary in the imperative mood and under ~72 chars.

## Versioning

The dataset is versioned with [Semantic Versioning](https://semver.org/) via the
`version` field in `pyproject.toml`, which is embedded in the published
`dump.json` so consumers can detect changes. Notable changes are recorded in
[`CHANGELOG.md`](./CHANGELOG.md).

| Kind of change                                   | Bump      |
|--------------------------------------------------|-----------|
| Data update (fee change, new account/bank)       | **patch** |
| New feature added to the catalog                 | **minor** |
| Schema change (rename, new required field, etc.) | **major** |

Maintainers handle the version bump and changelog entry at merge/release time —
as a contributor you generally don't need to touch `pyproject.toml`, but feel
free to add a `CHANGELOG.md` line under `## [Unreleased]` describing your change.

## Getting help

- Open a [Discussion](https://github.com/Flous-it/flous-data/discussions) or an
  issue with the `question` label.
- Not sure how to model something? Open a draft PR or an issue — we'd rather help
  early than have you guess.

Thanks again for contributing to open financial data for Italy 🇮🇹
