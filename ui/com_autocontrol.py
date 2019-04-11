from django.shortcuts import render
from django.urls import path
from django.http import *
import redis
import json
import time
import importlib
import codecs
import ui.cache as cache
import psutil
import os
import friend.settings as settings
import platform
import subprocess

import ui.device_bms as bms
print(bms)


def get_current_autocontrol_rule_file_path():
    communicate_profile_path = "newline:communicate:profile"

    r = redis.Redis(connection_pool=cache.redis_pool)
    profile_txt = r.get(communicate_profile_path)
    if profile_txt:
        profile = json.loads(profile_txt)
    else:
        return None

    return ''.join([profile['dev_model'], '-', profile['bms_model'], '.json'])


def get_current_dev_model():
    communicate_profile_path = "newline:communicate:profile"

    r = redis.Redis(connection_pool=cache.redis_pool)
    profile_txt = r.get(communicate_profile_path)
    if profile_txt:
        return json.loads(profile_txt)['dev_model']
    else:
        return None


def get_current_bms_model():
    communicate_profile_path = "newline:communicate:profile"

    r = redis.Redis(connection_pool=cache.redis_pool)
    profile_txt = r.get(communicate_profile_path)
    if profile_txt:
        return json.loads(profile_txt)['bms_model']
    else:
        return None


def get_current_profile():
    communicate_profile_path = "newline:communicate:profile"

    r = redis.Redis(connection_pool=cache.redis_pool)
    profile_txt = r.get(communicate_profile_path)
    if profile_txt:
        return json.loads(profile_txt)
    else:
        return None


def is_process_running():
    """
    判断自动控制进程是否在运行
    :return:
    """
    process_list = [x for x in psutil.process_iter() if x.name().lower() == 'python' or x.name().lower() == 'python.exe']
    for ps in process_list:
        cmdline = ps.cmdline()
        if settings.AUTOCONTROL_SCRIPT_PATH in cmdline:
            return ps
    return None


def response_all_supported_conditions(request):
    """
    返回支持的所有判定条件
    :param request:
    :param sid: 工步id默认位0
    :return:
    """

    default_conditions = {
        "True": "False",
        "False": "False",
        "self.loop": "self.loop"
    }
    data = dict()

    bms_model = get_current_bms_model()
    dev_model = get_current_dev_model()

    if None in (bms_model, dev_model):
        data['status'] = 'error'
        data['reason'] = "无法确定BMS和控制设备的型号"
        return HttpResponse(json.dumps(data, ensure_ascii=False))

    device = importlib.import_module('ui.device_' + dev_model)
    bms = importlib.import_module('ui.bms_' + bms_model)

    dev_conditions = device.get_judgement_conditions()
    bms_conditions = bms.get_judgement_conditions()

    data['status'] = 'ok'
    data['data'] = dict(default_conditions, **dev_conditions, **bms_conditions)

    return HttpResponse(json.dumps(data, ensure_ascii=False))


def save_single_step(request, step_name):
    """
    保存单个工步
    :param request:
    :param sid: 工步id默认位0
    :param step_name: 工步名
    :return:
    """
    package = dict()

    step_file_name = get_current_autocontrol_rule_file_path()
    if step_file_name is None:
        package['status'] = 'error'
        package['reason'] = "无法确定控制规则文件"
        return HttpResponse(json.dumps(package, ensure_ascii=False), content_type="application/json")

    try:
        with codecs.open(step_file_name, encoding='utf8') as file:
            steps = json.loads(file.read())
    except:
        steps = dict()

    step = json.loads(request.POST['data'])
    if '' in (step['true'], step['false']):
        package['status'] = "error"
        package['reason'] = "规则文件语法错误"
        return HttpResponse(json.dumps(package, ensure_ascii=False), content_type="application/json")

    steps[step_name] = step

    with codecs.open(step_file_name, "w", encoding='utf8') as file:
        file.write(json.dumps(steps, ensure_ascii=False, indent=2))

    return response_all_steps(request)


def delete_single_step(request, step_name):
    """
    删除单个工步
    :param request:
    :param sid: 工步id默认位0
    :param step_name: 工步名
    :return:
    """
    package = dict()

    step_file_name = get_current_autocontrol_rule_file_path()
    if step_file_name is None:
        package['status'] = 'error'
        package['reason'] = "无法确定控制规则文件"
        return HttpResponse(json.dumps(package, ensure_ascii=False))

    try:
        with codecs.open(step_file_name, encoding='utf8') as file:
            steps = json.loads(file.read())
    except:
        steps = dict()

    try:
        del steps[step_name]
    except:
        pass

    with codecs.open(step_file_name, "w", encoding='utf8') as file:
        file.write(json.dumps(steps, ensure_ascii=False, indent=2))

    return response_all_steps(request)


def query_single_step(request, step_name):
    """
    查询单个工步
    :param request:
    :param sid: 工步id默认位0
    :param step_name: 工步名
    :return:
    """
    package = dict()

    step_file_name = get_current_autocontrol_rule_file_path()
    if step_file_name is None:
        package['status'] = 'error'
        package['reason'] = "无法确定控制规则文件"
        return HttpResponse(json.dumps(package, ensure_ascii=False))

    try:
        with codecs.open(step_file_name, encoding='utf8') as file:
            steps = json.loads(file.read())
    except:
        steps = dict()

    try:
        step = steps[step_name]
        package['status'] = 'ok'
        package['data'] = step
    except:
        package['status'] = 'error'
        package['reason'] = "无当前工步"

    return HttpResponse(json.dumps(package, ensure_ascii=False, indent=2), content_type="application/json")


def response_active_step(request):
    """
    返回当前正在执行的工步
    :param request: HTTP请求对象
    :return: <json object>
    """
    package = dict()
    step_status_cache_path = "autocontrol:status"
    r = redis.Redis(connection_pool=cache.redis_pool)

    status_txt = r.get(step_status_cache_path)
    if status_txt is None:
        package['status'] = 'error'
        package['reason'] = "工步还未执行或已经结束"
    else:
        status = json.loads(status_txt)
        status['main'] = status['name']
        package['main'] = status['name']
        package['data'] = status
        package['status'] = 'ok'

    return HttpResponse(json.dumps(package, ensure_ascii=False, indent=2), content_type="application/json")


def response_all_steps(request):
    """
    返回全部工步数据
    :param request:
    :return:
    """
    package = dict()

    dev_model = get_current_dev_model()
    bms_model = get_current_bms_model()
    if None in (dev_model, bms_model):
        package['status'] = 'error'
        package['reason'] = "无法确定控制规则文件"
        return HttpResponse(json.dumps(package, ensure_ascii=False))

    return response_the_solution(request, dev_model, bms_model)


def response_the_solution(request, dev_model, bms_model):
    """
    返回指定的设备型号及BMS型号的控制方案
    :param request: HTTP请求对象
    :param dev_model: 设备型号
    :param bms_model: BMS型号
    :return: <json object>
    """
    package = dict()

    step_file_name = ''.join([dev_model, '-', bms_model, '.json'])
    if step_file_name is None:
        package['status'] = 'error'
        package['reason'] = "无法确定控制规则文件"
        return HttpResponse(json.dumps(package, ensure_ascii=False))

    package['name'] = '自动控制模式'
    package['filename'] = step_file_name
    package['dev_model'] = dev_model
    package['bms_model'] = bms_model

    try:
        with codecs.open(step_file_name, encoding='utf8') as file:
            package['steps'] = json.loads(file.read())

        steps_entry_number = [int(x[4:]) for x in package['steps']]
        package['main'] = 'step%d' % min(steps_entry_number)
    except:
        package['main'] = None
        package['steps'] = {}

    package['status'] = 'ok'

    return HttpResponse(json.dumps(package, ensure_ascii=False), content_type="application/json")


def step_syntax_check(request):
    """
    检查工步语法
    :param request:
    :param sid: 工步id默认位0
    :return:
    """
    package = dict()

    dev_model = get_current_dev_model()
    bms_model = get_current_bms_model()
    if None in (dev_model, bms_model):
        package['status'] = 'error'
        package['reason'] = "无法确定控制规则文件"
        return HttpResponse(json.dumps(package, ensure_ascii=False), content_type="application/json")

    step_file_name = ''.join([dev_model, '-', bms_model, '.json'])
    try:
        with codecs.open(step_file_name, encoding='utf8') as file:
            steps = json.loads(file.read())
            package['steps'] = steps

        for name, step in steps.items():
            if step['true'] == '$auto':
                pass
            elif step['true'] in steps:
                pass
            else:
                package['status'] = 'error'
                package['reason'] = "".join(["工步", name, "true 目标", step['true'], "没有定义"])
                break

            if step['false'] == '$auto':
                pass
            elif step['false'] in steps:
                pass
            else:
                package['status'] = 'error'
                package['reason'] = "".join(["工步", name, "false 目标", step['false'], "没有定义"])
                break
        if 'reason' not in package:
            package['status'] = 'ok'

        return HttpResponse(json.dumps(package, ensure_ascii=False), content_type="application/json")
    except:
        package['status'] = 'error'
        package['reason'] = "检查控制规则文件出现异常"
        return HttpResponse(json.dumps(package, ensure_ascii=False), content_type="application/json")


def start_step_autocontrol(request):
    """
    启动工步自动控制逻辑
    :param request:
    :return:
    """
    package = dict()
    profile = get_current_profile()

    if profile is None:
        package['status'] = 'error'
        package['reason'] = "无法确定控制规则文件"
        return HttpResponse(json.dumps(package, ensure_ascii=False), content_type="application/json")

    dev_model = profile['dev_model']
    bms_model = profile['bms_model']

    step_file_name = ''.join([dev_model, '-', bms_model, '.json'])
    if step_file_name is None:
        package['status'] = 'error'
        package['reason'] = "无法确定控制规则文件"
        return HttpResponse(json.dumps(package, ensure_ascii=False))

    package['name'] = '自动控制模式'
    package['filename'] = step_file_name
    package['dev_model'] = dev_model
    package['bms_model'] = bms_model

    try:
        with codecs.open(step_file_name, encoding='utf8') as file:
            steps = json.loads(file.read())

        steps_entry_number = [int(x[4:]) for x in steps]
        package['main'] = 'step%d' % min(steps_entry_number)
        package['steps'] = steps
    except Exception as e:
        package['main'] = None
        package['status'] = 'error'
        package['reason'] = '处理工步文件异常，%s' % e
        return HttpResponse(json.dumps(package, ensure_ascii=False), content_type="application/json")

    package['status'] = 'ok'
    try:
        entry = request.GET['entry']
    except:
        entry = package['main']

    if entry not in steps:
        package['status'] = 'error'
        package['reason'] = '启动入口指定错误'
        return HttpResponse(json.dumps(package, ensure_ascii=False), content_type="application/json")

    command_line = " ".join([
        "python3",
        settings.AUTOCONTROL_SCRIPT_PATH,
        "--dev-model", dev_model,
        "--dev-address", str(profile['dev_address']),
        "--bms-model", bms_model,
        "--entry", entry,
        "--web-host", request.environ['REMOTE_ADDR'],
        "--web-port", request.environ['SERVER_PORT']
    ])
    if platform.system().lower() != 'windows':
        command_line += '&'

    old_process = is_process_running()
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

    package['status'] = 'ok'
    return HttpResponse(json.dumps(package, ensure_ascii=False), content_type="application/json")


def stop_step_autocontrol(request):
    """
    停止工步自动控制逻辑
    :param request:
    :param sid: 工步id默认位0
    :return:
    """
    process = is_process_running()
    package = dict()

    autocontrol_command_path = "autocontrol:command"
    r = redis.Redis(connection_pool=cache.redis_pool)

    stop_command = '{"command": "stop"}'
    r.rpush(autocontrol_command_path, stop_command)

    package['status'] = 'ok'
    return HttpResponse(json.dumps(package, ensure_ascii=False), content_type="application/json")


# Create your views here.
urlpatterns = [
    path("steps/get/", response_all_steps),
    path("operation/get/", response_active_step),

    path("<str:step_name>/save/", save_single_step),
    path("<str:step_name>/delete/", delete_single_step),
    path("<str:step_name>/query/", query_single_step),
    path("<str:step_name>/get/", query_single_step),

    path("supported_conditions/", response_all_supported_conditions),
    path("check/", step_syntax_check),
    path("start/", start_step_autocontrol),
    path("stop/", stop_step_autocontrol),

    path("solution/device/<str:dev_model>/bms/<str:bms_model>/", response_the_solution)
]
urls = (urlpatterns, "steps", "steps")
