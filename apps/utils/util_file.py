# -*- coding: utf-8 -*-
import os


class FileUtil:
    @staticmethod
    def file_exists(file_path):
        """
        判断文件是否存在
        Arg: file_path (str): 要检查的文件路径。
        Returns: bool: 如果文件存在返回True，否则返回False。
        """
        return os.path.exists(file_path)
