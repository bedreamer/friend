# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import settings
import logging
import usbcan_2e_u as usbcan
import time


zlg_usb_can = {
    "USBCAN-2_1": (4, 0),
    "USBCAN-2_2": (4, 1),
    "USBCAN-2E-U_1": (21, 0),
    "USBCAN-2E-U_2": (21, 1),
}

if __name__ == '__main__':
    FORMAT = '[%(levelname)s %(asctime)-15s] %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    
    bms = __import__("model_" + settings.bms_model)
    if settings.can_model not in zlg_usb_can:
        logging.error("不支持的型号", settings.can_model)
        exit(0)

    dev_type_number, dev_channel = zlg_usb_can[settings.can_model]
    dev_idx = 0
    if not usbcan.c_open_device(dev_type_number, dev_idx):
        logging.error("打卡设备失败!")
        exit(0)

    # 读数据帧的ID过滤范围
    filter_id_pair_list = bms.get_filter_id_range_pairs_list()
    # 设备工作模式
    mode_normal = 0
    model_listen = 1
    usbcan.c_open_channel(dev_type_number, dev_idx, dev_channel, settings.can_bps, mode_normal, filter_id_pair_list)

    receive_frame_count_once = 1
    receive_frame_delay_in_ms = 1000
    while True:
        frame_list = usbcan.c_get_frame(dev_type_number, dev_idx, dev_channel, receive_frame_count_once, receive_frame_delay_in_ms)
        for frame in frame_list:
            print(frame)
            bms.on_frame(frame.id, frame.bytes_data)
