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
    'unrestricted_profiles': ['default'],
    'mention_only_profiles': ['security', 'dev1', 'dev2', 'qa1', 'qa2'],
    'allow_in_dm': True,
    'allow_commands': True,
    'allow_replies_to_bot': True,
    'allow_mentions': True,
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

print('All tests passed.')
