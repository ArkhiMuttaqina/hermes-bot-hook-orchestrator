# Upstream Hook Contract Proposal

## Problem

Hermes hooks currently fire after a session/agent lifecycle boundary, but there is no **pre-dispatch inbound message policy hook** for Telegram group messages.

For multi-bot orchestration, we need a way to decide **before agent work starts** whether the inbound message should be processed.

## Proposed event

`gateway:message:preprocess`

## When it should fire

After the Telegram adapter has normalized the inbound message into gateway context, but **before** session lookup / agent processing begins.

## Expected context

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

## Expected return shape

Hooks may return one of:

```python
{"action": "allow"}
{"action": "ignore", "reason": "not mentioned"}
{"action": "rewrite", "message": "..."}
```

`allow`:
- continue normal processing

`ignore`:
- stop processing immediately
- do not create/update session
- do not call the agent

`rewrite`:
- replace inbound message text, then continue

## Conflict resolution

If multiple hooks return decisions:

1. any `ignore` wins
2. else last `rewrite` wins
3. else `allow`

## Why this is minimal

This keeps policy out of the Telegram adapter and lets behavior live in profile-local hooks.

## Why `agent:start` is not enough

`agent:start` fires too late:
- session already selected
- agent spin-up may already be happening
- no hard veto path

## Intended use cases

- mention-only worker bots in groups
- suppress noisy channels
- role-based platform policy
- incident-room routing
