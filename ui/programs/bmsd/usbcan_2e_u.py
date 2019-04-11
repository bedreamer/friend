# -*- coding: utf8 -*-
import os
import struct
from ctypes import *


class CANFrame(object):
    def __init__(self, id, tsp, data, size=None):
        self.id = id
        self.tsp = tsp
        self.bytes_data = struct.pack("B" * len(data), *data)

        if isinstance(data, list) or isinstance(data, tuple):
            self.data = data
        else:
            self.data = list(data)[: size]

    def __str__(self):
        data = " ".join(["%02X" % data for data in self.data])
        sid = "%08X:" % self.id
        return "".join([str(self.tsp), " ", sid, ' [', data, ']'])


class USBCAN_2E_U:
    model_name = 'USBCAN-2E-U'
    model_type = 21
    nr_channel = 2
    bps_map = {
        '5Kbps': c_uint32(0x1c01c1),
        '10Kbps': c_uint32(0x1c00e0),
        '20Kbps': c_uint32(0x1600b3),
        '50Kbps': c_uint32(0x1c002c),
        '100Kbps': c_uint32(0x160023),
        '125Kbps': c_uint32(0x1c0011),
        '250Kbps': c_uint32(0x1c0008),
        '500Kbps': c_uint32(0x060007),
        '800Kbps': c_uint32(0x060004),
        '1000Kbps': c_uint32(0x060003),
    }


# CAN硬件结构体
class _VCI_BOARD_INFO(Structure):
    _fields_ = [('hw_Version', c_uint16),
                ('fw_Version', c_uint16),
                ('dr_Version', c_uint16),
                ('in_Version', c_uint16),
                ('irq_Num', c_uint16),
                ('can_Num', c_byte),
                ('str_Serial_num', c_char * 20),
                ('str_hw_Type', c_char * 40),
                ('Reserved', c_uint16 * 16)]


# CAN配置结构体
class _VCI_INIT_CONFIG(Structure):
    _fields_ = [('AccCode', c_ulong),
                ('AccMask', c_ulong),
                ('Reserved', c_ulong),
                ('Filter', c_ubyte),
                ('Timing0', c_ubyte),
                ('Timing1', c_ubyte),
                ('Mode', c_ubyte)]


class _VCI_CAN_OBJ(Structure):
    _fields_ = [('ID', c_uint),
                ('TimeStamp', c_uint),
                ('TimeFlag', c_uint8),
                ('SendType', c_uint8),
                ('RemoteFlag', c_uint8),
                ('ExternFlag', c_uint8),
                ('DataLen', c_uint8),
                ('Data', c_uint8 * 8),
                ('Reserved', c_uint8 * 3)]


class _VCI_FILTER_RECORD(Structure):
    _fields_ = [('ExtFrame', c_uint),
                ('Start', c_uint),
                ('End', c_uint)]


class _VCI_ERR_INFO(Structure):
    _fields_ = [('ErrCode', c_uint),
                ('Passiv_ErrData', c_uint8 * 3),
                ('ArLost_ErrData', c_uint8)]


# 动态库名称, 需要放在当前脚本目录
_zlg_dll_file_name = ''.join([os.path.dirname(__file__), '/driver/ControlCAN.dll'])

# dll 句柄，由windll.LoadLibrary返回
# 这里用cdll而不用windll的原因是函数声明方式不同
# 解释参见: https://blog.csdn.net/jiangxuchen/article/details/8741613
_zlg_dll = windll.LoadLibrary(_zlg_dll_file_name)

_token_name_can_device = "can device"
_token_name_can_channel = "can device channel"


def c_open_device(devtype, devidx):
    global _zlg_dll

    return _zlg_dll.VCI_OpenDevice(devtype, devidx, 0)


def c_get_error_info(devtype, devidx, channel_number):
    error = _VCI_ERR_INFO()
    success = _zlg_dll.VCI_ReadErrInfo(devtype, devidx, channel_number, pointer(error))

    if success:
        print("ErrCode=", error.ErrCode)
        print("Passiv_ErrData=", error.Passiv_ErrData[0], error.Passiv_ErrData[1], error.Passiv_ErrData[2])
        print("ArLost_ErrData=", error.ArLost_ErrData)
        return error

    print("读取错误信息失败....")
    return None


def is_device_online(devtype, devidx):
    global _zlg_dll

    info = _VCI_BOARD_INFO()
    status = _zlg_dll.VCI_ReadBoardInfo(devtype, devidx, pointer(info))

    return True if status == 1 else False


def c_close_device(devtype, devidx):
    global _zlg_dll

    # 关闭设备之前必须将关联的通道一并关闭, 做到资源主动回收
    return True if 0 == _zlg_dll.VCI_CloseDevice(devtype, devidx) else False


def c_open_channel(devtype, devidx, channel_number, bps, work_mode, filter_id_pair_list):
    global _zlg_dll
    global _bps_table

    # 设置波特率
    bps_config_data = USBCAN_2E_U.bps_map[bps]
    status = _zlg_dll.VCI_SetReference(devtype, devidx, channel_number, 0, pointer(bps_config_data))
    if status != 1:
        print("set bps to", bps, "failed!")
        return 0
    else:
        print("set bps to", bps, "successed!")

    # 初始化设备
    ic = _VCI_INIT_CONFIG()
    ic.Mode = work_mode
    status = _zlg_dll.VCI_InitCAN(devtype, devidx, channel_number, pointer(ic))
    if status != 1:
        print("configure failed, dev, dev-idx, channel-idx", devtype, devidx)
        return 0

    # 设置过滤器
    id_range_filter = _VCI_FILTER_RECORD()
    for id_begin, id_end in filter_id_pair_list:
        begin, end = min(id_begin, id_end), max(id_begin, id_end)

        id_range_filter.ExtFrame = 1 if begin & 0x1FFF8000 > 0 else 0
        id_range_filter.Start = begin
        id_range_filter.End = end

        success = _zlg_dll.VCI_SetReference(devtype, devidx, channel_number, 1, pointer(id_range_filter))
        print("1", success)
        success = _zlg_dll.VCI_SetReference(devtype, devidx, channel_number, 2, c_void_p(0))
        print("2", success)

    # 启动设备
    status = _zlg_dll.VCI_StartCAN(devtype, devidx, channel_number)
    if status != 1:
        print("start channel", channel_number, "failed!")
        return 0
    else:
        print("start channel", channel_number, "successed!")

    # 打开通道后先清空缓冲区
    _zlg_dll.VCI_ClearBuffer(devtype, devidx, channel_number)


def c_clear_cache(devtype, devidx, channel_number):
    global _zlg_dll
    return True if 0 == _zlg_dll.VCI_ClearBuffer(devtype, devidx, channel_number) else False


def c_get_cache_counter(devtype, devidx, channel_number):
    global _zlg_dll
    return _zlg_dll.VCI_GetReceiveNum(devtype, devidx, channel_number)


def c_get_frame(devtype, devidx, channel_number, count, wait_ms):
    global _zlg_dll

    CAN_OBJ_ARRY_TYPE = _VCI_CAN_OBJ * count
    buffer_list = CAN_OBJ_ARRY_TYPE()

    read_count = _zlg_dll.VCI_Receive(devtype, devidx, channel_number, pointer(buffer_list), count, wait_ms)
    if read_count in (0xffffffff, -1, 0):
        error = c_get_error_info(devtype, devidx, channel_number)
        print(error)
        return list()

    return [CANFrame(id=obj.ID, tsp=obj.TimeStamp, data=obj.Data, size=obj.DataLen) for obj in buffer_list]


def c_send_frame(devtype, devidx, channel_number, frames_list):
    global _zlg_dll

    count = 0
    for frame in frames_list:
        o = _VCI_CAN_OBJ()
        o.ID = frame.id
        o.SendType = 0
        o.RemoteFlag = 0
        o.ExternFlag = 1 if frame.id & 0x1FFF8000 > 0 else 0
        o.DataLen = len(frame.data)

        if len(frame.data) < 8:
            frame.data.extend([0] * (8 - len(frame.data)))
        elif len(frame.data) > 8:
            frame.data = frame.data[:8]
        else:
            pass
        o.Data = tuple(frame.data)
        status = _zlg_dll.VCI_Transmit(devtype, devidx, channel_number, pointer(o), 1)
        if status == 1:
            count += 1

    return count
