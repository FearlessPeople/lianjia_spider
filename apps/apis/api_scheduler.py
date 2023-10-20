# -*- coding: utf-8 -*-

from flask import jsonify
from flask import Blueprint, render_template
from apps.utils.util_scheduler import scheduler
from apps.utils.util_sqlite import SQLiteDB

api_scheduler = Blueprint('api_scheduler', __name__)
db = SQLiteDB()


@api_scheduler.route('/list', methods=['GET'])
def get_all_jobs():
    job_list = []
    try:
        for job in scheduler._scheduler.get_jobs():  # 获取所有任务
            job_info = {
                'id': job.id,
                'name': job.name,
                'trigger': str(job.trigger),
                'next_run_time': str(job.next_run_time),
                'func': job.func_ref,
                'args': job.args,
                'kwargs': job.kwargs
            }
            job_list.append(job_info)

        return jsonify(job_list)
    except Exception as e:
        return jsonify({'error': str(e)})


@api_scheduler.route('/history/<job_id>', methods=['GET'])
def job_history(job_id):
    job_history = []
    try:
        db_history = db.query(f"select * from job_history t where job_id='{job_id}' order by t.start_time desc;")
        content = {
            'job_id': job_id,
            'job_history': db_history
        }
        return render_template('history.html', **content)
    except Exception as e:
        return jsonify({'error': str(e)})
