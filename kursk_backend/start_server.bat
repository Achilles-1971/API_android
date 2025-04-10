@echo off
echo Starting Redis (WSL), Celery, Daphne (ASGI) and Celery Beat...

:: 1. Запуск Redis через WSL
start cmd /k "wsl redis-server"

:: 2. Пауза для запуска Redis
timeout /t 3 > nul

:: 3. Запуск Celery worker
start cmd /k "cd /d D:\cla$$$ic\API(VS)\API_android\kursk_backend && call ..\.venv\Scripts\activate && celery -A kursk_backend worker --loglevel=info --pool=solo"

:: 4. Запуск Daphne
start cmd /k "cd /d D:\cla$$$ic\API(VS)\API_android\kursk_backend && call ..\.venv\Scripts\activate && daphne -b 0.0.0.0 -p 8000 kursk_backend.asgi:application"

:: 5. Запуск Celery Beat
start cmd /k "cd /d D:\cla$$$ic\API(VS)\API_android\kursk_backend && call ..\.venv\Scripts\activate && celery -A kursk_backend beat --loglevel=info"

pause
