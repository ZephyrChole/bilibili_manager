# -*- coding: utf-8 -*-#fv

# Author:Jiawei Feng
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


def get_logger(name, level, has_console, has_file):
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if has_console:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    if has_file:
        count = 0
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


class RecordDownloader(metaclass=ABCMeta):
    folder = 'default'
    max_retry = 3

    def __init__(self, download_script_repo, logger, upper_repo, up):
        self.download_script_repo = download_script_repo
        self.repo = os.path.join(upper_repo, self.folder)
        self.up = up
        self.logger = get_logger(f'{logger.name}_', logger.level, False, False)
        self.logger.debug = lambda msg: logger.debug(f'{up.name} {msg}')
        self.logger.info = lambda msg: logger.info(f'{up.name} {msg}')
        self.logger.warning = lambda msg: logger.warning(f'{up.name} {msg}')
        self.logger.error = lambda msg: logger.error(f'{up.name} {msg}')

    def main(self):
        self.logger.info(f'{self.folder} download start')
        if check_path(self.repo):
            self.logger.info('path check success')
            self.start_download(self.get_info())
            return True
        else:
            self.logger.error('path check fail')
            return False

    @abstractmethod
    def get_info(self):
        pass

    def start_download(self, infos):
        for info in infos:
            attempt = 0
            while attempt < self.max_retry:
                if self.monitor_download(info):
                    break
                else:
                    attempt += 1
                    self.logger.info(f'{info.id} download timeout,{attempt} attempt')
            if attempt >= self.max_retry:
                self.logger.info(f'{info.id} download fail,skipping...')

    @abstractmethod
    def monitor_download(self, info):
        pass

    @abstractmethod
    def is_exist(self, info, tar_dir):
        pass

    @staticmethod
    def start_popen(parameters, cwd, timeout=None):
        log_file = os.path.join(cwd, 'log', f'{time.strftime("%Y-%m-%d-bili", time.localtime())}.log')
        try:
            p = Popen(parameters, stdout=open(log_file, 'w'))
            if timeout is not None:
                p.wait(timeout)
            else:
                p.wait()
            return True
        except TimeoutExpired:
            p.terminate()
            return False
