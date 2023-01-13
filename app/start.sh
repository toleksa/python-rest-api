export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=${API_PORT:-5000}
