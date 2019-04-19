from django.shortcuts import render
from django.urls import path
from django.http import *
import codecs
import json
import os
import time


user_define_path = os.path.dirname(os.path.dirname(__file__)) + '/userdefine'
if os.path.exists(user_define_path) is False:
    os.mkdir(user_define_path)


def define_new_bms(request):
    if request.method == 'GET':
        return render(request, "01-手动添加BMS报文.html")

    bms_name = "UserDefine_" + request.POST['bms_name']
    segs = list()
    for i in ['1', '2', '3']:
        seg = dict()
        seg['fid'] = int(request.POST['fid_' + i], 16)
        seg['sb'] = int(request.POST['sb_' + i])
        seg['bl'] = int(request.POST['bl_' + i])
        seg['order'] = request.POST['order_' + i]
        seg['x'] = float(request.POST['x_' + i])
        seg['offset'] = float(request.POST['offset_' + i])
        seg['max'] = float(request.POST['max_' + i])
        seg['min'] = float(request.POST['min_' + i])
        segs.append(seg)

    bms_profile = {
        'name': bms_name,
        'born': time.strftime("%Y-%m-%d %H:%M:%S"),
        'avr': segs[0],
        'max': segs[1],
        'min': segs[2],
    }

    bms_profile_path = user_define_path + '/' + bms_name
    with codecs.open(bms_profile_path, mode='w', encoding='utf8') as file:
        json.dump(bms_profile, file, ensure_ascii=False, indent=2)

    try:
        next = request.GET['next']
    except:
        next = '/'

    return HttpResponseRedirect(next)


def get_user_define_bms():
    bms_list = list()
    for x in os.listdir(user_define_path):
        with codecs.open(user_define_path + '/' + x, encoding='utf8') as file:
            bms = json.load(file)
            bms_list.append(bms)
    return bms_list


def query_bms_as_json(request):
    bms_profile_path = user_define_path + '/' + request.GET['bms_name']
    try:
        with codecs.open(bms_profile_path, encoding='utf8') as file:
            bms = json.load(file)
        return JsonResponse(bms, safe=False)
    except:
        return JsonResponse(None, safe=False)


# Create your views here.
urlpatterns = [
    path("define/", define_new_bms),
    path("query/", query_bms_as_json),
]
urls = (urlpatterns, "bms", "bms")
