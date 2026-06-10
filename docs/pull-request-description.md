# PR: Add hook-first Telegram mention-gate orchestrator scaffolding

## Summary

This PR adds the initial repository scaffolding for a **universal** hook-first Telegram multi-bot orchestration policy.

The immediate goal is to support workflows where:
- one orchestrator bot can respond freely in a war-room group
- worker bots should eventually become **mention-only** in Telegram groups/topics

This PR does **not** patch Hermes core directly. Instead, it creates a clean source-of-truth repo containing:
- the hook package prototype
- upstream contract docs
- upstream implementation plan
- issue drafts
- task breakdown
- repo bootstrap and tests

## What’s included

### Hook package
- `hooks/telegram-mention-gate/HOOK.yaml`
- `hooks/telegram-mention-gate/handler.py`
- `hooks/telegram-mention-gate/config.example.yaml`

### Docs
- `docs/upstream-hook-contract.md`
- `docs/hermes-upstream-pr-implementation-plan.md`
- `docs/hermes-upstream-issue-draft.md`
- `docs/hermes-upstream-issue-final.md`
- `docs/hermes-upstream-task-breakdown.md`

### Repo scaffolding
- `README.md`
- `.gitignore`
- `LICENSE`
- `CONTRIBUTING.md`
- `Makefile`

### Ops/test helpers
- `scripts/install_hook.sh`
- `tests/test_handler.py`

## Universalization in this PR

The hook package was refactored to be portable across any Hermes install:
- rules can match by **profile name**
- rules can match by **bot username**
- installer can copy a **custom config template**
- default config no longer assumes only one local naming scheme

## Why this PR exists

Hermes already has a hook system, but current hook events are not sufficient to enforce mention-only worker behavior before inbound Telegram messages reach the agent.

This repo prepares the policy and design work needed for a clean upstream solution, instead of relying on local source hacks.

## What this PR does *not* do

- does not modify Hermes upstream code
- does not yet enforce mention-only behavior in live Hermes builds
- does not add cross-platform gating beyond the Telegram-focused design docs

## Verification

Policy tests were run locally:

```bash
python tests/test_handler.py
```

Install workflow was also exercised against a temporary target directory.

## Merge impact

Low risk.
This PR only adds a new standalone repo structure, docs, and local policy tests.

## Suggested next step after merge

Use the included docs to open/drive the upstream Hermes feature work for:
- `gateway:message:preprocess`
- decision-style hook returns (`allow` / `ignore` / `rewrite`)
- Telegram adapter integration for mention/reply metadata
