# System variables
ENV_DIR=$(CURDIR)/.env
PYTHON=$(ENV_DIR)/bin/python
COVERAGE=$(ENV_DIR)/bin/coverage

PROJECT=rocketws
DOCKER_IMAGE=prawncake/rocketws
SETTINGS=rocketws.settings.default

help:
# target: help - Display callable targets
	@grep -e "^# target:" [Mm]akefile | sed -e 's/^# target: //g'

.PHONY: run
run: env
# target: run - run server in console mode
	@$(PYTHON) $(CURDIR)/manage.py runserver --settings=$(SETTINGS)

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
test: env
# target: test - Run tests
	@$(PYTHON) manage.py tests

.PHONY: test_coverage
test_coverage: env
# target: test_coverage - Run tests with coverage
	@$(COVERAGE) run --source=rocketws manage.py tests

.PHONY: pull_image
pull_image:
# target: pull_image - Pull docker image from the hub
	@docker pull $(DOCKER_IMAGE)

.PHONY: run_docker
run_docker:
# target: run_docker - Run rocketws with docker
	@docker run -i -t -d -p 58000:58000 -p 59999:59999 $(DOCKER_IMAGE) make run
