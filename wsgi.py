# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@version    : v1.0
@author     : fangzheng
@contact    : fangzheng@rp-pet.cn
@software   : PyCharm
@filename   : wsgi.py
@create time: 2023/10/8 5:15 PM
@modify time: 2023/10/8 5:15 PM
@describe   : 
-------------------------------------------------
"""
import conf.conf_base
import apps

app = apps.create_app()

if __name__ == '__main__':
    if conf.conf_base.SYS_PLATFORM == 'linux':  # 服务器
        app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)
    elif conf.conf_base.SYS_PLATFORM == 'darwin':  # MacOS
        app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
    elif conf.conf_base.SYS_PLATFORM == 'win32':  # Windows中gunicorn不可用，采用waitress替代
        from waitress import serve

        serve(app, host='0.0.0.0', port=8000)
        # app：指定要运行的 WSGI 应用程序。
        # host：指定服务器监听的主机地址。
        # port：指定服务器监听的端口号。
        # threads：指定服务器的线程数，默认为 4。
        # url_scheme：指定 URL 方案，可以是 'http' 或 'https'。
        # cleanup_interval：指定 Waitress 清理线程的时间间隔。
        # ident：指定服务器的标识。
