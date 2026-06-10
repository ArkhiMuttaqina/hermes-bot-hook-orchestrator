# PR: Add hook-first Telegram mention-gate orchestrator scaffolding

## Summary

This PR adds the initial repository scaffolding for a hook-first Telegram multi-bot orchestration policy.

The immediate goal is to support a workflow where:
- `default` / Haku can respond freely in the war-room group
- worker bots (`security`, `dev1`, `dev2`, `qa1`, `qa2`) should eventually become **mention-only** in Telegram groups/topics

This PR does **not** patch Hermes core directly. Instead, it creates a clean source-of-truth repo containing:
- the hook package prototype
- upstream contract docs
- upstream implementation plan
- issue draft
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

Expected/pass cases:
- default in group → allow
- dev1 plain group text → ignore
- dev1 mention → allow
- dev1 reply → allow
- security DM → allow

## Merge impact

Low risk.
This PR only adds a new standalone repo structure, docs, and local policy tests.

## Suggested next step after merge

Use the included docs to open/drive the upstream Hermes feature work for:
- `gateway:message:preprocess`
- decision-style hook returns (`allow` / `ignore` / `rewrite`)
- Telegram adapter integration for mention/reply metadata
