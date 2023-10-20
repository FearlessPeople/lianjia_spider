# -*- coding: utf-8 -*-
import sys

SYS_PLATFORM = sys.platform

# 是否生产环境
IS_PRO = True
if SYS_PLATFORM == 'linux':  # 服务器
    IS_PRO = True
elif SYS_PLATFORM == 'darwin':  # MacOS
    IS_PRO = False
elif SYS_PLATFORM == 'win32':  # Windows
    IS_PRO = True

# 解决Request object has no attribute 'is_xhr'
JSONIFY_PRETTYPRINT_REGULAR = False
# 支持中文
JSON_AS_ASCII = False
