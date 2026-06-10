.PHONY: test install list test-install

test:
	python tests/test_handler.py

test-install:
	TMPDIR=$$(mktemp -d) && bash scripts/install_hook.sh "$$TMPDIR" && find "$$TMPDIR" -maxdepth 3 -type f | sort

install:
	@echo "Usage: bash scripts/install_hook.sh <HERMES_PROFILE_HOME> [config-template-path]"

list:
	find . -maxdepth 3 -type f | sort
