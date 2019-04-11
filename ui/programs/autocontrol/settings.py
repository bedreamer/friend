# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import redis
import optparse


parser = optparse.OptionParser(usage="usage:%prog [-option arg] ...")
parser.add_option('-m', '--dev-model', default=None, help="指定一个MODBUS设备型号")
parser.add_option('-a', '--dev-address', default=1, type='int', help="MODBUS设备地址")
parser.add_option('-b', '--bms-model', default=None, help="指定BMS设备的型号")
parser.add_option('-e', '--entry', default=None, help="指定工步运行的入口名")
parser.add_option("-w", "--web-host", default='127.0.0.1', help="指定web服务的地址")
parser.add_option("-t", "--web-port", default=8000, type='int', help="指定web服务的端口")
parser.add_option('-r', '--redis-host', default='127.0.0.1', help="指定Redis数据库的地址")
parser.add_option('-p', '--redis-port', dest='redis_port', type='int', default=6379, help="指定Redis数据库的服务端口")
parser.add_option('-d', '--redis-database', dest='redis_database', type='int', default=1, help="指定Redis数据库入口")
_options, _arguments = parser.parse_args()

_opt_modbus_dev_model = _options.dev_model
_opt_modbus_dev_address = _options.dev_address
_opt_bms_model = _options.bms_model

_opt_solution_entry = _options.entry

_opt_redis_address = _options.redis_host
_opt_redis_port = _options.redis_port
_opt_redis_database = _options.redis_database

# MODBUS设备型号
modbus_dev_model = _opt_modbus_dev_model
if modbus_dev_model is None:
    print("需要提供modbus设备的型号")
    exit(1)

# BMS 设备型号
bms_model = _opt_bms_model
if bms_model is None:
    print("需要提供bms设备型号")
    exit(1)

# 工步运行入口
solution_entry = _opt_solution_entry
if solution_entry is None:
    print("需要提供工步入口名")
    exit(1)

# WEB 服务地址
web_host = _options.web_host
# WEB 服务端口
web_port = _options.web_port

# MODBUS设备地址
modbus_dev_address = _opt_modbus_dev_address

# redis 连接池
redis_pool = redis.ConnectionPool(host=_opt_redis_address, port=_opt_redis_port, db=_opt_redis_database)
