# -*- coding: utf-8 -*-
import requests
import os
import logging


class HttpUtils:
    logger = logging.getLogger('HttpUtils')

    @staticmethod
    def get(url, params=None, headers=None, timeout=None):
        try:
            response = requests.get(url=url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            HttpUtils.logger.error(f'Error in GET request: {e}')
        except Exception as e:
            HttpUtils.logger.error(f'Error in GET request: {e}')

    @staticmethod
    def post(url, *args, **kwargs):
        """
        requests.post 是用于发送 HTTP POST 请求的函数，它可以用于向服务器提交数据。
        以下是一些常用的参数：
            url：要发送 POST 请求的 URL。
            data：要作为请求正文发送的数据，可以是一个字典、元组列表、字节序列或文件对象。
            json：要作为 JSON 发送的数据，会自动将其转换为 JSON 格式。
            headers：HTTP 请求头。
            params：添加到 URL 中的查询字符串参数。
            auth：用于 HTTP 认证的元组。
            cookies：用于发送的 cookie。
            files：要上传的文件。
            timeout：设置请求超时时间。
            allow_redirects：设置是否允许重定向。
            proxies：代理字典。
            verify：用于验证 SSL 证书的布尔值或字符串。
            stream：设置为 True 以使响应内容立即下载。
            cert：用于 SSL 客户端证书的字符串或元组。
            hooks：用于自定义回调的字典。
        :param url:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            response = requests.post(url, *args, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            HttpUtils.logger.error(f'Error in POST request: {e}')
        except Exception as e:
            HttpUtils.logger.error(f'Error in GET request: {e}')

    @staticmethod
    def download(url, local_filename, headers_cookie=None):
        """
        下载文件
        :param url: 下载文件完整URL，例如：http://www.baidu.com/logo.png
        :param local_filename: 文件保存本地全路径
        :param headers_cookie: 是否需要cookie，对应header参数里cookie值
        :return: 成功True  失败False
        """
        headers = {
            'Accept': 'application/octet-stream, */*'
        }
        if headers_cookie:
            headers['Cookie'] = headers_cookie

        try:
            if not os.path.exists(os.path.dirname(local_filename)):
                os.makedirs(os.path.dirname(local_filename))
            response = requests.get(url, headers=headers)
            with open(local_filename, 'wb') as f:
                f.write(response.content)
            if os.path.exists(local_filename):
                return True
            else:
                return False
        except Exception as e:
            print("下载文件异常：", e)
