# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import redis
import json
import logging
import struct
import settings
import urllib.request


bms_data_cache_path = ":".join(["bms", 'userdefine', "运行数据"])
bms_data = dict()


def get_bms_definition(bms_model):
    url = ''.join(['http://' ,settings.web_host, ':', str(settings.web_port),
                   '/bms/query/', '?bms_name=', bms_model])
    f = urllib.request.urlopen(url)
    resolution_txt = f.read().decode('utf-8')

    return json.loads(resolution_txt)


bms_define = get_bms_definition(settings.bms_model)


def on_BMS_TempInfo(bits64):
    pack = dict()

    pack['TempMin'] = int(bits64[32:40][::-1], 2) - 40
    pack['TempMax'] = int(bits64[40:48][::-1], 2) - 40
    pack['TempAver'] = int(bits64[48:56][::-1], 2) - 40
    logging.debug(pack)

    global bms_data
    bms_data = dict(bms_data, **pack)
    r = redis.Redis(connection_pool=settings.redis_pool)
    r.set(bms_data_cache_path, json.dumps(bms_data, ensure_ascii=False, indent=2), ex=5)


filter_address = {
    0x364: on_BMS_TempInfo,
}


def get_filter_id_range_pairs_list():
    avr_id = bms_define['avr']['fid']
    max_id = bms_define['max']['fid']
    min_id = bms_define['min']['fid']

    return [(x, x) for x in {avr_id, max_id, min_id}]


def on_frame(fid, bytes_data):
    if fid not in filter_address:
        return

    if len(bytes_data) < 8:
        bytes_data += b'\x00' * (8 - len(bytes_data))

    interger = struct.unpack('<Q', bytes_data)[0]
    _bits64 = bin(interger)[2:]
    bits64 = '0' * (64 - len(_bits64)) + _bits64
    filter_address[fid](bits64[::-1])

