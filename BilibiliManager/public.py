# -*- coding: utf-8 -*-#

# Author:ZephyrChole
# @software: PyCharm
# @file: public.py
# @time: 2/22/2021 9:36 PM
import os
import sys
import time
import logging
from abc import ABCMeta, abstractmethod
from subprocess import Popen, TimeoutExpired
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def check_path(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        return True
    else:
        path = os.path.split(folder_path)[0]
        if check_path(path):
            try:
                os.mkdir(folder_path)
                return True
            except:
                return False
        else:
            return False


def get_logger(name, level, has_console, has_file):
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if has_console:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    if has_file:
        count = 1
        while True:
            path = f'./log/{time.strftime("%Y-%m-%d", time.localtime())}-{count}.log'
            if os.path.exists(path):
                count += 1
            else:
                break
        fh = logging.FileHandler(path, encoding='utf-8')
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger


def get_headless_browser():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    return webdriver.Chrome(chrome_options=chrome_options)


def wrap_logger(logger, head_msg):
    logger.debug = lambda msg: logger.debug(f'{head_msg} {msg}')
    logger.info = lambda msg: logger.info(f'{head_msg} {msg}')
    logger.warning = lambda msg: logger.warning(f'{head_msg} {msg}')
    logger.error = lambda msg: logger.error(f'{head_msg} {msg}')


class RecordDownloader(metaclass=ABCMeta):
    folder = 'default'

    def __init__(self, download_script_repo, logger, upper_repo, up):
        self.download_script_repo = download_script_repo
        self.repo = os.path.join(upper_repo, self.folder)
        self.up = up
        self.logger = get_logger(f'{logger.name}_', logger.level, False, False)
        wrap_logger(self.logger, self.up.name)

    def main(self):
        self.logger.info(f'{self.folder} download start')
        r = check_path(self.repo)
        if r:
            self.logger.info('path check success')
            self.start_download(self.get_info())
        else:
            self.logger.error('path check fail')
        return r

    @abstractmethod
    def get_info(self):
        pass

    def start_download(self, info):
        def is_normal():
            return reload < MAX_RELOAD

        MAX_RELOAD = 3
        for i in info:
            reload = 0
            while is_normal():
                if self.download(i):
                    break
                else:
                    self.logger.info(f'{i.id} download timeout,{reload} attempt')
                    reload += 1
            if not is_normal():
                self.logger.info(f'{i.id} download fail,skipping...')
            return is_normal()

    @abstractmethod
    def download(self, info):
        pass

    @abstractmethod
    def is_complete(self, info, tar_dir):
        pass

    @abstractmethod
    def raw_download(self, info, tar_dir):
        pass

    @staticmethod
    def start_Popen_stdout2file_wait(parameters, cwd, timeout=None):
        log_file = os.path.join(cwd, 'log', f'{time.strftime("%Y-%m-%d-bili", time.localtime())}.log')
        p = Popen(parameters, stdout=open(log_file, 'w'))
        try:
            if timeout is not None:
                p.wait(timeout)
            else:
                p.wait()
            return True
        except TimeoutExpired:
            p.terminate()
            return False
