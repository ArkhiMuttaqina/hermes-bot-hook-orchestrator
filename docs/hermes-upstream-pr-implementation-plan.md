# Hermes Upstream PR Implementation Plan

## Objective

Add a **pre-dispatch inbound gateway hook** to Hermes so profile-local hooks can enforce policies like:

- `default` / Haku: respond freely in Telegram group chats
- worker bots: process group/forum messages **only when mentioned or replied to**

This keeps policy out of the Telegram adapter and avoids per-user local source hacks.

---

## Why this PR is needed

Current Hermes hooks are not enough for mention-gating:

- `agent:start` fires too late
- the Telegram adapter already accepted and normalized the message
- a session may already be selected or created
- agent spin-up may already be underway
- there is no supported veto path

Current Telegram text handling runs through `_handle_text_message()` and checks `_should_process_message(msg)`, but there is no generic hook-driven decision point before dispatch.

---

## Proposed feature

### New event

`gateway:message:preprocess`

### Purpose

Let hooks decide whether an inbound message should:

- continue normally
- be ignored entirely
- have its text rewritten before normal processing

---

## Proposed decision model

Hooks may return one of:

```python
{"action": "allow"}
{"action": "ignore", "reason": "not mentioned"}
{"action": "rewrite", "message": "..."}
```

### Resolution order

If multiple hooks return decisions:

1. any `ignore` wins
2. else last `rewrite` wins
3. else default `allow`

This is intentionally tiny and deterministic.

---

## Minimal touched-file map in Hermes

### 1. `gateway/hooks.py`

Add a small helper that interprets collected decision results.

#### Proposed additions
- helper to normalize hook return shapes
- helper to resolve final action from `emit_collect(...)`
- docstring updates listing the new event and context contract

#### Why here
This keeps event semantics centralized in the hook system instead of scattering policy parsing across adapters.

---

### 2. `gateway/run.py`

Add a gateway-level helper that emits `gateway:message:preprocess` and returns the resolved action.

#### Proposed helper
Something like:

```python
async def _run_message_preprocess_hooks(self, event: MessageEvent) -> dict:
    ...
```

#### Responsibilities
- build hook context from normalized `MessageEvent` + source metadata
- include profile name if available
- call `self._hooks.emit_collect('gateway:message:preprocess', context)`
- resolve final action
- return `{"action": "allow"}` when no hook decides otherwise

#### Why in `run.py`
`GatewayRunner` already owns hook registry lifecycle and is the cleanest place to centralize policy evaluation.

---

### 3. `gateway/platforms/telegram.py`

Insert a call path from inbound Telegram handlers into the new pre-dispatch gate.

#### Main touch points
- `_handle_text_message`
- `_handle_command`
- `_handle_location_message`
- `_handle_media_message` (if mention-gating should also cover non-text group posts)

#### Suggested flow
Current flow in `_handle_text_message()`:

1. validate message exists
2. `_should_process_message(msg)`
3. build `MessageEvent`
4. clean trigger text
5. enqueue or dispatch

Proposed flow:

1. validate message exists
2. `_should_process_message(msg)`
3. build `MessageEvent`
4. compute preprocess context fields:
   - `platform`
   - `profile`
   - `chat_type`
   - `chat_id`
   - `thread_id`
   - `message`
   - `bot_username`
   - `is_mentioned`
   - `is_reply_to_bot`
   - `is_command`
5. ask gateway runner / hook policy whether to allow or ignore
6. if ignored: return early, without enqueueing/dispatching
7. if rewritten: replace `event.text`
8. continue normal flow

#### Important note
The PR should avoid embedding mention-only policy in Telegram itself. Telegram should only expose enough structured context for hooks to decide.

---

## Suggested helper functions in Telegram adapter

These are optional but would keep the patch neat:

- `_telegram_message_mentions_bot(msg) -> bool`
- `_telegram_message_replies_to_bot(msg) -> bool`
- `_telegram_preprocess_context(event, msg, is_command=False) -> dict`

This avoids repeating entity/reply inspection logic across handlers.

---

## Proposed context contract

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

### Notes
- `profile` is critical for role-based policy.
- `is_mentioned` must be computed from Telegram entities / explicit bot-mention parsing.
- `is_reply_to_bot` should be true when the incoming message replies to a bot-authored message from the same bot.

---

## Test plan for Hermes upstream

### New unit tests to add

#### `tests/gateway/test_hooks.py`
Add tests for:
- hook registry collecting preprocess decisions
- ignore beats rewrite
- rewrite beats allow
- empty results default to allow

#### `tests/gateway/test_telegram_mention_gate.py` (new)
Add tests for Telegram preprocess behavior:
- default profile group text allowed without mention
- worker profile plain group text ignored
- worker profile explicit mention allowed
- worker profile reply-to-bot allowed
- worker profile DM allowed
- rewrite action mutates text before dispatch

#### Optional regression tests
- ensure existing command handling still works
- ensure group observe / analytics paths do not break if a message is ignored

---

## Backward compatibility

This PR is backward compatible because:

- existing hook directories keep working
- no existing event contract changes
- no behavior changes occur if no hook returns preprocess decisions
- default behavior remains allow

---

## Rollout model after PR merges

1. install `telegram-mention-gate` hook into worker profiles:
   - `security`
   - `dev1`
   - `dev2`
   - `qa1`
   - `qa2`
2. do **not** install it into `default`
3. restart gateways
4. verify:
   - Haku/default still responds freely
   - worker bots ignore unmentioned group messages
   - worker bots respond when mentioned/replied to

---

## Non-goals for this PR

To keep scope tight, the PR should **not** try to add:

- reaction-only fallback behavior
- per-platform UI config screens
- policy persistence in core config.yaml
- cross-platform mention semantics for Slack/Discord/etc.

Those can come later. This PR should only add the small, reusable pre-dispatch hook capability.

---

## PR summary draft

### Title

`feat(gateway): add pre-dispatch message hook for profile-local inbound policy control`

### One-paragraph summary

Adds a new `gateway:message:preprocess` hook event so gateway hooks can allow, ignore, or rewrite inbound messages before session/agent processing begins. This enables clean profile-local policies such as mention-only worker bots in Telegram groups without embedding user-specific logic into Hermes core adapters.
