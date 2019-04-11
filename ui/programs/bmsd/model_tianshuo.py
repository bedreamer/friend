# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import redis
import json
import logging
import struct
import settings


bms_data_cache_path = ":".join(["bms", settings.bms_model, "运行数据"])
bms_data = dict()


def on_BMS_battery_info(bits64):
    pack = dict()

    pack['BMS_BattVol'] = int(bits64[0:16][::-1], 2) * 0.05
    pack['BMS_BattCurr'] = int(bits64[16:32][::-1], 2) * 0.05 - 1600
    pack['BMS_BattSOC'] = int(bits64[32:40][::-1], 2) * 0.4
    pack['BMS_BattSOH'] = int(bits64[40:48][::-1], 2) * 0.4
    pack['BMS_EmergCutoffHVReq'] = int(bits64[48:50][::-1], 2)
    pack['BMS_PmtCutoffLVFb'] = int(bits64[50:52][::-1], 2)
    pack['BMS_SelfChkState'] = int(bits64[52:54][::-1], 2)
    pack['BMS_FaultLevel'] = int(bits64[54:56][::-1], 2)
    pack['BMS_NegRelaySts'] = int(bits64[56:58][::-1], 2)
    pack['BMS_HeatRelaySts_Reserved'] = int(bits64[58:60][::-1], 2)
    pack['BMS_ActWorkSts'] = int(bits64[60:64][::-1], 2)
    logging.debug(pack)

    global bms_data
    bms_data = dict(bms_data, **pack)
    r = redis.Redis(connection_pool=settings.redis_pool)
    r.set(bms_data_cache_path, json.dumps(bms_data, ensure_ascii=False, indent=2), ex=5)


def on_BMS_CHgTempInfo(bits64):
    pack = dict()

    pack['BMS_DCChgPosTemp'] = int(bits64[0:8][::-1], 2) - 40
    pack['BMS_DCChgNegTemp'] = int(bits64[8:16][::-1], 2) - 40
    pack['BMS_SlowChgPosTemp'] = int(bits64[16:24][::-1], 2) - 40
    pack['BMS_SlowChgNegTemp'] = int(bits64[24:32][::-1], 2) - 40
    logging.debug(pack)

    global bms_data
    bms_data = dict(bms_data, **pack)
    r = redis.Redis(connection_pool=settings.redis_pool)
    r.set(bms_data_cache_path, json.dumps(bms_data, ensure_ascii=False, indent=2), ex=5)


def on_BMS_HVIsolationInfo(bits64):
    pack = dict()

    pack['BMS_PosIsolationRes'] = int(bits64[0:16][::-1], 2)
    pack['BMS_NegIsolationRes'] = int(bits64[16:32][::-1], 2)
    pack['BMS_HVIsolationSts'] = int(bits64[32:35][::-1], 2)
    pack['BMS_IsolationFault'] = int(bits64[35:40][::-1], 2)
    pack['BMS_HVIsolationInfo_AliveCnt'] = int(bits64[56:64][::-1], 2)
    logging.debug(pack)

    global bms_data
    bms_data = dict(bms_data, **pack)
    r = redis.Redis(connection_pool=settings.redis_pool)
    r.set(bms_data_cache_path, json.dumps(bms_data, ensure_ascii=False, indent=2), ex=5)


def on_BMS_Min_MAX_CellTemp(bits64):
    pack = dict()

    pack['BMS_BattMinTemp1'] = int(bits64[0:8][::-1], 2) - 40
    pack['BMS_MinTemp1SnsNum'] = int(bits64[8:16][::-1], 2)
    pack['BMS_MinTemp1SnsNum'] = int(bits64[16:24][::-1], 2)
    pack['BMS_BattMaxTemp1'] = int(bits64[24:32][::-1], 2) - 40
    pack['BMS_MaxTemp1PackNum'] = int(bits64[32:40][::-1], 2)
    pack['BMS_MaxTemp1SnsNum'] = int(bits64[40:48][::-1], 2)
    pack['BMS_Cell_Avg_Temp'] = int(bits64[48:64][::-1], 2) - 40
    logging.debug(pack)

    global bms_data
    bms_data = dict(bms_data, **pack)
    r = redis.Redis(connection_pool=settings.redis_pool)
    r.set(bms_data_cache_path, json.dumps(bms_data, ensure_ascii=False, indent=2), ex=5)


def on_BMS_Min_MAX_CellVolt(bits64):
    pack = dict()

    pack['BMS_MinCellVolt'] = int(bits64[0:16][::-1], 2)
    pack['BMS_MinVoltCellNum'] = int(bits64[16:24][::-1], 2)
    pack['BMS_MinVolt1CellPackNum'] = int(bits64[24:32][::-1], 2)
    pack['BMS_MaxCellVolt'] = int(bits64[32:48][::-1], 2)
    pack['BMS_MaxVoltCellNum'] = int(bits64[48:56][::-1], 2)
    pack['BMS_MaxVoltCellPackNum'] = int(bits64[56:64][::-1], 2)
    logging.debug(pack)

    global bms_data
    bms_data = dict(bms_data, **pack)
    r = redis.Redis(connection_pool=settings.redis_pool)
    r.set(bms_data_cache_path, json.dumps(bms_data, ensure_ascii=False, indent=2), ex=5)


def on_BMS_ThermalManageInfo(bits64):
    pack = dict()

    pack['BMS_BattPackInCoolTemp'] = int(bits64[0:8][::-1], 2) - 40
    pack['BMS_BattPackOutCoolTemp'] = int(bits64[8:16][::-1], 2) - 40
    pack['BMS_Batty_ThermalMangeReq'] = int(bits64[16:20][::-1], 2)
    logging.debug(pack)

    global bms_data
    bms_data = dict(bms_data, **pack)
    r = redis.Redis(connection_pool=settings.redis_pool)
    r.set(bms_data_cache_path, json.dumps(bms_data, ensure_ascii=False, indent=2), ex=5)


filter_address = {
    0x18FA40F4: on_BMS_battery_info,
    0x18FA51F4: on_BMS_CHgTempInfo,
    0x18FA41F4: on_BMS_HVIsolationInfo,
    0x18FA48F4: on_BMS_Min_MAX_CellTemp,
    0x18FA4AF4: on_BMS_Min_MAX_CellVolt,
    0x18FA52F4: on_BMS_ThermalManageInfo
}


def get_filter_id_range_pairs_list():
    return [
        (0x18FA40F4, 0x18FA40F4),
        (0x18FA51F4, 0x18FA51F4),
        (0x18FA41F4, 0x18FA41F4),
        (0x18FA48F4, 0x18FA48F4),
        (0x18FA4AF4, 0x18FA4AF4),
        (0x18FA52F4, 0x18FA52F4),
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

