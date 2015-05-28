# coding: utf-8

import threading
import functools
import logging

from torrent_broker import config

__author__ = 'buyvich'

log = logging.getLogger()

def set_main_thread_name():
    for thread in threading.enumerate():
        if isinstance(thread, threading._MainThread):
            thread.setName('main')

def configure_logger():
    for logger_name, params in config.Loggers.iteritems():
        if params.get('enabled', False):
            l_class = getattr(logging, params['class'])
            if isinstance(params['args'], list):
                lh = l_class(*params['args'])
            else:
                lh = l_class(**params['args'])
            lh.setLevel(getattr(logging, params['level']))
            lh.setFormatter(logging.Formatter(params['formatter']))
            log.addHandler(lh)