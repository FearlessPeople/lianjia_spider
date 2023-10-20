# -*- coding: utf-8 -*-

import os


class PathUtil:

    @staticmethod
    def project_root():
        """
        获取项目根路径
        :return:
        """
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @staticmethod
    def join(*paths):
        """
        拼接路径
        :param paths:
        :return:
        """
        return os.path.join(*paths)

    @staticmethod
    def parent_path(path=None):
        if path:
            return os.path.dirname(path)
        else:
            return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def create_path(path):
        """
        创建目录
        :param path:
        :return:
        """
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            return path
        except Exception as e:
            print("目录创建异常：", e.args[0])
