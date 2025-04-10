web: cd kursk_backend && daphne -b 0.0.0.0 -p $PORT kursk_backend.asgi:application
worker: cd kursk_backend && celery -A kursk_backend worker --loglevel=info
beat: cd kursk_backend && celery -A kursk_backend beat --loglevel=info
migrate: cd kursk_backend && python manage.py migrate
