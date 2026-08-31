# Contributing

## Workflow

1. Create a focused branch from `main`.
2. Keep each change small enough to review clearly.
3. Run the relevant local checks before committing.
4. Open a pull request that explains what changed and why.
5. Merge only after automated checks pass.

## Branch names

Use short descriptive prefixes such as:
- `feature/` for new behavior
- `fix/` for corrections
- `docs/` for documentation
- `chore/` for maintenance

## Validation

When Python files are present, run:
```bash
python -m compileall -q .
```

Never commit passwords, tokens, API keys, private keys, `.env` files, 2FA QR codes, recovery codes, authentication secrets, virtual environments, build output, or local caches.
