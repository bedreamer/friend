# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import redis
import logging
import optparse


parser = optparse.OptionParser(usage="usage:%prog [-option arg] ...")
parser.add_option('-b', '--bms-model', default=None, help="指定BMS设备的型号")

parser.add_option('-i', '--can-model', default=None, help="指定CAN设备的型号")
parser.add_option('-c', '--can-channel', default=0, type='int', help="指定BMS设备的型号")
parser.add_option('-s', '--can-bautrate', default=None, help="CAN通讯波特率")

parser.add_option('-r', '--redis-host', default='127.0.0.1', help="指定Redis数据库的地址")
parser.add_option('-p', '--redis-port', dest='redis_port', type='int', default=6379, help="指定Redis数据库的服务端口")
parser.add_option('-d', '--redis-database', dest='redis_database', type='int', default=1, help="指定Redis数据库入口")

parser.add_option("-w", "--web-host", default='127.0.0.1', help="指定web服务的地址")
parser.add_option("-t", "--web-port", default=8000, type='int', help="指定web服务的端口")
_options, _arguments = parser.parse_args()

_opt_bms_model = _options.bms_model

_opt_redis_address = _options.redis_host
_opt_redis_port = _options.redis_port
_opt_redis_database = _options.redis_database


# BMS 设备型号
bms_model = _opt_bms_model
if bms_model is None:
    logging.error("需要提供bms设备型号")
    exit(1)

# CAN 设备型号
can_model = _options.can_model
if can_model is None:
    logging.error("需要提供CAN设备型号")

# CAN 通道
can_channel = _options.can_channel

# CAN 波特率
can_bps = _options.can_bautrate
if can_bps is None:
    logging.error("需要指定CAN通讯波特率")


# WEB 服务地址
web_host = _options.web_host
# WEB 服务端口
web_port = _options.web_port


# redis 连接池
redis_pool = redis.ConnectionPool(host=_opt_redis_address, port=_opt_redis_port, db=_opt_redis_database)
