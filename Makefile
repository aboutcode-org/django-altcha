#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: MIT
# See https://github.com/aboutcode-org/django-altcha for support or download.
# See https://aboutcode.org for more information about AboutCode FOSS projects.
#

# Python version can be specified with `$ PYTHON_EXE=python3.x make conf`
PYTHON_EXE?=python3
VENV_LOCATION=.venv
ACTIVATE?=. ${VENV_LOCATION}/bin/activate;
DOCS_LOCATION=./docs

virtualenv:
	@echo "-> Bootstrap the virtualenv with PYTHON_EXE=${PYTHON_EXE}"
	${PYTHON_EXE} -m venv ${VENV_LOCATION}

dev: virtualenv
	@echo "-> Configure and install development dependencies"
	@${ACTIVATE} pip install ${PIP_ARGS} --editable .[dev]

check:
	@echo "-> Run Ruff linter validation (pycodestyle, bandit, isort, and more)"
	@${ACTIVATE} ruff check
	@echo "-> Run Ruff format validation"
	@${ACTIVATE} ruff format --check

valid:
	@echo "-> Run Ruff format"
	@${ACTIVATE} ruff format
	@echo "-> Run Ruff linter"
	@${ACTIVATE} ruff check --fix

clean:
	@echo "-> Clean the Python env"
	rm -rf .venv/ .*_cache/ *.egg-info/ build/ dist/
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

test:
	@echo "-> Run the test suite"
	@${ACTIVATE} pytest -s

dist:
	@echo "-> Build source and wheel distributions"
	@${ACTIVATE} pip install setuptools wheel
	@${ACTIVATE} python -m build

docs:
	@echo "-> Builds the installation_and_sysadmin docs"
	rm -rf ${DOCS_LOCATION}/_build/
	@${ACTIVATE} pip install ".[docs]"
	@${ACTIVATE} sphinx-build --fresh-env --fail-on-warning ${DOCS_LOCATION}/source ${DOCS_LOCATION}/_build

.PHONY: virtualenv dev check valid clean test dist docs
