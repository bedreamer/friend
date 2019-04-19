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
    url = ''.join(['http://', settings.web_host, ':', str(settings.web_port), '/bms/query/', '?bms_name=', bms_model])
    f = urllib.request.urlopen(url)
    resolution_txt = f.read().decode('utf-8')
    return json.loads(resolution_txt)


bms_define = get_bms_definition(settings.bms_model)
bms_fid_set = {
    bms_define['avr']['fid'],
    bms_define['max']['fid'],
    bms_define['min']['fid'],
}


def _parse_field_in_64bits(field, name, bits64):
    bb = field['sb']
    eb = bb + field['bl']
    x = field['x']
    offset = field['offset']

    value = int(bits64[bb:eb][::-1], 2) * x + offset
    return {name: value}


def on_parse_bms_avg_temp(bits64):
    return _parse_field_in_64bits(bms_define['avr'], 'TempAver', bits64)


def on_parse_bms_min_temp(bits64):
    return _parse_field_in_64bits(bms_define['min'], 'TempMin', bits64)


def on_parse_bms_max_temp(bits64):
    return _parse_field_in_64bits(bms_define['max'], 'TempMax', bits64)


def get_filter_id_range_pairs_list():
    avr_id = bms_define['avr']['fid']
    max_id = bms_define['max']['fid']
    min_id = bms_define['min']['fid']

    id_ranges_list = [(x, x) for x in {avr_id, max_id, min_id}]
    return id_ranges_list


def on_frame(fid, bytes_data):
    if fid not in bms_fid_set:
        return

    if len(bytes_data) < 8:
        bytes_data += b'\x00' * (8 - len(bytes_data))

    interger = struct.unpack('<Q', bytes_data)[0]
    _bits64 = bin(interger)[2:]
    bits64 = '0' * (64 - len(_bits64)) + _bits64

    package = dict()

    if fid == bms_define['avr']['fid']:
        pack = on_parse_bms_avg_temp(bits64)
        dict(package, **pack)

    if fid == bms_define['avr']['max']:
        pack = on_parse_bms_max_temp(bits64)
        dict(package, **pack)

    if fid == bms_define['avr']['min']:
        pack = on_parse_bms_min_temp(bits64)
        dict(package, **pack)

    global bms_data
    bms_data = dict(bms_data, **package)
    r = redis.Redis(connection_pool=settings.redis_pool)
    r.set(bms_data_cache_path, json.dumps(bms_data, ensure_ascii=False, indent=2), ex=5)
