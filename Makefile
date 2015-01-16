# System variables
ENV_DIR=$(CURDIR)/.env
PYTHON=$(ENV_DIR)/bin/python

PROJECT=rocketws
DOCKER_IMAGE=prawncake/rocketws

help:
# target: help - Display callable targets
	@grep -e "^# target:" [Mm]akefile | sed -e 's/^# target: //g'

.PHONY: run
run: env
# target: run - run server in console mode
	@$(PYTHON) $(CURDIR)/rocketws/server.py

.PHONY: run_bg
run_bg: env
# target: run_bg - run server in background
	@nohup $(PYTHON) $(CURDIR)/rocketws/server.py >> /var/log/rocketws.log &

.PHONY: shell
shell:
# target: Run command line interface
	@$(PYTHON) $(CURDIR)/rocketws/shell.py

.PHONY: env
env:
# target: env - create virtualenv and install packages
	@virtualenv $(ENV_DIR)
	@$(ENV_DIR)/bin/pip install -r $(CURDIR)/requirements.txt

.PHONY: test
test: env
# target: test - Run tests
	@$(PYTHON) -m unittest -v rocketws.tests


.PHONY: pull_image
pull_image:
# target: pull_image - Pull docker image from the hub
	@docker pull $(DOCKER_IMAGE)

.PHONY: run_docker
run_docker:
# target: run_docker - Run rocketws with docker
	@docker run -i -t -d -p 58000:58000 -p 59999:59999 $(DOCKER_IMAGE) make run_bg