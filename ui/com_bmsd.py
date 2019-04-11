import platform
import subprocess
import psutil
import os
import friend.settings as settings


def is_process_running():
    process_list = [x for x in psutil.process_iter() if x.name().lower() == 'python' or x.name().lower() == 'python.exe']
    for ps in process_list:
        cmdline = ps.cmdline()
        if settings.BMSD_SCRIPT_PATH in cmdline:
            return ps
    return None


def start_process_if_not_exist(can_model, bms_model, can_bautrate, redis_host, redis_port, redis_database):
    old_process = is_process_running()

    command_line = " ".join([
        "python3",
        "'" + settings.BMSD_SCRIPT_PATH + "'",
        "--bms-model", bms_model,
        "--can-model", can_model,
        "--can-channel", str(0),
        "--can-bautrate", can_bautrate,
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
