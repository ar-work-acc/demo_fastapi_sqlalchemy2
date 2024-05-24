#!/bin/bash
# echo "*** Checking mypy issues ... ***"
# mypy --disallow-untyped-defs src test

echo "*** Start running tests! ***"
# Set environment variables for testing.
# Celery also needs these environment variables.
export ENVIRONMENT=test
export DB_DATABASE=test
export DB_USER="postgres"
export DB_PASSWORD="pw2023"
export ADMIN_USERNAME="admin@meowfish.org"
export ADMIN_PASSWORD="pw2023"
export USER_USERNAME="alice@meowfish.org"
export USER_PASSWORD="maxwell"
export CORS_ORIGINS="http://localhost,http://meowfish.org,https://meowfish.org"
export JWT_SECRET_KEY="45126bffdf6fe8197cac2e7aba1444054040cc048ed0c17e3a1356f6a59dac89"
export REDIS_USERNAME="admin"
export REDIS_PASSWORD="pw2024"
export REDIS_DB_BROKER=14
export REDIS_DB_RESULT_BACKEND=15

pytest "$@"