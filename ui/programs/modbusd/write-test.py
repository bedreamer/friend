import redis
import json


redis_pool = redis.ConnectionPool(host="192.168.1.42", port=6379, db=1)
r = redis.Redis(connection_pool=redis_pool)


value = dict()
print("远程定值温度设定...")
value["远程定值温度设定"] = 35
r.lpush("1:设置参数-写入", json.dumps(value, ensure_ascii=False, indent=2))
input("按回车继续.....")


value = dict()
print("远程流量设定...")
value["远程流量设定"] = 35
r.lpush("1:设置参数-写入", json.dumps(value, ensure_ascii=False, indent=2))
input("按回车继续.....")


value = dict()
print("远程强制控制加热器...")
value["远程强制控制加热器"] = 35
r.lpush("1:设置参数-写入", json.dumps(value, ensure_ascii=False, indent=2))
input("按回车继续.....")


value = dict()
print("远程运行程序号...")
value["远程运行程序号"] = 2
r.lpush("1:设置参数-写入", json.dumps(value, ensure_ascii=False, indent=2))
input("按回车继续.....")


value = dict()
print("远程启动...")
value["远程启动"] = 1
r.lpush("1:设置参数-写入", json.dumps(value, ensure_ascii=False, indent=2))
input("按回车继续.....")


value = dict()
print("远程定值程序模式选择...")
value["远程定值程序模式选择"] = 1
r.lpush("1:设置参数-写入", json.dumps(value, ensure_ascii=False, indent=2))
input("按回车继续.....")


value = dict()
print("远程排汽加液_启动循环泵...")
value["远程排汽加液_启动循环泵"] = 1
r.lpush("1:设置参数-写入", json.dumps(value, ensure_ascii=False, indent=2))
input("按回车继续.....")


value = dict()
print("远程内外循环切换...")
value["远程内外循环切换"] = 1
r.lpush("1:设置参数-写入", json.dumps(value, ensure_ascii=False, indent=2))
input("按回车继续.....")


value = dict()
print("远程停止...")
value["远程停止"] = 1
r.lpush("1:设置参数-写入", json.dumps(value, ensure_ascii=False, indent=2))
input("按回车继续.....")
