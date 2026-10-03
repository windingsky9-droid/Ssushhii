# Workflow Map

~~~text
local idea / fix
      |
      v
feature branch or worktree
      |
      +--> python tests + compile
      |
      +--> publisher static validation
      |
      +--> Ruff + dependency audit
      |
      +--> CodeQL
      |
      v
draft pull request
      |
      v
GitHub Actions evidence
      |
      v
deploy / public verification
      |
      +--> live resource checks
      +--> security headers
      +--> sitemap / metadata
      |
      v
reviewable release candidate
~~~

## Workflow responsibilities

### Market Observatory CI
Protects the Flask application and Python runtime.

### Publisher Site CI
Checks the static publisher package for broken internal links, missing metadata, invalid public assets, and secret-like strings.

### Repository Health
Combines compile checks, tests, publisher validation, Ruff static analysis, and Python dependency auditing.

### CodeQL
Runs semantic security analysis for Python and JavaScript/TypeScript.

### Live Site Smoke
Checks the deployed public publisher daily and on relevant branch changes.

## Recovery rule

1. Preserve the last known-good state.
2. Inspect the exact failed step.
3. Fix the root cause instead of bypassing the gate.
4. Rerun only the relevant check when possible.
5. Record the working fallback when the failure came from tooling rather than code.
