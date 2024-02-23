# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@version    : v1.0
@author     : fangzheng
@contact    : fangzheng@rp-pet.cn
@software   : PyCharm
@filename   : util_print.py
@create time: 2024/2/22 2:50 PM
@modify time: 2024/2/22 2:50 PM
@describe   : 
-------------------------------------------------
"""
import queue
import datetime

# 创建一个先进先出的队列，用于存储日志信息
logqueue = queue.Queue()


def print2(*args, **kwargs):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{current_time}]", *args, **kwargs)
    logqueue.put(str(f"[{current_time}] {args[0]}"))
