from django.shortcuts import render
from django.urls import path
from django.http import *
import redis
import json
import time
import ui.cache as cache


bms_model = "userdefine"
bms_data_path = ':'.join(['bms', bms_model, '运行数据'])


def get_judgement_conditions():
    values = [
        "TempMin",
        "TempMax",
        "TempAver",
    ]
    return {v: "bms." + v for v in values}


def get_data():
    try:
        r = redis.Redis(connection_pool=cache.redis_pool)
        return json.loads(r.get(bms_data_path))
    except:
        return None

