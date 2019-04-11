import platform
import subprocess
import psutil
import os
import friend.settings as settings


def is_process_running():
    """
    检查modbusd进程是否在运行，
    :return: <Process object> if process is running,
    """
    process_list = [x for x in psutil.process_iter() if x.name().lower() == 'python' or x.name().lower() == 'python.exe']
    for ps in process_list:
        cmdline = ps.cmdline()
        if settings.MODBUSD_SCRIPT_PATH in cmdline:
            return ps
    return None


def start_process_if_not_exist(model, dev_address, serial_host, serial_port, redis_host, redis_port, redis_database):
    """
    启动modbusd进程
    :param model: 设备型号
    :param dev_address: 设备地址
    :param serial_host: 串口转发程序地址
    :param serial_port: 串口转发程序端口
    :param redis_host: redis服务器地址
    :param redis_port: redis服务器端口
    :param redis_database: redis数据库
    :return:
    """
    old_process = is_process_running()

    command_line = " ".join([
        "python3",
        "'" + settings.MODBUSD_SCRIPT_PATH + "'",
        "--model", model,
        "--address", str(dev_address),
        "--serial-host", serial_host,
        "--serial-port", str(serial_port),
        "--redis-host", redis_host,
        "--redis-port", str(redis_port),
        "--redis-database", str(redis_database)
    ])
    if platform.system().lower() != 'windows':
        command_line += '&'

    if old_process is None:
        old_process_line = ''
    else:
        old_process_line = ''.join(old_process.cmdline())

    new_process_line = ''.join(command_line)

    if old_process_line == new_process_line:
        # 进程参数相同则不做任何处理
        return
    elif old_process is not None:
        # 旧进程需要关闭
        old_process.kill()

    if platform.system().lower() == 'windows':
        subprocess.Popen(command_line)
    else:
        os.system(command_line)


def stop_process():
    """
    停止modbusd进程
    :return:
    """
    ps = is_process_running()
    if ps is None:
        return

    ps.kill()


def restart_process(model, dev_address, serial_host, serial_port, redis_host, redis_port, redis_database):
    """
    重启modbusd进程
    :param serial_url:
    :return:
    """
    stop_process()
    start_process_if_not_exist(model, dev_address, serial_host, serial_port, redis_host, redis_port, redis_database)
