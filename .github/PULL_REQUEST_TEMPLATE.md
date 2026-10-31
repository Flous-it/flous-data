<!-- Thanks for contributing to flous-data! Please fill this in. -->

## What does this PR do?

<!-- One or two sentences. e.g. "Adds the Fineco FincoOne current account." -->

## Type of change

- [ ] 🏦 Data: new bank / account
- [ ] 🐞 Data: correction to existing data
- [ ] 🧩 New feature in the catalog (`features.yaml`)
- [ ] 🛠️ Tooling / schema / CI
- [ ] 📖 Docs

## Source (required for data changes)

<!-- Official bank page / fee sheet (Foglio Informativo) URL the data comes from -->
- Source URL:
- Date verified (`last_updated`):

## Checklist

- [ ] `python scripts/validate.py` passes locally
- [ ] `ruff check schemas/ scripts/` and `mypy schemas/ scripts/` pass (if I touched code)
- [ ] I did **not** edit anything in `dist/` (it's generated)
- [ ] New `id`s were freshly generated and existing `id`s/`slug`s are unchanged
- [ ] Italian-facing text is in Italian; money values use a dot decimal, no symbol
- [ ] I added a line under `## [Unreleased]` in `CHANGELOG.md` (optional but appreciated)

## Notes for the reviewer

<!-- Anything that needs context, or "n/a" -->
