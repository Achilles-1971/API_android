web: daphne -b 0.0.0.0 -p $PORT kursk_backend.asgi:application
worker: celery -A kursk_backend worker --loglevel=info
beat: celery -A kursk_backend beat --loglevel=info
