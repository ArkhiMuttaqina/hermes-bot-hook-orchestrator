# Issue Draft: Add Pre-Dispatch Gateway Message Hook for Policy Control

## Title

Add `gateway:message:preprocess` hook so profile-local hooks can allow/ignore/rewrite inbound messages before agent dispatch

## Summary

Hermes already has a flexible gateway hook system, but it currently lacks a **pre-dispatch inbound message policy hook**. This makes it hard to implement clean profile-local policies such as:

- one orchestrator bot (`default`) that can respond freely in Telegram group chats
- worker bots (`security`, `dev1`, `dev2`, `qa1`, `qa2`) that should only respond when **explicitly mentioned** or when a message is a **reply to the bot**

Today, hook code can observe lifecycle events like `agent:start`, but that is too late for a true policy veto. By that point, the message has already been accepted for processing.

## Problem

Current hooks are not sufficient for inbound gateway policy control because:

- `agent:start` fires after inbound message acceptance
- there is no generic hook event before message dispatch
- there is no standard hook return contract for `ignore` / `rewrite`
- profile-local behavior therefore leaks into adapter logic or local source patches

For multi-bot orchestration, this is especially painful in Telegram groups/topics where workers should be quiet unless summoned.

## Proposed Feature

Introduce a new hook event:

```text
gateway:message:preprocess
```

This event should fire **after the adapter normalizes the inbound message context**, but **before session creation/selection and before agent processing begins**.

## Proposed Hook Return Contract

Hooks may return one of:

```python
{"action": "allow"}
{"action": "ignore", "reason": "not mentioned"}
{"action": "rewrite", "message": "..."}
```

### Semantics

- `allow` → continue normally
- `ignore` → stop processing entirely
- `rewrite` → replace inbound message text, then continue normally

### Resolution order

If multiple hooks return decisions:

1. any `ignore` wins
2. else last `rewrite` wins
3. else default `allow`

## Example Use Case

### Desired Telegram behavior

- `default` / Haku: respond normally in war-room group
- worker bots: in groups/topics, only process if
  - explicitly mentioned, or
  - replied to directly
- worker bots: ignore plain group chatter
- DMs: still allowed

This is not Telegram-specific policy hardcoded in Hermes core; it is an example of why a generic preprocess hook is valuable.

## Proposed Context Shape

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

## Why `agent:start` is not enough

`agent:start` is an observability hook, not a dispatch policy hook.

By the time it fires:
- the adapter already accepted the message
- the gateway may already have selected or created a session
- agent work may already be spinning up
- there is no clean hard-veto path

## Minimal Implementation Surface

Likely touched files:

- `gateway/hooks.py`
  - normalize / resolve preprocess decisions
- `gateway/run.py`
  - central helper to emit preprocess hooks and resolve final action
- `gateway/platforms/telegram.py`
  - compute mention/reply metadata and call preprocess hook before dispatch

## Backward Compatibility

This should be backward compatible because:

- existing hooks continue working unchanged
- default behavior stays `allow`
- no current platform behavior changes unless a hook opts into the new event

## Suggested Tests

- preprocess hook resolution: ignore > rewrite > allow
- worker profile plain group message ignored
- worker profile explicit mention allowed
- worker profile reply-to-bot allowed
- DM allowed
- rewrite action mutates text before dispatch

## Why this matters

This gives Hermes a clean, reusable policy layer for:

- mention-only worker bots
- noisy-channel suppression
- role-based routing
- incident-room policies
- future cross-platform inbound gating

without forcing local source patches or platform-specific hardcoding.

## Reference

Detailed implementation plan lives here:

- `docs/hermes-upstream-pr-implementation-plan.md`

Ready hook policy reference lives here:

- `hooks/telegram-mention-gate/`
