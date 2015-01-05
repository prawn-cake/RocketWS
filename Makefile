# System variables
ENV_DIR=$(CURDIR)/.env
PYTHON=$(ENV_DIR)/bin/python

PROJECT=rocketws

help:
# target: help - Display callable targets
	@grep -e "^# target:" [Mm]akefile | sed -e 's/^# target: //g'

.PHONY: run
run: $(ENV)
# target: run - run server in console mode
	@$(PYTHON) $(CURDIR)/rocketws/server.py

.PHONY: env
env:
# target: env - create virtualenv and install packages
	@virtualenv $(ENV_DIR)
	@$(ENV_DIR)/bin/pip install -r $(CURDIR)/requirements.txt

.PHONY: test
test:
# target: test - Run tests
	@$(PYTHON) -m unittest -v rocketws.tests
