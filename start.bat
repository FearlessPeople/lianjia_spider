title RPA机器人服务
@echo off
echo 不要关闭本窗口！
echo 不要关闭本窗口！
echo 不要关闭本窗口！


rem 激活虚拟环境
call .\venv\Scripts\activate.bat

git pull origin master

setlocal

echo Starting Gunicorn...
waitress-serve --listen=*:8000 wsgi:app

echo Gunicorn is running.
pause
