#!/bin/bash
# echo "*** Checking mypy issues ... ***"
# mypy test

echo "*** Start running tests! ***"
export ENVIRONMENT=test
export DB_DATABASE=test
export CORS_ORIGINS="http://localhost,http://meowfish.org,https://meowfish.org"
export JWT_SECRET_KEY="45126bffdf6fe8197cac2e7aba1444054040cc048ed0c17e3a1356f6a59dac89"
pytest "$@"

