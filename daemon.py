# -*- coding: utf-8 -*-#

import time

# Author:Jiawei Feng
# @software: PyCharm
# @file: daemon.py
# @time: 2/20/2021 1:54 PM
import file_parse

while True:
    while True:
        try:
            file_parse.main()
            break
        except Exception as e:
            print(e)
            time.sleep(60 * 10)
    time.sleep(24 * 60 * 60)
