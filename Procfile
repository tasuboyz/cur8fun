web: gunicorn --config gunicorn.conf.py app:app
release: python -c "from app import app, db; app.app_context().push(); db.create_all()"
