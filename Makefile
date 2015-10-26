# System variables
ENV_DIR=$(CURDIR)/.env
PYTHON=$(ENV_DIR)/bin/python
COVERAGE=$(ENV_DIR)/bin/coverage
NOSE=$(ENV_DIR)/bin/nosetests
PROJECT_NAME=rocketws
DOCKER_IMAGE=prawncake/rocketws
CODE_DIR=$(CURDIR)/$(PROJECT_NAME)


help:
# target: help - Display callable targets
	@grep -e "^# target:" [Mm]akefile | sed -e 's/^# target: //g'

.PHONY: run
run: env
# target: run - run server in console mode
	@$(PYTHON) $(CURDIR)/manage.py runserver --ws-conn 0.0.0.0:58000 --transport 0.0.0.0:59999

.PHONY: requirements-test.txt
requirements-test.txt: env
# target: requirements-test.txt - install test requirements
	@$(ENV_DIR)/bin/pip install -r $(CURDIR)/requirements-test.txt

.PHONY: run_bg
run_bg:
# target: run_bg - run server in background
	@make run & disown

.PHONY: shell
shell:
# target: Run command line interface
	@$(PYTHON) manage.py shell

.PHONY: env
env:
# target: env - create virtualenv and install packages
	@virtualenv $(ENV_DIR)
	@$(ENV_DIR)/bin/pip install -r $(CURDIR)/requirements.txt

.PHONY: test
test: requirements-test.txt
# target: test - Run tests
	@$(NOSE) --with-coverage $(CODE_DIR)/tests

.PHONY: pull_image
pull_image:
# target: pull_image - Pull docker image from the hub
	@docker pull $(DOCKER_IMAGE)

.PHONY: run_docker
run_docker:
# target: run_docker - Run rocketws with docker
	@docker run -i -t -d -p 58000:58000 -p 59999:59999 $(DOCKER_IMAGE) make run
