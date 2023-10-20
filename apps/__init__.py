# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@version    : v1.0
@author     : fangzheng
@contact    : fangzheng@rp-pet.cn
@software   : PyCharm
@filename   : __init__.py.py
@create time: 2023/10/8 6:33 PM
@modify time: 2023/10/8 6:33 PM
@describe   : 
-------------------------------------------------
"""

from flask import Flask
from conf.conf_scheduler import APSchedulerJobConfig
from conf.conf_logger import dictConfig
from sql.init_table import init_sql
from apps.utils.util_sqlite import SQLiteDB
from conf import conf_base
from apps.apis import apis
from apps.utils.util_scheduler import register_scheduler

db = SQLiteDB()


def app_init():
    db_init()
    clear_runing_job()


def db_init():
    db.execute(sql=init_sql)


def clear_runing_job():
    """
    每次启动程序时，将当天所有未运行成功的job强制成功
    :return:
    """
    db.execute(
        sql="update job_history set run_statu=0 where run_statu=2  and date(start_time)=DATE('now', 'localtime') ;")


def register_blueprint(app):
    # 注册蓝图
    for api in apis:
        app.register_blueprint(api['blueprint'], url_prefix=api['url_prefix'])


def create_app():
    app = Flask(__name__,
                template_folder='../frontend/templates',
                static_folder='../frontend/static',
                )
    app.config.from_object(APSchedulerJobConfig())
    app.config.from_object(dictConfig)
    app.config.from_object(conf_base)

    register_scheduler(app)

    register_blueprint(app)

    app_init()

    return app


if __name__ == '__main__':
    db_init()
