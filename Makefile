# SPDX-License-Identifier: Apache-2.0
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/skeleton for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

# Python version can be specified with `$ PYTHON_EXE=python3.x make conf`
PYTHON_EXE?=python3
VENV_LOCATION=.venv
ACTIVATE?=. ${VENV_LOCATION}/bin/activate;
MANAGE=${VENV_LOCATION}/bin/python manage.py

virtualenv:
	@echo "-> Bootstrap the virtualenv with PYTHON_EXE=${PYTHON_EXE}"
	${PYTHON_EXE} -m venv ${VENV_LOCATION}

dev: virtualenv
	@echo "-> Configure and install development dependencies"
	@${ACTIVATE} pip install ${PIP_ARGS} --editable .[dev]

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
	${MANAGE} test --noinput --parallel auto

.PHONY: virtualenv dev valid clean test
