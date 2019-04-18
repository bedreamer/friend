from django.shortcuts import render
from django.urls import path
from django.http import *
import serial.tools.list_ports
import ui.device_tianshuo as tianshuo
import ui.cache as cache
import ui.bms as bms
import redis
import json
import platform
import subprocess
import psutil
import friend.settings as settings


# 用于缓存数据
import ui.com_redisd as redisd
# 用于转发串口数据到socket端口上
import ui.com_serial_redirect as serial_redirect
# 用于从CAN接口上获取BMS数据
import ui.com_bmsd as bmsd
# 用于驱动设备
import ui.com_modbusd as modbusd
# 用于自动化控制设备
import ui.com_autocontrol as autocontrol
# 用户自定义的BMS数据
import ui.bms as bms

def show_main_page(request):
    return HttpResponseRedirect("/open/")


def show_open_device_page(request):
    # 通讯信息的配置数据
    communicate_profile_path = "newline:communicate:profile"
    # 串口转发进程的心跳数据路径
    serial_redirect_process_path = "newline:serial_redirect:heartbeat"
    # modbusd进程的心跳数据路径
    modbusd_process_path = "newline:modbusd:heartbeat"

    if request.method == 'GET':
        context = dict()

        context['may_interface_list'] = serial.tools.list_ports.comports()

        context['redis_server_process'] = redisd.is_process_running()
        context['serial_redirect_process'] = serial_redirect.is_process_running()
        context['bmsd_process'] = bmsd.is_process_running()
        context['modbusd_process'] = modbusd.is_process_running()
        context['autocontrol_process'] = autocontrol.is_process_running()
        context['user_define_list'] = bms.get_user_define_bms()

        return render(request, "page-打开设备.html", context=context)
    else:
        r = redis.Redis(connection_pool=cache.redis_pool)

        dev_model = request.POST['dev_model']
        dev_address = request.POST['dev_address']
        com_dev = request.POST['com_dev']

        serial_host = request.POST['serial_host']
        serial_forward_port = request.POST['serial_forward_port']

        baudrate = request.POST['baudrate']
        bytesize = request.POST['bytesize']
        stopbit = request.POST['stopbit']
        parity = request.POST['parity']

        can_iface = request.POST['can_iface']
        can_bps = request.POST['can_bps']
        bms_model = request.POST['bms_model']

        redis_host = '127.0.0.1'
        redis_port = 6379
        redis_database = 1

        # 启动串口转发器程序
        serial_redirect.start_process_if_not_exist(com_dev, serial_forward_port, baudrate, bytesize, stopbit, parity)

        # 启动modbusd驱动程序
        modbusd.start_process_if_not_exist(dev_model, dev_address, serial_host, serial_forward_port, redis_host, redis_port, redis_database)

        # 启动BMSD驱动程序
        bmsd.start_process_if_not_exist(request, can_iface, bms_model, can_bps, redis_host, redis_port, redis_database)

        form = dict()
        for key, value in request.POST.items():
            form[key] = value

        r.set(communicate_profile_path, json.dumps(form, ensure_ascii=False))

        url = "/".join(["", dev_model, dev_address, "open"])

        return HttpResponseRedirect(url)


# Create your views here.
urlpatterns = [
    path("", show_main_page),
    path("open/", show_open_device_page),

    path("tianshuo/", tianshuo.urls),

    path("v1.0/json/step/", autocontrol.urls),

    path("bms/", bms.urls),
]
urls = (urlpatterns, "ui", "ui")
