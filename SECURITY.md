# Security Policy

## Reporting a vulnerability

Do not publish sensitive vulnerability details in a public issue.

If GitHub Private Vulnerability Reporting is enabled for this repository, use that channel. Otherwise, contact the repository owner through a private channel already established with them.

Include:
- a concise description of the issue
- affected files or components
- reproduction steps when safe to provide
- expected versus observed behavior
- any suggested mitigation

Do not include passwords, access tokens, API keys, private keys, 2FA QR codes, recovery codes, authentication secrets, or unrelated personal data in a report.

## Secrets

Credentials must stay outside the repository. Use environment variables or GitHub encrypted secrets when project automation needs credentials.
