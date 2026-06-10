# hermes-bot-hook-orchestrator

Hook-first orchestration policy repo for Hermes multi-bot Telegram setups.

## Goal

Keep **Haku/default** free to respond in the war-room group while forcing worker bots like `security`, `dev1`, `dev2`, `qa1`, and `qa2` to be **mention-only** in group chats.

## Important reality

Hermes currently ships a generic gateway hook system, but it does **not** expose a pre-dispatch inbound message policy hook for Telegram group messages. That means a hook repo like this can define the policy cleanly, but **cannot fully enforce mention-only behavior on current Hermes builds without an upstream hook point**.

So this repo does three things:

1. defines the **policy contract**,
2. provides a **ready hook implementation** for the desired future event,
3. documents the **minimal upstream gateway extension** Hermes needs so this policy can run without local one-off hacks.

## What is included

- `hooks/telegram-mention-gate/HOOK.yaml` — hook manifest
- `hooks/telegram-mention-gate/handler.py` — mention-gate policy logic
- `hooks/telegram-mention-gate/config.example.yaml` — policy example
- `docs/upstream-hook-contract.md` — proposed Hermes hook contract
- `scripts/install_hook.sh` — installs the hook into a target Hermes profile
- `tests/test_handler.py` — unit tests for the policy logic

## Intended behavior

### default / Haku
- allow normal group processing
- orchestrator can respond without mention

### worker bots
- in groups/forum topics: only process if
  - bot is explicitly mentioned, or
  - message is a reply to that bot
- otherwise ignore the message entirely

### DMs
- always allow

## Current limitation

On current Hermes, `agent:start` hooks are **observability hooks**, not **decision hooks**. Returning `{"action": "ignore"}` from an `agent:start` hook does not stop processing.

The hook in this repo is therefore **PR-ready policy code**, but it needs Hermes to emit and honor a decision-style event such as:

- `gateway:message:preprocess`

See `docs/upstream-hook-contract.md`.

## Install into a profile

```bash
bash scripts/install_hook.sh /home/arkhi25/.hermes/profiles/dev1
```

That copies the hook into:

```bash
<profile>/hooks/telegram-mention-gate/
```

## Test the policy logic

```bash
python tests/test_handler.py
```

## Recommended rollout

1. Keep this repo as source of truth.
2. Add the tiny upstream hook point to Hermes via PR.
3. Install this hook into worker profiles only.
4. Leave `default` un-gated.
