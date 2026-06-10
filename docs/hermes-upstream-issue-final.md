# Add `gateway:message:preprocess` Hook for Inbound Policy Control

## Summary

Hermes currently has a flexible gateway hook system, but it lacks a **pre-dispatch inbound message policy hook**.

This makes it difficult to implement clean profile-local behavior such as:
- one orchestrator bot (`default` / Haku) that can respond freely in Telegram groups
- multiple worker bots (`security`, `dev1`, `dev2`, `qa1`, `qa2`) that should only respond when they are **explicitly mentioned** or when the message is a **reply to the bot**

Right now, hooks like `agent:start` are too late for this use case because the message has already been accepted for processing.

---

## Problem

Current Hermes hooks are not sufficient for inbound policy control because:

- there is no generic hook event before message dispatch
- there is no supported hard-veto path for inbound messages
- there is no standard hook return contract for allow/ignore/rewrite
- policy therefore leaks into adapter logic or local source patches

This is especially painful in Telegram multi-bot group workflows where worker bots should stay quiet unless summoned.

---

## Proposed feature

Introduce a new decision-style hook event:

```text
gateway:message:preprocess
```

This event should fire:
- after the adapter has normalized inbound message context
- before session creation/selection
- before agent processing begins

---

## Proposed hook return contract

Hooks may return one of:

```python
{"action": "allow"}
{"action": "ignore", "reason": "not mentioned"}
{"action": "rewrite", "message": "..."}
```

### Semantics

- `allow` → continue normally
- `ignore` → stop processing immediately
- `rewrite` → replace inbound message text, then continue normally

### Conflict resolution

If multiple hooks return decisions:

1. any `ignore` wins
2. else last `rewrite` wins
3. else default `allow`

---

## Example use case

### Desired Telegram behavior

- `default` / Haku: respond normally in the war-room group
- worker bots: in groups/topics, only process if:
  - they are explicitly mentioned, or
  - the message is a direct reply to that bot
- worker bots: ignore plain group chatter
- DMs: remain allowed

This is not a request to hardcode Telegram-specific worker policy into Hermes core. The goal is to expose a **generic preprocess hook** so this behavior can live in profile-local hook packages.

---

## Proposed context shape

```python
{
  "platform": "telegram",
  "profile": "dev1",
  "chat_type": "dm" | "group" | "forum",
  "chat_id": "...",
  "thread_id": "...",
  "message": "raw text",
  "bot_username": "Devans1_bot",
  "is_mentioned": True | False,
  "is_reply_to_bot": True | False,
  "is_command": True | False,
  "from_user_id": "...",
}
```

Important fields:
- `profile` → enables role-based policy
- `is_mentioned` → lets hooks gate worker behavior cleanly
- `is_reply_to_bot` → supports natural reply-thread workflows

---

## Why `agent:start` is not enough

`agent:start` is an observability hook, not a dispatch policy hook.

By the time it fires:
- the adapter already accepted the message
- a session may already be selected or created
- agent work may already be starting
- there is no clean hard-veto path

---

## Minimal implementation surface

Likely touched files:

### `gateway/hooks.py`
- normalize preprocess return shapes
- resolve hook decision precedence
- document the new event

### `gateway/run.py`
- add central helper to emit preprocess hooks
- resolve final action before agent dispatch

### `gateway/platforms/telegram.py`
- compute `is_mentioned`
- compute `is_reply_to_bot`
- call preprocess hook before enqueue/dispatch

---

## Backward compatibility

This should be backward compatible because:
- existing hooks keep working unchanged
- default behavior stays `allow`
- no current platform behavior changes unless a hook opts into the new event

---

## Suggested tests

- preprocess resolution: ignore > rewrite > allow
- worker profile plain group message ignored
- worker profile explicit mention allowed
- worker profile reply-to-bot allowed
- DM allowed
- rewrite action mutates text before dispatch

---

## Why this matters

This gives Hermes a clean, reusable policy layer for:
- mention-only worker bots
- noisy-channel suppression
- role-based routing
- incident-room policies
- future cross-platform inbound gating

without forcing local source patches or platform-specific hardcoding.

---

## Reference implementation/docs

Related design repo artifacts:
- `docs/upstream-hook-contract.md`
- `docs/hermes-upstream-pr-implementation-plan.md`
- `docs/hermes-upstream-task-breakdown.md`
- `hooks/telegram-mention-gate/`
