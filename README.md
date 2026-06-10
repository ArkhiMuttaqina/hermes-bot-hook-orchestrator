# hermes-bot-hook-orchestrator

Hook-first orchestration policy repo for Hermes multi-bot Telegram setups.

## Goal

Keep **Haku/default** free to respond in the war-room group while forcing worker bots to be **mention-only** in group chats.

## Important reality

Hermes currently ships a generic gateway hook system, but it does **not** expose a pre-dispatch inbound message policy hook for Telegram group messages. That means a hook repo like this can define the policy cleanly, but **cannot fully enforce mention-only behavior on current Hermes builds without an upstream hook point**.

So this repo does three things:

1. defines the **policy contract**,
2. provides a **ready hook implementation** for the desired future event,
3. documents the **minimal upstream gateway extension** Hermes needs so this policy can run without local one-off hacks.

## What is included

- `hooks/telegram-mention-gate/HOOK.yaml` — hook manifest
- `hooks/telegram-mention-gate/handler.py` — universal mention-gate policy logic
- `hooks/telegram-mention-gate/config.example.yaml` — portable config example
- `docs/upstream-hook-contract.md` — proposed Hermes hook contract
- `scripts/install_hook.sh` — installs the hook into any target Hermes profile
- `tests/test_handler.py` — unit tests for the policy logic

## Universal install model

This hook is designed to work for **any Hermes install** by using configurable rules instead of hardcoded local assumptions.

It can gate bots by either:
- **Hermes profile name** via `profile_rules`, or
- **bot username** via `bot_rules`

That means the same hook package can be reused across:
- single-user setups
- multi-profile setups
- differently named worker bots
- repos that don't use `dev1/dev2/qa1/...`

## Intended behavior

### unrestricted bots
- allow normal group processing
- orchestrator can respond without mention

### mention-only bots
- in groups/forum topics: only process if
  - bot is explicitly mentioned, or
  - message is a reply to that bot
- otherwise ignore the message entirely

### DMs
- always allow by default

## Current limitation

On current Hermes, `agent:start` hooks are **observability hooks**, not **decision hooks**. Returning `{"action": "ignore"}` from an `agent:start` hook does not stop processing.

The hook in this repo is therefore **PR-ready policy code**, but it needs Hermes to emit and honor a decision-style event such as:

- `gateway:message:preprocess`

See `docs/upstream-hook-contract.md`.

## Install into any profile

```bash
bash scripts/install_hook.sh /path/to/hermes/profile/home
```

Optional custom config template:

```bash
bash scripts/install_hook.sh /path/to/hermes/profile/home /path/to/my-config.yaml
```

That copies the hook into:

```bash
<profile>/hooks/telegram-mention-gate/
```

and installs `config.yaml` for immediate editing.

## Config model

Main knobs:
- `default_action`
- `allow_in_dm`
- `allow_commands`
- `allow_replies_to_bot`
- `allow_mentions`
- `gate_forum_topics`
- `profile_rules`
- `bot_rules`

### Example idea
- set orchestrator profile to `allow_all`
- set worker profiles or bot usernames to `mention_only`
- leave unknown profiles on `allow`

## Test the policy logic

```bash
python tests/test_handler.py
```

## Test the install workflow

```bash
TMPDIR=$(mktemp -d)
bash scripts/install_hook.sh "$TMPDIR"
find "$TMPDIR" -maxdepth 3 -type f | sort
```

## Recommended rollout

1. Keep this repo as source of truth.
2. Add the tiny upstream hook point to Hermes via PR.
3. Install this hook into whichever worker profiles you want gated.
4. Leave your orchestrator unrestricted.
