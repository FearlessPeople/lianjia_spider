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
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication

from utils.util_area import all_province, get_city_by_province


class LianJia:

    def __init__(self):
        # 从文件中加载UI定义

        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.ui = QUiLoader().load('./ui/lianjia_spider.ui')

        # 创建一个QFile对象，加载QSS文件
        style_file = QFile("./ui/lianjia_spider.qss")
        style_file.open(QFile.ReadOnly)

        # 为整个应用程序设置样式表
        app.setStyleSheet(style_file.readAll().data().decode("utf-8"))

        # 初始化所有省份下拉框数据
        self.ui.province_comboBox.addItems(all_province())
        # 省份下拉框发生变化
        self.ui.province_comboBox.currentIndexChanged.connect(self.handleProvinceChange)
        # 开始按钮点击事件
        self.ui.start_bt.clicked.connect(self.handleStartSpider)
        # 初始化区域按钮点击事件
        self.ui.reset_bt.clicked.connect(self.handleResetBtnSpider)
        # 停止按钮点击事件
        self.ui.stop_bt.clicked.connect(self.handleStopBtnSpider)

    def handleStartSpider(self):
        """
        开始采集按钮点击事件
        """
        province = self.getProvinceText()
        city = self.getCityText()
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f'开始采集:{province}-{city}')
        self.ui.statusbar.showMessage(f"开始采集【{province}-{city}】区域下数据......")

        self.disbleButton()

    def handleResetBtnSpider(self):
        """
        初始化区域按钮点击事件
        """
        province = self.getProvinceText()
        city = self.getCityText()
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(f'开始初始化:{province}-{city}')
        self.ui.statusbar.showMessage(f"开始初始化【{province}-{city}】区域下数据......")

        self.disbleButton()

    def handleStopBtnSpider(self):
        """
        停止按钮点击事件
        """
        self.ui.statusbar.clearMessage()
        self.enableButton()
        self.ui.textBrowser.clear()

    def disbleButton(self):
        # 禁用相关按钮
        self.ui.province_comboBox.setEnabled(False)
        self.ui.city_comboBox.setEnabled(False)
        self.ui.start_bt.setEnabled(False)
        self.ui.reset_bt.setEnabled(False)

    def enableButton(self):
        # 启用相关按钮
        self.ui.province_comboBox.setEnabled(True)
        self.ui.city_comboBox.setEnabled(True)
        self.ui.start_bt.setEnabled(True)
        self.ui.reset_bt.setEnabled(True)

    def handleProvinceChange(self):
        """
        省份下拉框发生变化事件
        """
        province = self.getProvinceText()
        citys = get_city_by_province(province)
        self.ui.city_comboBox.clear()
        self.ui.city_comboBox.addItems(citys)

    def getProvinceText(self):
        return self.ui.province_comboBox.currentText()

    def getCityText(self):
        return self.ui.city_comboBox.currentText()


if __name__ == '__main__':
    app = QApplication([])
    lianjia = LianJia()
    lianjia.ui.show()
    app.exec_()
