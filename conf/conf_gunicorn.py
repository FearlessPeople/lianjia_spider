# -*- coding: utf-8 -*-

# 并行进程数
workers = 1

# 指定每个进程开启的线程数
threads = 1

# 监听端口
bind = '0.0.0.0:8000'

# 是否设为守护进程
daemon = 'true'

# 工作模式：协程
# 默认为sync异步，类型：sync, eventlet, gevent, tornado, gthread, gaiohttp
# worker_class = 'gevent'

# 客户端最大并发量，默认为1000
worker_connections = 512
# 等待连接的最大数，默认2048
backlog = 1024

# 进程文件
pidfile = 'logs/gunicorn.pid'

# 访问日志和错误日志
accesslog = 'logs/gunicorn_access.log'
errorlog = 'logs/gunicorn_error.log'

# 日志级别
loglevel = 'info'
