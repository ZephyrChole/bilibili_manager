# -*- coding: utf-8 -*-#
# Author:Jiawei Feng
# @software: PyCharm
# @file: daemon.py
# @time: 2/20/2021 1:54 PM
import file_parse
import time

attempt = 0
while True:
    attempt += 1
    try:
        file_parse.main()
        break
    except Exception as e:
        print(e)
        if attempt > 3:
            break
        time.sleep(60 * 10)
print('failed')