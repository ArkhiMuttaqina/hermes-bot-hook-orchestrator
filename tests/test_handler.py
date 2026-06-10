from pathlib import Path
import importlib.util

handler_path = Path(__file__).resolve().parents[1] / 'hooks' / 'telegram-mention-gate' / 'handler.py'
spec = importlib.util.spec_from_file_location('mention_gate_handler', handler_path)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def check(name, got, expected_action):
    if got.get('action') != expected_action:
        raise AssertionError(f"{name}: expected {expected_action}, got {got}")
    print(f"PASS {name}: {got}")


cfg = {
    'platforms': ['telegram'],
    'default_action': 'allow',
    'allow_in_dm': True,
    'allow_commands': True,
    'allow_replies_to_bot': True,
    'allow_mentions': True,
    'gate_forum_topics': True,
    'profile_rules': {
        'default': {'mode': 'allow_all'},
        'security': {'mode': 'mention_only'},
        'dev1': {'mode': 'mention_only'},
        'dev2': {'mode': 'mention_only'},
        'qa1': {'mode': 'mention_only'},
        'qa2': {'mode': 'mention_only'},
    },
    'bot_rules': {
        'custom-worker-bot': {'mode': 'mention_only'},
    },
}

check('default in group', module.decide_action({
    'platform': 'telegram', 'profile': 'default', 'chat_type': 'group'
}, cfg), 'allow')

check('dev1 plain group text ignored', module.decide_action({
    'platform': 'telegram', 'profile': 'dev1', 'chat_type': 'group', 'is_mentioned': False, 'is_reply_to_bot': False, 'is_command': False
}, cfg), 'ignore')

check('dev1 mention allowed', module.decide_action({
    'platform': 'telegram', 'profile': 'dev1', 'chat_type': 'group', 'is_mentioned': True
}, cfg), 'allow')

check('dev1 reply allowed', module.decide_action({
    'platform': 'telegram', 'profile': 'dev1', 'chat_type': 'group', 'is_reply_to_bot': True
}, cfg), 'allow')

check('security DM allowed', module.decide_action({
    'platform': 'telegram', 'profile': 'security', 'chat_type': 'dm'
}, cfg), 'allow')

check('bot username fallback mention-only ignored', module.decide_action({
    'platform': 'telegram', 'profile': 'weird-profile-name', 'bot_username': 'custom-worker-bot', 'chat_type': 'group', 'is_mentioned': False
}, cfg), 'ignore')

check('bot username fallback mention allowed', module.decide_action({
    'platform': 'telegram', 'profile': 'weird-profile-name', 'bot_username': 'custom-worker-bot', 'chat_type': 'group', 'is_mentioned': True
}, cfg), 'allow')

print('All tests passed.')
