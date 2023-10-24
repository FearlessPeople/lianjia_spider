# -*- coding: utf-8 -*-
from datetime import datetime
from logging.config import dictConfig

from apps.utils.util_path import PathUtil

current_date = datetime.now().strftime("%Y%m%d")
project_root = PathUtil.project_root()
PathUtil.create_path(f'{project_root}/logs')

dictConfig({
    "version": 1,
    "disable_existing_loggers": False,  # 不覆盖默认配置
    "formatters": {  # 日志输出样式
        "default": {
            "format": "[%(asctime)s %(levelname)s %(filename)s:%(lineno)d] %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",  # 控制台输出
            "level": "INFO",
            "formatter": "default",
        },
        "debug_handler": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "DEBUG",
            "when": "D",  # 表示按天进行切分
            "interval": 1,  # 每天都切分。 比如interval=2就表示两天切分一下。"
            "formatter": "default",  # 日志输出样式对应formatters
            "filename": f"{project_root}/logs/{current_date}_debug.log",  # 指定log文件目录
            "backupCount": 10,  # 保留10个日志文件
            "encoding": "utf8",  # 文件编码
        },
        "info_handler": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "when": "D",  # 表示按天进行切分
            "interval": 1,  # 每天都切分。 比如interval=2就表示两天切分一下。"
            "formatter": "default",  # 日志输出样式对应formatters
            "filename": f"{project_root}/logs/{current_date}_info.log",  # 指定log文件目录
            "backupCount": 10,  # 保留10个日志文件
            "encoding": "utf8",  # 文件编码
        },
        "error_handler": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "ERROR",
            "when": "D",  # 表示按天进行切分
            "interval": 1,  # 每天都切分。 比如interval=2就表示两天切分一下。"
            "formatter": "default",  # 日志输出样式对应formatters
            "filename": f"{project_root}/logs/{current_date}_error.log",  # 指定log文件目录
            "backupCount": 10,  # 保留10个日志文件
            "encoding": "utf8",  # 文件编码
        },
        'werkzeug_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f"{project_root}/logs/{current_date}_werkzeug.log",  # 指定log文件目录
            'maxBytes': 4194304,  # 4 MB
            'backupCount': 10,
            'level': 'INFO',
        },
    },
    'loggers': {
        'werkzeug': {
            # 这里设置级别可以阻止werkzeug框架烦人的请求日志打印
            # 例如 2023-10-12 11:34:32,910 - werkzeug - INFO - 127.0.0.1 - - [12/Oct/2023 11:34:32] "GET / HTTP/1.1" 200 -
            'level': 'WARNING',
            'handlers': ['werkzeug_handler']
        }
    },
    "root": {
        "level": "DEBUG",  # handler中的level会覆盖掉这里的level
        "handlers": ["console", "debug_handler", "info_handler", "error_handler"],
    },
}
)

if __name__ == '__main__':
    pass
