# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import redis
import optparse


parser = optparse.OptionParser(usage="usage:%prog [-option arg] ...")
parser.add_option('-m', '--model', default=None, help="指定一个MODBUS设备型号")
parser.add_option('-a', '--address', default=1, type="int", help="指定MODBUS设备的地址, 范围1~255")
parser.add_option('-s', '--serial-host', default='127.0.0.1', help="指定一个串口的redirect服务器地址")
parser.add_option('-P', '--serial-port', default='7777', help="指定一个串口的redirect服务器端口")
parser.add_option('-r', '--redis-host', default='127.0.0.1', help="指定Redis数据库的地址")
parser.add_option('-p', '--redis-port', dest='redis_port', type='int', default=6379, help="指定Redis数据库的服务端口")
parser.add_option('-d', '--redis-database', dest='redis_database', type='int', default=1, help="指定Redis数据库入口")
_options, _arguments = parser.parse_args()

_opt_modbus_model = _options.model
_opt_serial_host = _options.serial_host
_opt_serial_port = _options.serial_port
_opt_modbus_dev_address = _options.address
_opt_redis_address = _options.redis_host
_opt_redis_port = _options.redis_port
_opt_redis_database = _options.redis_database

# MODBUS设备型号
modbus_model = _opt_modbus_model
if modbus_model is None:
    print("需要提供modbus设备的型号")
    exit(1)


# MODBUS设备地址
modbus_dev_address = _opt_modbus_dev_address

# 串口通讯端口
serial_port = ''.join(['socket://', _opt_serial_host, ':', _opt_serial_port, "?logging=debug"])

# redis 连接池
redis_pool = redis.ConnectionPool(host=_opt_redis_address, port=_opt_redis_port, db=_opt_redis_database)
