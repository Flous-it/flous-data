# Changelog

All notable changes to this dataset are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

Bump guidance (see [CONTRIBUTING.md](./CONTRIBUTING.md#versioning)):
**patch** = data updates · **minor** = new catalog feature · **major** = schema
change.

## [Unreleased]

### Added
- Open-source contribution infrastructure: `LICENSE` (MIT), `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `SECURITY.md`, this changelog, GitHub issue/PR templates,
  `CODEOWNERS`, and Dependabot.
- Branch protection on `main`: changes now land via Pull Request with required
  CI checks instead of direct pushes.

## [0.1.0] - 2026-06-02

### Added
- Initial dataset: 8 banks, 25 current accounts, and the feature catalog.
- YAML → `dist/` build pipeline (`flous-data.json`, `flous.sqlite`, `types.ts`).
- Validation (Pydantic schemas + cross-references), lint, and type-check.
- CI: validate on PR, build + publish to the Cloudflare R2 CDN on merge to main.

[Unreleased]: https://github.com/Flous-it/flous-data/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Flous-it/flous-data/releases/tag/v0.1.0
