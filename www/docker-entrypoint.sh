#!/usr/bin/env sh
set -eu

envsubst '${ENV_API_URL} ${WWW_PORT}' < /etc/nginx/conf.d/default.template > /etc/nginx/conf.d/default.conf

exec "$@"

