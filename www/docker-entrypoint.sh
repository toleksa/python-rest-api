#!/usr/bin/env sh
set -eu

envsubst '${ENV_API_URL}' < /etc/nginx/conf.d/default.template > /etc/nginx/conf.d/default.conf

exec "$@"

