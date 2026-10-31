# Security Policy

`flous-data` is an open dataset and a small set of build/validate scripts. It
holds **no secrets, no personal data, and no user input** — the published
artifacts are static files served from a CDN. Still, we take a few things
seriously and welcome responsible reports.

## What counts as a security issue here

- A vulnerability in the build/validate tooling (`scripts/`, `schemas/`) or the
  CI workflows (`.github/workflows/`) — e.g. a way to inject malicious content
  into the published artifacts, or to exfiltrate the CI secrets used for
  publishing.
- A supply-chain concern in our dependencies that affects this repo.
- Exposure of a credential or secret in the repository or its history.

> Factual mistakes in the **data itself** (a wrong fee, an outdated condition)
> are **not** security issues — please open a *Data correction* issue or a PR
> instead.

## Reporting a vulnerability

Please report security issues **privately** — do not open a public issue for an
exploitable vulnerability.

1. Preferred: use GitHub's **private vulnerability reporting** on this repo
   (the *Security* tab → *Report a vulnerability*).
2. Or email **lefhim.a@gmail.com** with details and, if possible, steps to
   reproduce.

We aim to acknowledge reports within **5 business days** and to keep you updated
as we investigate and fix. Once a fix is released, we're happy to credit you
(unless you prefer to remain anonymous).

## Supported versions

Only the latest published dataset (`data.flous.it/v1/`) and the current `main`
branch are supported. There are no backports to older snapshots.
