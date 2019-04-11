import platform
import subprocess
import psutil
import os
import friend.settings as settings


def is_process_running():
    """
    检查serial_redirect进程是否在运行，
    :return: <Process object> if process is running,
    """
    process_list = [x for x in psutil.process_iter()
                    if x.name().lower() == 'redis-server' or x.name().lower() == 'redis-server.exe']

    return None if len(process_list) == 0 else process_list[0]


def start_process_if_not_exist():
    """
    启动serial_redirect进程
    """
    old_process = is_process_running()
    if old_process:
        return

    if platform.system().lower() == 'windows':
        pass
    else:
        os.system("/etc/init.d/redis-server start")


def stop_process():
    """
    停止serial_redirect进程
    :return:
    """
    ps = is_process_running()
    if ps is None:
        return

    ps.kill()


def restart_process():
    """
    重启modbusd进程
    :return:
    """
    stop_process()
    start_process_if_not_exist()
