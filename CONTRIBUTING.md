# Contributing

## Purpose

This repo exists to keep Telegram multi-bot orchestration policy clean, reusable, and portable across different Hermes installs.

## Contribution rules

- Keep policy logic generic and profile-local when possible.
- Do not hardcode private bot tokens, chat IDs, or secrets.
- Prefer hook-based and contract-based designs over adapter-specific hacks.
- If Hermes core changes are required, document them in `docs/` first.
- Keep examples small and testable.
- Prefer config-driven selectors (profile names, bot usernames) over one-off local naming assumptions.

## Expected workflow

1. Update docs first when proposing a new hook contract.
2. Update hook code second.
3. Add or adjust tests.
4. Verify with `python tests/test_handler.py`.
5. If installer behavior changes, test `scripts/install_hook.sh` against a temp directory.

## Repo conventions

- `hooks/` contains installable hook packages.
- `docs/` contains design notes, issue drafts, and upstream PR plans.
- `scripts/` contains convenience install/bootstrap scripts.
- `tests/` contains simple verification scripts for policy behavior.
