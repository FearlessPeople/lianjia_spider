# -*- coding: utf-8 -*-

import os
import platform

version = '0.0.2'


def build_macos():
    os.system('pyinstaller '
              '--clean '
              '--python="./venv/bin/python3" '
              '--windowed '
              '--noconfirm '
              f'--name="LianJia-{version}-macos-arm64" '
              '--hidden-import "lxml" '
              '--hidden-import "pypinyin" '
              '--icon="./static/image/logo.icns" '
              '--add-data="static:static" '
              'gui.py')


def build_windows():
    os.system('pyinstaller '
              '--clean '
              '--python="./venv/bin/python3" '
              '--windowed '
              '--noconfirm '
              f'--name="LianJia-{version}-windows-x86_64" '
              '--hidden-import "lxml" '
              '--hidden-import "pypinyin" '
              '--icon="./static/image/logo.ico" '
              '--add-data="static;static" '
              'gui.py')


def main():
    # 获取当前操作系统类型
    current_os = platform.system().lower()

    # 根据当前操作系统执行相应的打包操作
    if current_os == 'darwin':
        build_macos()
    elif current_os == 'windows':
        build_windows()
    else:
        print("Unsupported operating system.")


if __name__ == "__main__":
    main()
    print("build success......")
