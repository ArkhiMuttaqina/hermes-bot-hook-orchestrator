from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable
import yaml

DEFAULT_CONFIG = {
    "platforms": ["telegram"],
    "default_action": "allow",
    "allow_in_dm": True,
    "allow_commands": True,
    "allow_replies_to_bot": True,
    "allow_mentions": True,
    "gate_forum_topics": True,
    "profile_rules": {
        "default": {"mode": "allow_all"},
        "security": {"mode": "mention_only"},
        "dev1": {"mode": "mention_only"},
        "dev2": {"mode": "mention_only"},
        "qa1": {"mode": "mention_only"},
        "qa2": {"mode": "mention_only"},
    },
    "bot_rules": {},
}


def _as_set(value: Any) -> set[str]:
    if not value:
        return set()
    if isinstance(value, str):
        return {value.strip()} if value.strip() else set()
    if isinstance(value, Iterable):
        out = set()
        for item in value:
            s = str(item).strip()
            if s:
                out.add(s)
        return out
    return {str(value).strip()} if str(value).strip() else set()


def _load_config() -> Dict[str, Any]:
    config_path = Path(__file__).with_name('config.yaml')
    example_path = Path(__file__).with_name('config.example.yaml')
    path = config_path if config_path.exists() else example_path
    if not path.exists():
        return dict(DEFAULT_CONFIG)
    data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    merged = dict(DEFAULT_CONFIG)
    merged.update(data)
    merged['profile_rules'] = dict(DEFAULT_CONFIG.get('profile_rules', {})) | dict(data.get('profile_rules', {}) or {})
    merged['bot_rules'] = dict(DEFAULT_CONFIG.get('bot_rules', {})) | dict(data.get('bot_rules', {}) or {})
    return merged


def _match_rule(context: Dict[str, Any], cfg: Dict[str, Any]) -> Dict[str, Any]:
    profile = str(context.get('profile') or '').strip()
    bot_username = str(context.get('bot_username') or '').strip().lstrip('@').lower()

    profile_rules = cfg.get('profile_rules', {}) or {}
    bot_rules = cfg.get('bot_rules', {}) or {}

    if profile and profile in profile_rules:
        rule = dict(profile_rules[profile] or {})
        rule['_matched_by'] = f'profile:{profile}'
        return rule

    lowered = {str(k).lower(): v for k, v in bot_rules.items()}
    if bot_username and bot_username in lowered:
        rule = dict(lowered[bot_username] or {})
        rule['_matched_by'] = f'bot:{bot_username}'
        return rule

    return {"mode": cfg.get('default_action', 'allow'), '_matched_by': 'default'}


def decide_action(context: Dict[str, Any], config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    cfg = config or _load_config()
    platform = str(context.get('platform') or '').lower()
    chat_type = str(context.get('chat_type') or '').lower()
    is_mentioned = bool(context.get('is_mentioned'))
    is_reply_to_bot = bool(context.get('is_reply_to_bot'))
    is_command = bool(context.get('is_command'))

    enabled_platforms = _as_set(cfg.get('platforms', ['telegram']))
    if enabled_platforms and platform not in {p.lower() for p in enabled_platforms}:
        return {"action": "allow", "reason": "platform not gated"}

    if chat_type == 'dm' and cfg.get('allow_in_dm', True):
        return {"action": "allow", "reason": "dm allowed"}

    if chat_type == 'forum' and not cfg.get('gate_forum_topics', True):
        return {"action": "allow", "reason": "forum gating disabled"}

    rule = _match_rule(context, cfg)
    mode = str(rule.get('mode') or cfg.get('default_action', 'allow')).strip().lower()

    if mode in {'allow', 'allow_all', 'unrestricted'}:
        return {"action": "allow", "reason": f"unrestricted via {rule.get('_matched_by', 'rule')}"}

    if mode in {'ignore', 'deny', 'drop'}:
        return {"action": "ignore", "reason": f"ignored via {rule.get('_matched_by', 'rule')}"}

    if mode not in {'mention_only', 'reply_or_mention'}:
        return {"action": "allow", "reason": f"unknown mode {mode}; fail-open"}

    if is_command and cfg.get('allow_commands', True):
        return {"action": "allow", "reason": "command allowed"}

    if is_reply_to_bot and cfg.get('allow_replies_to_bot', True):
        return {"action": "allow", "reason": "reply-to-bot allowed"}

    if is_mentioned and cfg.get('allow_mentions', True):
        return {"action": "allow", "reason": "explicit mention allowed"}

    return {"action": "ignore", "reason": f"mention gate via {rule.get('_matched_by', 'rule')}"}


async def handle(event_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
    return decide_action(context)
