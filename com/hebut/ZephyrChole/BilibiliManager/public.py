# -*- coding: utf-8 -*-#

# Author:Jiawei Feng
# @software: PyCharm
# @file: public.py
# @time: 2/22/2021 9:36 PM

from abc import ABCMeta, abstractmethod


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
