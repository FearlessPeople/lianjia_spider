# -*- coding: utf-8 -*-
import atexit
import logging
import os
import sys
import traceback

import portalocker
from apscheduler.events import EVENT_JOB_SUBMITTED, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from flask_apscheduler import APScheduler

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

"""
def create_app(app_config):
    global redis_client, app
    # 加载flask配置
    app.config.from_pyfile(os.getcwd() + '/config/' + app_config + '.py')  # 加载配置文件
    app.config.from_object(conf_scheduler)
    app.config['use_reloader'] = False
    server_ip = get_server_ip()
    if server_ip:
        conf_ds = app.config.get('CONF_DS')
        sche_job_allowed_ip = conf_ds.get('sche_job_allowed_ip')
        if server_ip == sche_job_allowed_ip:
            register_scheduler(app)
"""

scheduler = APScheduler()


# 事件                    对应枚举值         描述                     归属类
# EVENT_SCHEDULER_STARTED     1        调度程序启动                   SchedulerEvent
# EVENT_SCHEDULER_SHUTDOWN    2        调度程序关闭                   SchedulerEvent
# EVENT_SCHEDULER_PAUSED      4        调度程序中任务处理暂停         SchedulerEvent
# EVENT_SCHEDULER_RESUMED     8        调度程序中任务处理恢复         SchedulerEvent
# EVENT_EXECUTOR_ADDED        16       将执行器添加到调度程序中     SchedulerEvent
# EVENT_EXECUTOR_REMOVED      32       执行器从调度程序中删除       SchedulerEvent
# EVENT_JOBSTORE_ADDED        64       将任务存储添加到调度程序中    SchedulerEvent
# EVENT_JOBSTORE_REMOVED      128      任务存储从调度程序中删除    SchedulerEvent
# EVENT_ALL_JOBS_REMOVED      256      所有任务从所有任务存储中删除或从一个特定的任务存储中删除    SchedulerEvent
# EVENT_JOB_ADDED             512      任务添加到任务存储中       JobEvent
# EVENT_JOB_REMOVED           1024     从任务存储中删除了任务      JobEvent
# EVENT_JOB_MODIFIED          2048     从调度程序外部修改了任务    JobEvent
# EVENT_JOB_EXECUTED          4096     任务被成功执行            JobExecutionEvent
# EVENT_JOB_ERROR             8192     任务在执行期间引发异常      JobExecutionEvent
# EVENT_JOB_MISSED            16384    错过了任务执行             JobExecutionEvent
# EVENT_JOB_SUBMITTED         32768    任务已经提交到执行器中执行   JobSubmissionEvent
# EVENT_JOB_MAX_INSTANCES     65536    任务因为达到最大并发执行时，触发的事件    JobSubmissionEvent
# EVENT_ALL                            包含以上的所有事件


def event_job_submitted_listener(event):
    code = event.code
    if code == EVENT_JOB_SUBMITTED:
        print("任务开始运行")


def event_job_executed_listener(event):
    code = event.code
    if code == EVENT_JOB_EXECUTED:
        print("任务执行完成")


def event_job_error_listener(event):
    code = event.code
    if code == EVENT_JOB_ERROR:
        print("任务执行失败")


def add_listener(scheduler):
    pass
    # # 任务开始运行监听器
    # scheduler.add_listener(event_job_submitted_listener, EVENT_JOB_SUBMITTED)
    # # 任务执行完成监听器
    # scheduler.add_listener(event_job_executed_listener, EVENT_JOB_EXECUTED)
    # # 任务执行失败监听器
    # scheduler.add_listener(event_job_error_listener, EVENT_JOB_ERROR)


def register_scheduler(flask_app):
    """
    注册定时任务, 使用举例见 上边 def create_app
    flask-scheduler注册任务时注意多线程重复启动任务问题，这里才有lock文件来保证只启动一次定时任务
    :param flask_app:
    :return:
    """
    lock_path = os.path.join(os.getcwd(), 'logs')
    if not os.path.exists(lock_path):
        os.makedirs(lock_path)

    try:
        lock_path = os.path.join(lock_path, 'secheduler.lock')
        # 在上下文管理器中对文件加锁
        with open(lock_path, 'a') as file:
            portalocker.lock(file, portalocker.LOCK_EX)  # 加锁
            file.write(f'This is a flask-scheduler locked file.\n')
            scheduler.init_app(flask_app)
            add_listener(scheduler)
            scheduler.start()
    except Exception as e:
        msg = traceback.format_exc()
        msg = '\n'.join([item for item in msg.split('\n') if item.strip('\n')])
        print('定时任务注册失败...', msg)
        sys.exit(1)

    def unlock():
        portalocker.unlock(file)  # 解锁

    atexit.register(unlock)
