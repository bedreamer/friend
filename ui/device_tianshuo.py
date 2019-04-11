from django.shortcuts import render
from django.urls import path
from django.http import *
import redis
import json
import time
import importlib
import ui.cache as cache
import ui.com_autocontrol as com_autocontrol

dev_model = "tianshuo"


def get_judgement_conditions():
    values = [
        "供液压力显示",
        "回液压力显示",
        "供液流量显示",
        "膨胀罐液位显示",
        "阀门开度显示",
        "供液温度显示",
        "回液温度显示",
        "排气温度显示",
        "冷凝液温度显示"
    ]
    return {v: "newline." + v for v in values}


def show_dashboard_page(request, dev_address):
    context = dict()

    context['dev_model'] = dev_model
    context['dev_address'] = dev_address

    r = redis.Redis(connection_pool=cache.redis_pool)
    last_error_path = "%s:%d:lasterror" % (dev_model, dev_address)
    context['lasterror'] = r.llen(last_error_path)

    return render(request, "01-天硕/dashboard.html", context=context)


def show_device_basic_infomation_page(request, dev_address):
    """
    显示设备的控制面板
    :param request: 请求对象
    :param dev_address: 设备地址
    :return:
    """
    context = dict()

    context['dev_model'] = dev_model
    context['dev_address'] = dev_address

    return render(request, "01-天硕/01-设备基本信息.html", context=context)


def show_yaoxin_page(request, dev_address):
    """
    显示设备的控制面板
    :param request: 请求对象
    :param dev_address: 设备地址
    :return:
    """
    context = dict()

    context['dev_model'] = dev_model
    context['dev_address'] = dev_address

    r = redis.Redis(connection_pool=cache.redis_pool)

    status_path = "%s:%d:机组运行状态" % (dev_model, dev_address)
    txt_status = r.get(status_path)
    if txt_status:
        context['status'] = json.loads(txt_status)
    else:
        context['status'] = None

    alarm_path = "%s:%d:输出故障报警" % (dev_model, dev_address)
    txt_alarm = r.get(alarm_path)
    if txt_alarm:
        context['alarm'] = json.loads(txt_alarm)
    else:
        context['alarm'] = None

    last_error_path = "%s:%d:lasterror" % (dev_model, dev_address)
    context['lasterror'] = r.llen(last_error_path)

    return render(request, "01-天硕/02-遥信面板.html", context=context)


def show_yaoce_page(request, dev_address):
    """
    显示设备的控制面板
    :param request: 请求对象
    :param dev_address: 设备地址
    :return:
    """
    context = dict()

    context['dev_model'] = dev_model
    context['dev_address'] = dev_address

    r = redis.Redis(connection_pool=cache.redis_pool)
    yaoce_path = "%s:%d:运行数据" % (dev_model, dev_address)
    txt_yaoce = r.get(yaoce_path)
    if txt_yaoce:
        context['yaoce'] = json.loads(txt_yaoce)
    else:
        context['yaoce'] = None

    bms_model = com_autocontrol.get_current_bms_model()
    bms = importlib.import_module('ui.bms_' + bms_model)
    context['bms'] = bms.get_data()

    last_error_path = "%s:%d:lasterror" % (dev_model, dev_address)
    context['lasterror'] = r.llen(last_error_path)

    return render(request, "01-天硕/03-遥测面板-仪表视图.html", context=context)


def show_yaoce_json(request, dev_address):
    """
    返回json版的遥测数据
    :param request: HTTP请求对象
    :param dev_address: 设备地址
    :return:
    """
    r = redis.Redis(connection_pool=cache.redis_pool)
    yaoce_path = "%s:%d:运行数据" % (dev_model, dev_address)
    txt_yaoce = r.get(yaoce_path)
    if txt_yaoce:
        return HttpResponse(txt_yaoce)
    else:
        return HttpResponse("{}")


def control(r, dev_address, name, value):
    form = dict()
    control_path = "%s:%d:设置参数-写入" % (dev_model, dev_address)
    form[name] = value
    r.rpush(control_path, json.dumps(form, ensure_ascii=False, indent=2))


def show_yaotiao_page(request, dev_address):
    """
    显示设备的控制面板
    :param request: 请求对象
    :param dev_address: 设备地址
    :return:
    """
    r = redis.Redis(connection_pool=cache.redis_pool)

    if request.method == 'POST':
        form = dict()
        for key, value in request.POST.items():
            try:
                form[key] = float(value)
            except:
                pass

        if form == dict():
            return HttpResponseRedirect(request.path)

        if form['远程强制控制加热器'] != 0 and '远程运行程序号' in form and form['远程运行程序号'] == 0:
            # 定值控温
            # 1. 设定加热功率，定值控温时，加热器功率固定为 101%
            control(r, dev_address, '远程强制控制加热器', 101)

            # 2. 选择定值模式, 0: 定值模式， 其他为程序模式
            control(r, dev_address, '远程定值程序模式选择', 0)

            # 3. 设定目标温度
            try:
                control(r, dev_address, '远程定值温度设定', form['远程定值温度设定'])
            except:
                pass

            # 4. 设定目标流量
            try:
                control(r, dev_address, '远程流量设定', form['远程流量设定'])
            except:
                pass

            # 5. 选择循环方式
            try:
                control(r, dev_address, '远程内外循环切换', int(form['远程内外循环切换']))
            except:
                pass

            # 6. 启动循环泵
            control(r, dev_address, '远程排汽加液_启动循环泵', 1)
        elif form['远程强制控制加热器'] == 0 and '远程运行程序号' in form and form['远程运行程序号'] != 0:
            # 程序控温
            # 1. 选择程序模式
            control(r, dev_address, '远程定值程序模式选择', 1)

            # 2. 选择程序号
            control(r, dev_address, '远程运行程序号', int(form['远程运行程序号']))

            # 3. 选择循环方式
            try:
                control(r, dev_address, '远程内外循环切换', int(form['远程内外循环切换']))
            except:
                pass

            # 4. 设定目标流量
            try:
                control(r, dev_address, '远程流量设定', form['远程流量设定'])
            except:
                pass
        elif form['远程强制控制加热器'] != 0 and '远程流量设定' in form and form['远程流量设定'] != 0:
            # 强制加热模式，远程运行程序号输入框需要留空

            # 1. 设定加热功率
            control(r, dev_address, '远程强制控制加热器', form['远程强制控制加热器'])
            # 2. 设定流量
            control(r, dev_address, '远程流量设定', form['远程流量设定'])

        time.sleep(1.5)
        return HttpResponseRedirect(request.path)

    context = dict()

    context['dev_model'] = dev_model
    context['dev_address'] = dev_address

    yaotiao_path = "%s:%d:设置参数-读出" % (dev_model, dev_address)
    txt_yaotiao = r.get(yaotiao_path)
    if txt_yaotiao:
        context['yaotiao'] = json.loads(txt_yaotiao)
    else:
        context['yaotiao'] = None

    last_error_path = "%s:%d:lasterror" % (dev_model, dev_address)
    context['lasterror'] = r.llen(last_error_path)

    return render(request, "01-天硕/05-遥调面板.html", context=context)


def show_yaokong_page(request, dev_address):
    """
    显示设备的控制面板
    :param request: 请求对象
    :param dev_address: 设备地址
    :return:
    """
    r = redis.Redis(connection_pool=cache.redis_pool)

    if request.method == 'POST':
        yaotiao_path = "%s:%d:设置参数-写入" % (dev_model, dev_address)

        form = dict()
        for key, value in request.POST.items():
            form[key] = float(value)

        r.rpush(yaotiao_path, json.dumps(form, ensure_ascii=False, indent=2))
        count = r.llen(yaotiao_path)

        now = time.time()
        while count > 0 and time.time() - now < 3:
            count = r.llen(yaotiao_path)
            print(count)
            time.sleep(0.5)

        time.sleep(0.5)
        return HttpResponseRedirect(request.path)

    context = dict()

    context['dev_model'] = dev_model
    context['dev_address'] = dev_address

    yaotiao_path = "%s:%d:设置参数-读出" % (dev_model, dev_address)
    txt_yaotiao = r.get(yaotiao_path)
    if txt_yaotiao:
        context['yaokong'] = json.loads(txt_yaotiao)
    else:
        context['yaokong'] = None

    last_error_path = "%s:%d:lasterror" % (dev_model, dev_address)
    context['lasterror'] = r.llen(last_error_path)

    return render(request, "01-天硕/04-遥控面板.html", context=context)


def show_autocontrol_page(request, dev_address):
    context = dict()

    context['dev_model'] = dev_model
    context['dev_address'] = dev_address
    context['control_method'] = 'auto'

    return render(request, "00-工步/06-工步控制面板.html", context=context)
    #return render(request, "00-工步/03-运行工步.html", context=context)


def show_autocontrol_edit_page(request, dev_address):
    context = dict()

    context['dev_model'] = dev_model
    context['dev_address'] = dev_address

    return render(request, "00-工步/4-工步列表设置/step_set.html", context=context)


def show_open_device_page(request, dev_address):
    url = ['', dev_model, str(dev_address), '']
    return HttpResponseRedirect('/'.join(url))


def show_control_page_by_const(request, dev_address):
    """
    显示定值控制的控制页面
    :param request:
    :param dev_address:
    :return:
    """
    r = redis.Redis(connection_pool=cache.redis_pool)
    if request.method == 'POST':
        try:
            _ = request.POST['control']
            try:
                control(r, dev_address, '远程启动', int(request.POST['远程启动']))
            except:
                pass

            try:
                control(r, dev_address, '远程停止', int(request.POST['远程停止']))
            except:
                pass

            try:
                control(r, dev_address, '远程内外循环切换', int(request.POST['远程内外循环切换']))
            except:
                pass
        except:
            control(r, dev_address, '远程定值程序模式选择', 0)
            control(r, dev_address, '远程定值温度设定', float(request.POST['远程定值温度设定']))
            control(r, dev_address, '远程流量设定', float(request.POST['远程流量设定']))
        return HttpResponseRedirect(request.path)

    context = dict()
    context['control_method'] = 'const'
    context['dev_model'] = dev_model
    context['dev_address'] = dev_address
    yaotiao_path = "%s:%d:设置参数-读出" % (dev_model, dev_address)
    txt_yaotiao = r.get(yaotiao_path)
    if txt_yaotiao:
        context['control'] = json.loads(txt_yaotiao)
    else:
        context['control'] = None

    return render(request, "01-天硕/07-控制面板-定值模式.html", context=context)


def show_control_page_by_program(request, dev_address):
    """
    显示程序控制页面
    :param request:
    :param dev_address:
    :return:
    """
    r = redis.Redis(connection_pool=cache.redis_pool)
    if request.method == 'POST':
        try:
            _ = request.POST['control']
            try:
                control(r, dev_address, '远程启动', int(request.POST['远程启动']))
            except:
                pass

            try:
                control(r, dev_address, '远程停止', int(request.POST['远程停止']))
            except:
                pass

            try:
                control(r, dev_address, '远程内外循环切换', int(request.POST['远程内外循环切换']))
            except:
                pass
        except:
            control(r, dev_address, '远程定值程序模式选择', 1)
            control(r, dev_address, '远程流量设定', float(request.POST['远程流量设定']))
            control(r, dev_address, '远程运行程序号', int(request.POST['远程运行程序号']))
        return HttpResponseRedirect(request.path)

    context = dict()
    context['dev_model'] = dev_model
    context['dev_address'] = dev_address
    context['control_method'] = 'program'
    yaotiao_path = "%s:%d:设置参数-读出" % (dev_model, dev_address)
    txt_yaotiao = r.get(yaotiao_path)
    if txt_yaotiao:
        context['control'] = json.loads(txt_yaotiao)
    else:
        context['control'] = None

    return render(request, "01-天硕/08-控制面板-程序模式.html", context=context)


def show_control_page_by_manual(request, dev_address):
    r = redis.Redis(connection_pool=cache.redis_pool)
    if request.method == 'POST':
        try:
            _ = request.POST['control']
            try:
                control(r, dev_address, '远程内外循环切换', int(request.POST['远程内外循环切换']))
            except:
                pass

            try:
                control(r, dev_address, '远程排汽加液_启动循环泵', int(request.POST['远程排汽加液_启动循环泵']))
            except:
                pass
        except:
            control(r, dev_address, '远程定值程序模式选择', 1)
            control(r, dev_address, '远程流量设定', float(request.POST['远程流量设定']))
            control(r, dev_address, '远程强制控制加热器', float(request.POST['远程强制控制加热器']))
        return HttpResponseRedirect(request.path)

    context = dict()
    context['dev_model'] = dev_model
    context['dev_address'] = dev_address
    context['control_method'] = 'manual'
    yaotiao_path = "%s:%d:设置参数-读出" % (dev_model, dev_address)
    txt_yaotiao = r.get(yaotiao_path)
    if txt_yaotiao:
        context['control'] = json.loads(txt_yaotiao)
    else:
        context['control'] = None

    return render(request, "01-天硕/09-控制面板-强制加热模式.html", context=context)


# Create your views here.
urlpatterns = [
    path("<int:dev_address>/", show_dashboard_page),
    path("<int:dev_address>/profile/", show_device_basic_infomation_page),
    path("<int:dev_address>/open/", show_open_device_page),

    path("<int:dev_address>/yaoxin/", show_yaoxin_page),
    path("<int:dev_address>/yaoce/", show_yaoce_page),
    path("<int:dev_address>/yaoce/json/", show_yaoce_json),

    path("<int:dev_address>/yaotiao/", show_yaotiao_page),
    path("<int:dev_address>/control/", show_control_page_by_const),
    path("<int:dev_address>/control/const/", show_control_page_by_const),
    path("<int:dev_address>/control/program/", show_control_page_by_program),
    path("<int:dev_address>/control/manual/", show_control_page_by_manual),
    path("<int:dev_address>/control/auto/", show_autocontrol_page),

    path("<int:dev_address>/yaokong/", show_yaokong_page),
    path("<int:dev_address>/autocontrol/", show_autocontrol_page),
    path("<int:dev_address>/autocontrol/edit/", show_autocontrol_edit_page),
]
urls = (urlpatterns, "tianshuo", "tianshuo")
