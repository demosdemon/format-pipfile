ifeq ($(VIRTUAL_ENV), )
VIRTUAL_ENV := $(shell pipenv --venv 2>/dev/null)
endif

ifeq ($(VIRTUAL_ENV), )
VIRTUAL_ENV := $(CURDIR)/.venv
endif

PYTHON ?= $(VIRTUAL_ENV)/bin/python
python_code := format_pipfile ci tests

help:
	@echo 'Usage: make <target>'
	@echo '  Where <target> is one of:'
	@echo '    all             Execute all build operations.'
	@echo '    clean           Delete the generated output.'
	@echo '    debug-make      Print all of the `make` variables for debugging.'
	@echo '    format          Execute black and isort formatters on python code.'
	@echo '    format-pipfile  Reformats the project Pipfile using the ci/format_requirements.py script.
	@echo '    help            Show this message and exit.'
	@echo '    lock            Regenerate the lockfile.'
	@echo '    sync            Synchronize the virtual environment with the lockfile.'
	@echo '    test            Executes py.test unit tests.'

debug-make:
	@echo "CURDIR      := $(CURDIR)"
	@echo "VIRTUAL_ENV := $(VIRTUAL_ENV)"
	@echo "PYTHON      := $(PYTHON)"
	@echo "python_code := $(python_code)"

Pipfile.lock: Pipfile
	pipenv lock --pre

all: lock sync format test

clean:
	git clean -xdf -e .env -e .venv

format: format-pipfile $(PYTHON)
	$(VIRTUAL_ENV)/bin/python-modernize --nobackup --write $(python_code)
	$(PYTHON) -m isort --recursive $(python_code)
	$(PYTHON) -m black $(python_code)
	$(PYTHON) ci/bootstrap.py

format-pipfile:
	$(PYTHON) -m format_pipfile

lock: Pipfile.lock

sync $(PYTHON): Pipfile.lock
	pipenv sync --dev
	pipenv clean
	@touch $(PYTHON)

test: $(PYTHON)
	$(PYTHON) -m pytest

.PHONY: all clean debug-make format help lock sync test
