# -*- coding: utf-8 -*-
import json
import logging
import os

logger = logging.getLogger(os.path.basename(__file__))


class Cookies:
    def __init__(self, cookie_path):
        self.cookie_path = cookie_path
        self.cookies = self._load_cookies()

    def _load_cookies(self):
        try:
            with open(self.cookie_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(e)
            logger.error("Failed to load cookies file")
            logger.error(e.args[0])

    def convert_to_http_header(self, cookies=None, filter_dict=None):
        if cookies:
            input_list = cookies
        else:
            input_list = self.cookies['cookies']
        header_string = ''
        for item in input_list:
            if filter_dict and all(item.get(key) == value for key, value in filter_dict.items()):
                if 'name' in item and 'value' in item:
                    header_string += f"{item['name']}={item['value']};"
            elif not filter_dict:
                if 'name' in item and 'value' in item:
                    header_string += f"{item['name']}={item['value']};"
        return header_string

