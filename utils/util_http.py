# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@version    : v1.0
@author     : fangzheng
@contact    : fangzheng@rp-pet.cn
@software   : PyCharm
@filename   : util_http.py
@create time: 2024/2/22 2:49 PM
@modify time: 2024/2/22 2:49 PM
@describe   : 
-------------------------------------------------
"""
import requests

from utils.util_print import print2


class HttpUtils:

    @staticmethod
    def get(url, params=None, headers=None, timeout=None):
        try:
            response = requests.get(url=url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print2(f'Error in GET request: {e}')
        except Exception as e:
            print2(f'Error in GET request: {e}')

    @staticmethod
    def post(url, *args, **kwargs):
        try:
            response = requests.post(url, *args, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print2(f'Error in POST request: {e}')
        except Exception as e:
            print2(f'Error in GET request: {e}')
