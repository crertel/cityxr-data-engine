#! /usr/bin/env bash

set -eou pipefail
docker-compose exec db psql -U cxrdev -d cxr_dev