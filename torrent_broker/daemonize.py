# coding: utf-8

import os
import sys
import time
import signal
import atexit
import logging

from torrent_broker import config

__author__ = 'buyvich'

log = logging.getLogger()

CHECK_PROCESS_INTERVAL = 15  # sec


def redirect_to_devnull():
    log.debug('Redirect to devnull')
    dev_null = os.open(os.devnull, os.O_WRONLY)
    if dev_null != -1:
        os.dup2(dev_null, sys.stdout.fileno())
        os.dup2(dev_null, sys.stdin.fileno())


def process_alive(pid):
    try:
        os.kill(pid, signal.SIG_DFL)
        return True
    except OSError:
        return False


def kill_process(pid):
    log.debug('Sending SIGTERM to %s', pid)
    os.kill(pid, signal.SIGTERM)
    start_time = time.time()
    while process_alive(pid):
        if time.time() - start_time > CHECK_PROCESS_INTERVAL:
            log.debug('Cant stop process %s, sending SIGKILL', pid)
            os.kill(pid, signal.SIGKILL)
        time.sleep(1)
    log.debug('%s killed', pid)

def process_pid():
    pid = os.getpid()
    if os.path.exists(config.PID_FILE):
        exists_pid = int(open(config.PID_FILE).read().strip())
        if process_alive(exists_pid):
            log.debug('Another torrent_broker running. Trying to kill it')
            kill_process(exists_pid)
        else:
            log.debug('Process %s is not alive', exists_pid)

    try:
        with open(config.PID_FILE, 'w') as f:
            f.write(str(pid))
        log.debug('Create PID file: %s', config.PID_FILE)
    except Exception as ex:
        log.warning('Cannot create PID file %s. %s', config.PID_FILE, ex)

def cleanup():
    log.debug('Cleanup before exit')
    if os.path.exists(config.PID_FILE):
        try:
            os.remove(config.PID_FILE)
            log.debug('Pid-file removed: %s', config.PID_FILE)
        except OSError:
            log.warning('Cannot remove pid-file: %s', config.PID_FILE)


def daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError:
        log.exception('Cannot fork main process')
        sys.exit(13)
    os.setsid()
    os.umask(0)
    log.debug('### torrent-broker starting ###')
    process_pid()

    redirect_to_devnull()
    atexit.register(cleanup)
