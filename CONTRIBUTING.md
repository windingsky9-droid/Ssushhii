# Contributing

This repository mixes a Flask application, static publisher content, tests, deployment files, and portfolio material. Keep changes small and reviewable.

## Before opening a pull request

1. Create or use a feature branch.
2. Do not commit secrets, API keys, access tokens, payment credentials, recovery codes, or .env files.
3. Run:
~~~bash
python -m pytest -q
python -m compileall -q app.py src tests scripts
python scripts/validate_publisher_site.py
ruff check app.py src tests scripts
mypy app.py src --config-file mypy.ini
bandit -q -r app.py src scripts
pre-commit run --all-files
~~~
4. Check the visual result when changing HTML/CSS/Three.js work.
5. Include evidence in the PR: test output, screenshot, benchmark, or public URL.

## Change boundaries

- Keep external provider credentials server-side.
- Keep demo data clearly labeled.
- Prefer deterministic test fixtures.
- Do not weaken CI to make a failing change pass.
- Update documentation when a public route, environment variable, or deployment step changes.

## Review standard

A change is ready when it is understandable, testable, reversible, and passes the relevant GitHub Actions workflows.
