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
    process_list = [x for x in psutil.process_iter() if x.name().lower() == 'python' or x.name().lower() == 'python.exe']
    for ps in process_list:
        cmdline = ps.cmdline()
        if settings.REDIRECT_SERIAL_SCRIPT_PATH in cmdline:
            return ps
    return None


def start_process_if_not_exist(com_dev, forward_port, baudrate, bytesize, stopbit, parity):
    """
    启动serial_redirect进程
    """
    old_process = is_process_running()

    command_line = " ".join([
        "python3",
        settings.REDIRECT_SERIAL_SCRIPT_PATH,
        "--parity", parity,
        "--stopbits", stopbit,
        "--bytesize", bytesize,
        "-P", forward_port,
        com_dev,
        baudrate,
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

    print(command_line)
    if platform.system().lower() == 'windows':
        subprocess.Popen(command_line)
    elif platform.system().lower() in {'macosx', 'darwin', 'linux'}:
        os.system(command_line)
    else:
        print("无法确定系统类型!")


def stop_process():
    """
    停止serial_redirect进程
    :return:
    """
    ps = is_process_running()
    if ps is None:
        return

    ps.kill()


def restart_process(com_dev, forward_port, baudrate, bytesize, stopbit, parity):
    """
    重启modbusd进程
    :return:
    """
    stop_process()
    start_process_if_not_exist(com_dev, forward_port, baudrate, bytesize, stopbit, parity)
