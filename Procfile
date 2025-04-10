web: cd /app && daphne -b 0.0.0.0 -p $PORT kursk_backend.asgi:application
worker: cd /app && celery -A kursk_backend worker --loglevel=info
beat: cd /app && celery -A kursk_backend beat --loglevel=info
