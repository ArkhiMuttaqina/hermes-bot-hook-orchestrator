# Hermes Upstream Task Breakdown

## Goal

Ship a minimal Hermes upstream change that enables profile-local inbound gateway policy hooks, so worker bots can be mention-only in Telegram groups without local source patching.

---

## Acceptance Criteria

A PR is considered complete when all of these are true:

1. Hermes exposes a new decision-style hook event:
   - `gateway:message:preprocess`
2. Hooks can return:
   - `allow`
   - `ignore`
   - `rewrite`
3. Telegram inbound group messages can be ignored before agent/session processing.
4. Existing hooks and current users see no behavior change unless they opt into the new event.
5. A worker-profile mention gate can be implemented entirely as a hook package.
6. Automated tests cover ignore/allow/rewrite precedence and Telegram mention/reply behavior.

---

## Phase 1 — Hook contract in core

### Task 1.1 — Document the new event in `gateway/hooks.py`
**Output:** hook docstring updated with new event and return semantics.

### Task 1.2 — Add decision normalization helper
**Output:** helper that interprets hook return values into a canonical shape.

### Task 1.3 — Add decision resolution helper
**Output:** helper that resolves multiple hook results with this precedence:
- ignore wins
- else last rewrite wins
- else allow

### Verification
- unit test for empty result list → allow
- unit test for invalid/unknown result shapes → ignored safely
- unit test for ignore precedence

---

## Phase 2 — Gateway runner integration

### Task 2.1 — Add preprocess hook runner in `gateway/run.py`
**Output:** a helper like `_run_message_preprocess_hooks(...)`

### Responsibilities
- accept normalized context
- call `emit_collect('gateway:message:preprocess', context)`
- resolve final action
- return a canonical decision

### Task 2.2 — Ensure profile name is available in hook context
**Output:** hook context includes `profile`

### Verification
- test that no hooks → allow
- test that rewrite decision comes back intact
- test that ignore decision is propagated

---

## Phase 3 — Telegram adapter integration

### Task 3.1 — Add mention detection helper
**Suggested helper:** `_telegram_message_mentions_bot(msg)`

### Task 3.2 — Add reply-to-bot helper
**Suggested helper:** `_telegram_message_replies_to_bot(msg)`

### Task 3.3 — Build preprocess context in Telegram adapter
**Context fields:**
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
- `from_user_id`

### Task 3.4 — Call preprocess hook before dispatch
**Touch points:**
- `_handle_text_message`
- `_handle_command`
- `_handle_location_message`
- `_handle_media_message` (optional in first pass, but recommended)

### Expected behavior
- if `ignore`: return immediately
- if `rewrite`: mutate text and continue
- if `allow`: continue unchanged

### Verification
- plain group text for worker profile ignored
- mentioned worker message allowed
- reply-to-worker allowed
- DM allowed

---

## Phase 4 — Regression safety

### Task 4.1 — Preserve existing command behavior
Commands should continue to work exactly as before unless a hook explicitly chooses to ignore.

### Task 4.2 — Preserve default behavior for users without hooks
No hook installed should mean no behavior change.

### Task 4.3 — Ensure ignored messages do not trigger agent work
No unnecessary session churn, no agent spin-up.

### Verification
- smoke test existing Telegram command handling
- smoke test normal default profile message handling
- smoke test worker profile with no hook installed still behaves as current Hermes

---

## Phase 5 — Hook repo rollout validation

### Task 5.1 — Install `telegram-mention-gate` into worker profiles
Profiles:
- `security`
- `dev1`
- `dev2`
- `qa1`
- `qa2`

### Task 5.2 — Leave `default` un-gated
This keeps Haku as unrestricted orchestrator.

### Task 5.3 — Restart gateways and verify real behavior
Expected:
- Haku/default responds freely
- worker bots ignore plain group chat
- worker bots respond on mention
- worker bots respond on reply

---

## Suggested PR sequencing

### PR 1 — Core hook contract only
Smallest safe PR:
- `gateway/hooks.py`
- tests for decision resolution

### PR 2 — Gateway runner + Telegram integration
Second PR:
- `gateway/run.py`
- `gateway/platforms/telegram.py`
- Telegram-specific tests

### PR 3 — Optional follow-up polish
Only if needed:
- media/location parity
- richer docs
- cross-platform extension notes

This sequencing reduces blast radius and makes review easier.

---

## Blast radius notes

### Low risk
- hook doc updates
- decision helper logic
- default allow behavior

### Medium risk
- Telegram adapter integration
- mention/reply detection correctness
- interaction with command routing and topic mode

### Watch carefully
- forum topic routing
- group observe paths
- command mention cleanup
- message batching for Telegram text bursts

---

## Reviewer checklist

Before merging upstream PR:
- [ ] no behavior change without hooks
- [ ] ignored messages do not reach agent dispatch
- [ ] rewrite path is tested
- [ ] Telegram mention logic is deterministic
- [ ] reply-to-bot path is tested
- [ ] docs mention the new event clearly

---

## Definition of done

Done means a clean upstream Hermes build can support this repo’s `telegram-mention-gate` hook **without any local source modification** beyond normal upstream release usage.
