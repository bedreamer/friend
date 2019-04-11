# -*- coding: utf8 -*-
__version__ = "天硕版MODBUS通讯程序"


import logging
import channel
import struct
import redis
import json
import time
import settings


redis_pool = settings.redis_pool
dev_model = "tianshuo"


def initialize_device(dev_address):
    last_error_path = "%s:%d:lasterror" % (dev_model, dev_address)
    r = redis.Redis(connection_pool=redis_pool)
    r.expire(last_error_path, 0)


def init_all_registers(serial_channel, dev_address):
    pass


def read_all_coils_register(serial_channel, dev_address):
    last_error_path = "%s:%d:lasterror" % (dev_model, dev_address)
    r = redis.Redis(connection_pool=redis_pool)

    exception_code = [0x83]
    output_fault_alarm = channel.do_multiple_read_request(serial_channel, dev_address, 0x03, exception_code, 0x0009, 1)

    if not output_fault_alarm:
        logging.error("读取输出故障报警寄存器失败!")
        r.rpush(last_error_path, "读取输出故障报警寄存器失败!")
        raise ValueError

    logging.debug(output_fault_alarm)
    real_data = struct.unpack(">H", output_fault_alarm[3:5])[0]

    fault_alarm = dict()
    # bit0
    fault_alarm['加热器超温报警'] = real_data & 0x0001
    fault_alarm['压缩机排气温度高报警'] = real_data & 0x0002
    fault_alarm['压缩机低压保护'] = real_data & 0x0004
    fault_alarm['压缩机高压保护'] = real_data & 0x0008

    # bit4
    fault_alarm['电源故障相序错误指示'] = real_data & 0x0010

    # bit6
    fault_alarm['供液压力传感器故障'] = real_data & 0x0040
    fault_alarm['供液压力超压报警'] = real_data & 0x0080

    # bit8
    fault_alarm['回液压力传感器故障'] = real_data & 0x0100
    fault_alarm['供液流量超限报警'] = real_data & 0x0200
    fault_alarm['膨胀罐液位传感器故障'] = real_data & 0x0400
    fault_alarm['供液流量传感器故障'] = real_data & 0x0800

    logging.debug(fault_alarm)
    fault_alarm_register_path = "%s:%d:输出故障报警" % (dev_model, dev_address)
    r.set(fault_alarm_register_path, json.dumps(fault_alarm, ensure_ascii=False, indent=2), ex=3)

    working_status_bytes = channel.do_multiple_read_request(serial_channel, dev_address, 0x03, exception_code, 0x000B, 1)
    if not working_status_bytes:
        logging.error("读取机组运行状态寄存器失败!")
        r.rpush(last_error_path, "读取机组运行状态寄存器失败!")
        raise ValueError

    logging.debug(output_fault_alarm)
    real_data = struct.unpack(">H", working_status_bytes[3:5])[0]

    working_status = dict()
    # bit0
    working_status["加热器运行状态"] = real_data & 0x0001
    working_status["压缩机运行指示"] = real_data & 0x0002
    working_status["循环泵运行指示"] = real_data & 0x0004
    working_status["电动三通阀开关"] = real_data & 0x0008

    # bit4
    working_status["电动球阀"] = real_data & 0x0010
    working_status["通讯状态检测"] = real_data & 0x0020

    logging.debug(working_status)

    working_status_register_path = "%s:%d:机组运行状态" % (dev_model, dev_address)
    r.set(working_status_register_path, json.dumps(working_status, ensure_ascii=False, indent=2), ex=3)


def read_all_discrete_input_register(serial_channel, dev_address):
    pass


def read_all_input_register(serial_channel, dev_address):
    last_error_path = "%s:%d:lasterror" % (dev_model, dev_address)
    exception_code = [0x83]
    r = redis.Redis(connection_pool=redis_pool)

    input_register_0_10 = channel.do_multiple_read_request(serial_channel, dev_address, 0x03, exception_code, 0x0000, 11)
    if not input_register_0_10:
        logging.error("读取输入寄存器0-11失败!")
        r.rpush(last_error_path, "读取输入寄存器0-11失败!")
        raise ValueError

    logging.debug(input_register_0_10)
    values = dict()
    values["供液压力显示"] = struct.unpack(">H", input_register_0_10[3: 5])[0]/100.0
    values["回液压力显示"] = struct.unpack(">H", input_register_0_10[5: 7])[0]/100.0
    values["供液流量显示"] = struct.unpack(">H", input_register_0_10[7: 9])[0]/100.0
    values["膨胀罐液位显示"] = struct.unpack(">H", input_register_0_10[9: 11])[0]/100.0
    values["阀门开度显示"] = struct.unpack(">H", input_register_0_10[11: 13])[0]/100.0
    values["供液温度显示"] = struct.unpack(">H", input_register_0_10[13: 15])[0]/100.0
    values["排气温度显示"] = struct.unpack(">H", input_register_0_10[15: 17])[0]/100.0
    values["回液温度显示"] = struct.unpack(">H", input_register_0_10[17: 19])[0]/100.0
    _ = struct.unpack(">H", input_register_0_10[19: 21])[0]
    _ = struct.unpack(">H", input_register_0_10[21: 23])[0]
    values["冷凝液温度显示"] = struct.unpack(">H", input_register_0_10[23: 25])[0]/100.0

    logging.debug(values)

    running_data_path = "%s:%d:运行数据" % (dev_model, dev_address)
    r.set(running_data_path, json.dumps(values, ensure_ascii=False, indent=2), ex=3)


def read_all_holding_register(serial_channel, dev_address):
    last_error_path = "%s:%d:lasterror" % (dev_model, dev_address)
    exception_code = [0x83]
    r = redis.Redis(connection_pool=redis_pool)

    hold_register_15_24 = channel.do_multiple_read_request(serial_channel, dev_address, 0x03, exception_code, 0x000F, 9)
    if not hold_register_15_24:
        logging.error("读取输入寄存器15-24失败!")
        r.rpush(last_error_path, "读取输入寄存器15-24失败!")
        raise ValueError

    logging.debug(hold_register_15_24)
    parameters = dict()
    parameters["远程定值温度设定"] = struct.unpack(">H", hold_register_15_24[3: 5])[0]/100.0
    parameters["远程流量设定"] = struct.unpack(">H", hold_register_15_24[5: 7])[0]/100.0
    parameters["远程强制控制加热器"] = struct.unpack(">H", hold_register_15_24[7: 9])[0]/100.0
    parameters["远程运行程序号"] = struct.unpack(">H", hold_register_15_24[9: 11])[0]
    parameters["远程启动"] = struct.unpack(">H", hold_register_15_24[11: 13])[0]
    parameters["远程定值程序模式选择"] = struct.unpack(">H", hold_register_15_24[13: 15])[0]
    parameters["远程排汽加液_启动循环泵"] = struct.unpack(">H", hold_register_15_24[15: 17])[0]
    parameters["远程内外循环切换"] = struct.unpack(">H", hold_register_15_24[17: 19])[0]
    parameters["远程停止"] = struct.unpack(">H", hold_register_15_24[19: 21])[0]

    logging.debug(parameters)

    settings_parameters_path = "%s:%d:设置参数-读出" % (dev_model, dev_address)
    r.set(settings_parameters_path, json.dumps(parameters, ensure_ascii=False, indent=2), ex=3)


def write_all_custom_settings_register(serial_channel, dev_address):
    last_error_path = "%s:%d:lasterror" % (dev_model, dev_address)
    exception_code = [0x86]
    settings_parameters_path = "%s:%d:设置参数-写入" % (dev_model, dev_address)

    r = redis.Redis(connection_pool=redis_pool)
    result = r.lpop(settings_parameters_path)
    if result is None:
        return

    logging.debug(result)
    try:
        pack = json.loads(result)
    except:
        return

    try:
        display_value = float(pack["远程定值温度设定"]) * 100
        modbus_value = int(display_value)
        r = channel.do_single_write_request(serial_channel, dev_address, 0x06, exception_code, 0x000F, modbus_value)
        if not r:
            r.rpush(last_error_path, "写寄存器失败!")
            raise ValueError
        logging.info("远程定值温度设定：{}".format(modbus_value))
    except KeyError:
        pass

    try:
        display_value = float(pack["远程流量设定"]) * 100
        modbus_value = int(display_value)
        r = channel.do_single_write_request(serial_channel, dev_address, 0x06, exception_code, 0x0010, modbus_value)
        if not r:
            r.rpush(last_error_path, "写寄存器失败!")
            raise ValueError
        logging.info("远程流量设定：{}".format(modbus_value))
    except KeyError:
        pass

    try:
        display_value = pack["远程强制控制加热器"]
        modbus_value = int(display_value * 100)
        r = channel.do_single_write_request(serial_channel, dev_address, 0x06, exception_code, 0x0011, modbus_value)
        if not r:
            r.rpush(last_error_path, "写寄存器失败!")
            raise ValueError
        logging.info("远程强制控制加热器：{}".format(modbus_value))
    except KeyError:
        pass
    try:
        display_value = pack["远程运行程序号"]
        modbus_value = int(display_value)
        r = channel.do_single_write_request(serial_channel, dev_address, 0x06, exception_code, 0x0012, modbus_value)
        if not r:
            r.rpush(last_error_path, "写寄存器失败!")
            raise ValueError
        logging.info("远程运行程序号：{}".format(modbus_value))
    except KeyError:
        pass

    try:
        display_value = pack["远程定值程序模式选择"]
        modbus_value = int(display_value)
        r = channel.do_single_write_request(serial_channel, dev_address, 0x06, exception_code, 0x0014, modbus_value)
        if not r:
            r.rpush(last_error_path, "写寄存器失败!")
            raise ValueError
        logging.info("远程定值程序模式选择：{}".format(modbus_value))
    except KeyError:
        pass

    try:
        # 1 开 0 关
        display_value = pack["远程排汽加液_启动循环泵"]
        modbus_value = int(display_value)
        if modbus_value not in {0, 1}:
            raise KeyError("远程排汽加液控制值必须是0或1")

        r = channel.do_single_write_request(serial_channel, dev_address, 0x06, exception_code, 0x0015, modbus_value)
        if not r:
            r.rpush(last_error_path, "写寄存器失败!")
            raise ValueError
        logging.info("远程排汽加液_启动循环泵：{}".format(modbus_value))
    except KeyError:
        pass

    try:
        display_value = pack["远程内外循环切换"]
        modbus_value = int(display_value)
        if modbus_value not in {0, 1}:
            raise KeyError("远程内外循环切换控制值必须是0或1")

        r = channel.do_single_write_request(serial_channel, dev_address, 0x06, exception_code, 0x0016, modbus_value)
        if not r:
            r.rpush(last_error_path, "写寄存器失败!")
            raise ValueError
        logging.info("远程内外循环切换：{}".format(modbus_value))
    except KeyError:
        pass

    try:
        # 按1送0
        _ = pack["远程启动"]
        r = channel.do_single_write_request(serial_channel, dev_address, 0x06, exception_code, 0x0013, 1)
        if not r:
            r.rpush(last_error_path, "写寄存器失败!")
            raise ValueError

        time.sleep(1)

        r = channel.do_single_write_request(serial_channel, dev_address, 0x06, exception_code, 0x0013, 0)
        if not r:
            r.rpush(last_error_path, "写寄存器失败!")
            raise ValueError
        logging.info("远程启动")
    except KeyError:
        pass

    try:
        # 按1送0
        _ = pack["远程停止"]
        if not r:
            raise ValueError

        r = channel.do_single_write_request(serial_channel, dev_address, 0x06, exception_code, 0x0017, 1)
        if not r:
            r.rpush(last_error_path, "写寄存器失败!")
            raise ValueError

        time.sleep(1)

        r = channel.do_single_write_request(serial_channel, dev_address, 0x06, exception_code, 0x0017, 0)
        if not r:
            r.rpush(last_error_path, "写寄存器失败!")
            raise ValueError
        logging.info("远程停止")
    except KeyError:
        pass
