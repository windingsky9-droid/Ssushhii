# Contributing

Thanks for helping improve Market Observatory. Small, understandable changes are easiest to review and maintain.

## Before you start

- Search existing issues and pull requests so related work stays together.
- For a larger change, open an issue first to agree on the behavior and boundaries.
- Do not include API keys, payment links that are meant to stay private, customer records, or other secrets in issues, commits, screenshots, or tests.

## Local setup

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Activate the virtual environment, then start the app with `python app.py`.

## Checks

Before opening a pull request, run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall app.py src
```

The CI workflow runs these checks for pull requests and pushes to `main`.

## Pull requests

1. Use a short branch name that describes the change.
2. Keep the diff focused and explain the user-visible or maintenance benefit.
3. Add or update tests when behavior changes.
4. Update docs when setup, configuration, or behavior changes.
5. Confirm generated files and local secrets are not included.
6. In the PR description, state what you changed, how you checked it, and anything a reviewer should know.

## Project boundaries

- Keep Factor Weave credentials on the server.
- Preserve demo mode as a working path without paid services or credentials.
- Keep payment actions disabled unless the intended hosted Payment Links are configured.
- Describe market outputs as research context, not financial advice or guaranteed results.
- Keep public demos free of private prospect details and customer data.

See [SECURITY.md](SECURITY.md) for vulnerability reporting guidance.
