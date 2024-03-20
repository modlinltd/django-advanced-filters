#!/bin/env bash
set -e # Exit immediately if a command exits with a non-zero status.

# Run tests and check code style. Executed from tox (see tox.ini)
#
# this is required due to an issue with generic types used in asgiref and
# pypy's support for them:
# https://github.com/django/asgiref/issues/393

echo "Running tox env $TOX_ENV_NAME"
if [[ $TOX_ENV_NAME = pypy* ]]; then
	echo "Running tests without coverage"
	pytest .
else
	echo "Running tests with coverage"
	pytest --cov-append .
fi
echo "Checking code style"
pycodestyle --exclude=urls.py,migrations,.ropeproject -v advanced_filters
