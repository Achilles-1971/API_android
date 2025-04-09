@echo off
set /p TOKEN=Введите ваш токен (без "Token "):
set /p USER_ID=Введите ID собеседника:

echo 📡 Подключение к WebSocket чату с пользователем %USER_ID%...
wscat -c ws://localhost:8000/ws/chat/%USER_ID%/ -H "Authorization: Token %TOKEN%"
pause
