@echo off
setlocal

for /f "tokens=5" %%P in ('netstat -a -n -o ^| find "0.0.0.0:8000"') do set "pid=%%P"
if defined pid (
    echo Stopping Gunicorn (PID: %pid%)...
    taskkill /F /PID %pid%
    echo Gunicorn has been stopped.
) else (
    echo Gunicorn is not running.
)

pause
