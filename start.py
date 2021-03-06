# -*- coding: utf-8 -*-#
# Author:Jiawei Feng
# @software: PyCharm
# @file: daemon.py
# @time: 2/20/2021 1:54 PM
import file_parse
import time

while True:
    try:
        file_parse.main()
        break
    except Exception as e:
        print(e)
        time.sleep(60 * 10)
