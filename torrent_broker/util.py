# coding: utf-8

import threading

__author__ = 'buyvich'

def set_main_thread_name():
    for thread in threading.enumerate():
        if isinstance(thread, threading._MainThread):
            thread.setName('main')
