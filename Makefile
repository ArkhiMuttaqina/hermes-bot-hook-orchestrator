.PHONY: test install-dev1 install-dev2 install-qa1 install-qa2 install-security list

test:
	python tests/test_handler.py

install-dev1:
	bash scripts/install_hook.sh /home/arkhi25/.hermes/profiles/dev1

install-dev2:
	bash scripts/install_hook.sh /home/arkhi25/.hermes/profiles/dev2

install-qa1:
	bash scripts/install_hook.sh /home/arkhi25/.hermes/profiles/qa1

install-qa2:
	bash scripts/install_hook.sh /home/arkhi25/.hermes/profiles/qa2

install-security:
	bash scripts/install_hook.sh /home/arkhi25/.hermes/profiles/security

list:
	find . -maxdepth 3 -type f | sort
