# -*- coding: utf-8 -*-
from flask import jsonify, Blueprint, render_template
from apps.apis.api_scheduler import get_all_jobs
from apps.utils.util_sqlite import SQLiteDB

index = Blueprint('index', __name__)

db = SQLiteDB()


@index.route('/')
def home():
    all_jobs = get_all_jobs().json
    result_jobs = []
    for job in all_jobs:
        job_id = job['id']
        job_runing = db.query(
            f"select * from job_history t where job_id='{job_id}' and date(start_time)=DATE('now', 'localtime') and run_statu=2 limit 100;")
        if job_runing:
            job_status = "Runing"
        else:
            job_status = "Pending"
        job['job_status'] = job_status
        result_jobs.append(job)

    content = {
        'all_jobs': result_jobs
    }
    return render_template('index.html', **content)


@index.route('/login/<job_id>', methods=['GET'])
def login(job_id):
    login_status = False

    content = {
        'login_status': login_status
    }
    return jsonify({'result': content})
