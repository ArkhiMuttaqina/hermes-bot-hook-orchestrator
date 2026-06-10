from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import yaml

DEFAULT_CONFIG = {
    "unrestricted_profiles": ["default"],
    "mention_only_profiles": ["security", "dev1", "dev2", "qa1", "qa2"],
    "allow_in_dm": True,
    "allow_commands": True,
    "allow_replies_to_bot": True,
    "allow_mentions": True,
}


def _load_config() -> Dict[str, Any]:
    config_path = Path(__file__).with_name('config.yaml')
    example_path = Path(__file__).with_name('config.example.yaml')
    path = config_path if config_path.exists() else example_path
    if not path.exists():
        return dict(DEFAULT_CONFIG)
    data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    merged = dict(DEFAULT_CONFIG)
    merged.update(data)
    return merged


def decide_action(context: Dict[str, Any], config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    cfg = config or _load_config()
    platform = str(context.get('platform') or '').lower()
    profile = str(context.get('profile') or '').strip()
    chat_type = str(context.get('chat_type') or '').lower()
    is_mentioned = bool(context.get('is_mentioned'))
    is_reply_to_bot = bool(context.get('is_reply_to_bot'))
    is_command = bool(context.get('is_command'))

    if platform != 'telegram':
        return {"action": "allow", "reason": "non-telegram platform"}

    if profile in set(cfg.get('unrestricted_profiles', [])):
        return {"action": "allow", "reason": "unrestricted profile"}

    if chat_type == 'dm' and cfg.get('allow_in_dm', True):
        return {"action": "allow", "reason": "dm allowed"}

    mention_only_profiles = set(cfg.get('mention_only_profiles', []))
    if profile not in mention_only_profiles:
        return {"action": "allow", "reason": "profile not gated"}

    if is_command and cfg.get('allow_commands', True):
        return {"action": "allow", "reason": "command allowed"}

    if is_reply_to_bot and cfg.get('allow_replies_to_bot', True):
        return {"action": "allow", "reason": "reply-to-bot allowed"}

    if is_mentioned and cfg.get('allow_mentions', True):
        return {"action": "allow", "reason": "explicit mention allowed"}

    return {"action": "ignore", "reason": "worker bot not mentioned"}


async def handle(event_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
    # This becomes effective once Hermes emits and honors gateway:message:preprocess.
    return decide_action(context)
