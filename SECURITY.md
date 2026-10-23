# Security policy

## Reporting a vulnerability

Please do not report security vulnerabilities in a public issue or pull request.

If GitHub's private vulnerability reporting is enabled for this repository, use **Security → Advisories → Report a vulnerability** to send the report privately. Include the affected file or endpoint, steps to reproduce, and potential impact. Redact credentials, tokens, and private user data.

If private reporting is unavailable, contact the repository owner through the contact method listed on the GitHub profile and ask for a private security-reporting channel. Do not attach working credentials or other people's personal information.

## Scope and response

This is a small, evolving MVP. There is no guaranteed response or remediation time. Reports are reviewed as capacity allows. Please avoid testing against systems or accounts you do not own or have permission to assess.

## Handling secrets

Never commit API keys, payment credentials, access tokens, or production customer data. If a secret is exposed, revoke or rotate it immediately; deleting it from a later commit does not make the credential safe again.
