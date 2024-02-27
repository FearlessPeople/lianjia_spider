# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@version    : v1.0
@author     : fangzheng
@contact    : fangzheng@rp-pet.cn
@software   : PyCharm
@filename   : gui.py
@create time: 2024/2/21 11:33 AM
@modify time: 2024/2/21 11:33 AM
@describe   : 
-------------------------------------------------
"""
import os
import sys
import time
import traceback

from PySide2.QtCore import QFile, Signal, QObject, QThreadPool, QCoreApplication
from PySide2.QtCore import QRunnable, Slot
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QTextBrowser, QSystemTrayIcon, QMenu, QAction

from lianjia import LianjiaSpider, create_table
from utils.util_area import all_province, get_city_by_province
from utils.util_print import logqueue

basedir = os.path.dirname(__file__)


class WorkerSignals(QObject):
    """
    自定义信号处理
    """
    finished = Signal()  # worker执行信号
    error = Signal(tuple)  # worker执行错误信号
    result = Signal(object)  # worker执行结果信号
    progress = Signal(int)  # worker执行进度信号


class Worker(QRunnable):
    """
    实际工作线程（通用）
    从 QRunnable 继承到处理程序工作线程设置、信号和结果返回。
    :param callback: 要在此工作线程上运行的函数回调。提供的参数和kwargs 将传递给运行器。
    :type callback: function
    :param args: 要传递给回调函数的参数
    :param kwargs: 要传递给回调函数的关键字
    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self):
        """
        通过初始化的args，kwargs来初始化实际执行函数
        """
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            if result:
                self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class MySignals(QObject):
    """
    打印日志信息的信号处理
    """
    # Signal类有2个参数
    # 参数QTextBrowser：代表你要在哪个组件上进行信号操作
    # 参数str：表示传递的参数类型，这里是str类型
    log_print = Signal(QTextBrowser, str)
    export_statu_print = Signal(str)

    # 进度条处理信号
    progress_print = Signal(int)


# 信号实例化
global_ms = MySignals()


class LianJiaGui:

    def __init__(self):
        # 从文件中加载UI定义

        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        ui_path = os.path.join(basedir, "static", "ui", "lianjia_spider.ui")
        self.ui = QUiLoader().load(ui_path)
        self.log_run_flag = True
        # 创建一个QFile对象，加载QSS文件
        qss_path = os.path.join(basedir, "static", "ui", "lianjia_spider.qss")
        style_file = QFile(qss_path)
        style_file.open(QFile.ReadOnly)

        # 设置窗口图标
        icon_path = os.path.join(basedir, "static", "image", "logo.png")
        icon = QIcon(icon_path)
        self.ui.setWindowIcon(icon)
        tray = QSystemTrayIcon()
        tray.setIcon(icon)
        tray.setVisible(True)

        # 为整个应用程序设置样式表
        app.setStyleSheet(style_file.readAll().data().decode("utf-8"))

        # 初始化所有省份下拉框数据
        self.ui.province_comboBox.addItems(all_province())
        # 省份下拉框发生变化
        self.ui.province_comboBox.currentIndexChanged.connect(self.handleProvinceChange)
        # 开始按钮点击事件
        self.ui.start_bt.clicked.connect(self.handleStartSpider)
        # 导出Excel按钮点击事件
        self.ui.export_bt.clicked.connect(self.handleExportBtnSpider)
        # 停止按钮点击事件
        self.ui.stop_bt.clicked.connect(self.handleStopBtnSpider)

        # 自定义信号的处理函数
        global_ms.log_print.connect(self.logPrint)
        global_ms.export_statu_print.connect(self.exportStatuPrint)

        self.threadpool = QThreadPool()
        self.lj = LianjiaSpider(province_name=None)
        self.lj.signals = global_ms

        # 使用说明
        self.readInstructions()

    def readInstructions(self):
        try:
            txt_file_path = os.path.join(basedir, "static", "使用说明.txt")
            with open(txt_file_path, "r", encoding="utf-8") as file:
                for line in file:
                    self.ui.textBrowser.append(line.strip())
        except FileNotFoundError:
            self.ui.textBrowser.append("找不到使用说明文件！")
        except Exception as e:
            self.ui.textBrowser.append(f"读取文件时出错：{str(e)}")

    def logPrint(self, fb, text):
        """
        打印内容到页面组件上
        """
        fb.append(str(text))
        fb.ensureCursorVisible()

    def exportStatuPrint(self, text):
        """
        打印导出状态到标签上
        """
        self.ui.export_text.setText(str(text))

    def handleStartSpider(self):
        """
        开始采集按钮点击事件
        """
        self.start_flag()
        province = self.getProvinceText()
        city = self.getCityText()

        self.disbleButton()
        self.ui.textBrowser.clear()

        # 开启采集数据线程
        self.lj.province_name = province
        self.lj.city_name = city
        worker = Worker(self.spiderThreadFunc)
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        self.threadpool.start(worker)

        # 开启一个写日志线程
        self.log_run_flag = True
        log_worker = Worker(self.logThreadFunc)
        self.threadpool.start(log_worker)

    def progress_fn(self, n):
        print("%d%% done" % n)

    def logThreadFunc(self, progress_callback):
        while True:
            if not self.log_run_flag:
                return
            logtext = logqueue.get()
            if logtext is None:
                break
            else:
                global_ms.log_print.emit(self.ui.textBrowser, str(logtext))
                time.sleep(0.5)

    def spiderThreadFunc(self, progress_callback):
        self.lj.spider_by_condition()
        # 回调函数：用于打印进度条
        # for n in range(0, 5):
        #     time.sleep(1)
        #     progress_callback.emit(n)

    def dbinitThreadFunc(self, progress_callback):
        self.lj.province_name = self.getProvinceText()
        self.lj.city_name = self.getCityText()
        self.lj.run_flag = True
        self.lj.db_init()

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def handleResetBtnSpider(self):
        """
        初始化区域按钮点击事件
        """
        self.start_flag()
        province = self.getProvinceText()
        city = self.getCityText()

        self.disbleButton()
        self.ui.textBrowser.clear()

        # 开启采集数据线程
        self.lj.province_name = province
        self.lj.city_name = city
        worker = Worker(self.dbinitThreadFunc)
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        self.threadpool.start(worker)

        # 开启一个写日志线程
        self.log_run_flag = True
        log_worker = Worker(self.logThreadFunc)
        self.threadpool.start(log_worker)

    def handleExportBtnSpider(self):
        """
        导出Excel
        """
        self.lj.province_name = self.getProvinceText()
        self.lj.city_name = self.getCityText()
        self.lj.to_excel()

    def handleStopBtnSpider(self):
        """
        停止按钮点击事件
        """
        self.stop_flag()
        self.threadpool.waitForDone()
        self.ui.statusbar.clearMessage()
        self.enableButton()
        self.ui.textBrowser.clear()

    def disbleButton(self):
        """
        禁用相关按钮
        """
        self.ui.province_comboBox.setEnabled(False)
        self.ui.city_comboBox.setEnabled(False)
        self.ui.start_bt.setEnabled(False)
        self.ui.export_bt.setEnabled(False)

    def enableButton(self):
        """
        启用相关按钮
        """
        self.ui.province_comboBox.setEnabled(True)
        self.ui.city_comboBox.setEnabled(True)
        self.ui.start_bt.setEnabled(True)
        self.ui.export_bt.setEnabled(True)

    def handleProvinceChange(self):
        """
        省份下拉框发生变化事件
        """
        province = self.getProvinceText()
        citys = get_city_by_province(province)
        self.ui.city_comboBox.clear()
        self.ui.city_comboBox.addItems(citys)

    def getProvinceText(self):
        """
        获取省份文本
        """
        return self.ui.province_comboBox.currentText()

    def getCityText(self):
        """
        获取城市文本
        """
        return self.ui.city_comboBox.currentText()

    def closeEvent(self, event):
        QApplication.processEvents()
        self.stop_flag()
        QCoreApplication.quit()  # 退出应用程序的事件循环
        self.stop_thread()
        self.threadpool.waitForDone()

    def start_flag(self):
        self.lj.run_flag = True
        self.log_run_flag = True

    def stop_flag(self):
        self.lj.run_flag = False
        self.log_run_flag = False


if __name__ == '__main__':
    create_table()
    app = QApplication([])
    lianjia = LianJiaGui()
    lianjia.ui.show()

    # app.setQuitOnLastWindowClosed(False) # 禁用窗体本身关闭按钮
    icon_path = os.path.join(basedir, "static", "image", "logo.png")
    icon = QIcon(icon_path)
    # Create the tray
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)
    menu = QMenu()
    quit_menu = QAction("退出")
    quit_menu.triggered.connect(app.quit)
    menu.addAction(quit_menu)
    tray.setContextMenu(menu)

    sys.exit(app.exec_())
