# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import redis
import json
import logging
import struct
import settings


bms_data_cache_path = ":".join(["bms", settings.bms_model, "运行数据"])
bms_data = dict()


def on_BMS_TempInfo(bits64):
    pack = dict()

    pack['BMS_Batt_TempMin'] = int(bits64[32:40][::-1], 2) - 40
    pack['BMS_Batt_TempMax'] = int(bits64[40:48][::-1], 2) - 40
    pack['BMS_Batt_TempAver'] = int(bits64[48:56][::-1], 2) - 40
    logging.debug(pack)

    global bms_data
    bms_data = dict(bms_data, **pack)
    r = redis.Redis(connection_pool=settings.redis_pool)
    r.set(bms_data_cache_path, json.dumps(bms_data, ensure_ascii=False, indent=2), ex=5)


filter_address = {
    0x364: on_BMS_TempInfo,
}


def get_filter_id_range_pairs_list():
    return [
        (0x364, 0x364),
    ]


def on_frame(fid, bytes_data):
    if fid not in filter_address:
        return

    if len(bytes_data) < 8:
        bytes_data += b'\x00' * (8 - len(bytes_data))

    interger = struct.unpack('<Q', bytes_data)[0]
    _bits64 = bin(interger)[2:]
    bits64 = '0' * (64 - len(_bits64)) + _bits64
    filter_address[fid](bits64[::-1])

