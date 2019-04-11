import redis
import time
import ui.com_redisd as redisd

redisd.start_process_if_not_exist()
time.sleep(1)
redis_pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=1)
