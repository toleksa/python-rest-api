export FLASK_APP=app.py
REDIS_HOST=${REDIS_HOST:-127.0.0.1} \
REDIS_PORT=${REDIS_PORT:-6379} \
DB_HOST=${DB_HOST:-127.0.0.1} \
DB_PORT=${DB_PORT:-3306} \
DB_DATABASE=${DB_DATABASE:-python_rest_api} \
API_PORT=${API_PORT:-5000} \
DB_USER=${DB_USER:-user} \
DB_PASS=${DB_PASS:-password} \
flask run --host=0.0.0.0 --port=${API_PORT:-5000}

