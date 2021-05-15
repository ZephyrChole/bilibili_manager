# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: public.py
# @time: 2/22/2021 9:36 PM
import os
from abc import ABCMeta, abstractmethod


def get_abs(path):
    return path if os.path.isabs(path) else os.path.abspath(path)


def check_path(dir_path):
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        return True
    else:
        path = os.path.split(dir_path)[0]
        if check_path(path):
            try:
                os.mkdir(dir_path)
                return True
            except:
                return False
        else:
            return False


class RecordDownloader(metaclass=ABCMeta):

    @abstractmethod
    def main(self):
        pass

    @abstractmethod
    def get_infos(self):
        pass

    @abstractmethod
    def start_download(self, infos):
        pass
