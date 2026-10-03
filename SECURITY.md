# Security Policy

## Supported code

Security fixes are applied to the active default branch and to current feature branches that are being prepared for merge.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting / Security Advisory flow for this repository when available.

Do **not** publish passwords, API keys, access tokens, recovery codes, private URLs, payment credentials, or other secrets in a public issue.

A useful report includes:

- affected file or endpoint
- reproduction steps
- expected vs. observed behavior
- impact
- suggested mitigation, if known

## Project security principles

- secrets stay server-side and out of committed client code
- demo data is labeled and separated from live providers
- pull requests run automated tests and static validation
- the publisher site uses restrictive security headers
- dependency and CodeQL checks run in GitHub Actions
