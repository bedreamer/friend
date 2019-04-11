# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import logging
import urllib.request
import json
import time
import redis
import datetime
import settings


class Solution:
    def __init__(self, entry_name, solution_json, dev_model, dev_address, bms_model):
        self.entry_name = entry_name
        self.solution_json = solution_json
        self.dev_model = dev_model
        self.dev_address = dev_address
        self.bms_model = bms_model
        self.step_idx = sorted([int(x[4:]) for x in self.solution_json])

        # 自动控制心跳
        self.heart_beat_path = 'autocontrol:heartbeat'
        # 自动控制工步当前状态
        self.solution_status_path = 'autocontrol:status'
        # modbus设备数据路径
        self.newline_data_path = ':'.join([self.dev_model, str(self.dev_address), '运行数据'])
        # modbus设备控制路径
        self.newline_control_path = ':'.join([self.dev_model, str(self.dev_address), "设置参数-写入"])
        # bms设备数据路径
        self.bms_data_path = ':'.join(['bms', self.bms_model, '运行数据'])

        self.newline = None
        self.bms = None
        self.step = None

    def control(self, r, name, value):
        control = dict()
        control[name] = value
        r.rpush(self.newline_control_path, json.dumps(control, ensure_ascii=False, indent=2))

    # 工步切入处理, 没切换一次，执行一次
    def step_switch_in(self, r, step_name):
        self.step = self.solution_json[step_name]
        self.step['name'] = step_name

        # 总切换次数
        try:
            self.step['loop'] += 1
        except KeyError:
            self.step['loop'] = 1

        now = datetime.datetime.now()
        # 当前循环次数
        self.step['count'] = 0
        # 激活时戳
        self.step['born'] = time.mktime(now.timetuple())
        # 激活日期时间
        self.step['active'] = now.strftime("%Y-%m-%d %H:%M:%S")

        logging.info("switch into step: {}".format(step_name))

        # 当工步激活后，立即设置工步状态三秒过期，保证这个数据是最新的
        r.set(self.solution_status_path, json.dumps(self.step, ensure_ascii=False, indent=2), ex=3)

        if self.step['mode'] == '自动模式':
            # 0 为定值模式，1为程序模式
            self.control(r, '远程定值程序模式选择', 0)
            # 0 为设备内部循环，1为设备外部循环
            self.control(r, '远程内外循环切换', 1)

            try:
                self.control(r, '远程定值温度设定', float(self.step['wendu']))
            except:
                pass

            try:
                self.control(r, '远程流量设定', float(self.step['liuliang']))
            except:
                pass

            try:
                self.control(r, '远程强制控制加热器', float(self.step['jiaregonglv']))
            except:
                pass

            self.control(r, '远程启动', 1)
        elif self.step['mode'] == '循环模式':
            # 0 为定值模式，1为程序模式
            self.control(r, '远程定值程序模式选择', 0)

            try:
                self.control(r, '远程流量设定', float(self.step['liuliang']))
            except:
                pass

            # 0 为设备内部循环，1为设备外部循环
            self.control(r, '远程内外循环切换', 1)

            # 启动循环泵， 1启动， 0关闭
            self.control(r, '远程排汽加液_启动循环泵', 1)
        elif self.step['mode'] == '加热模式':
            # 0 为定值模式，1为程序模式
            self.control(r, '远程定值程序模式选择', 0)

            try:
                self.control(r, '远程定值温度设定', float(self.step['wendu']))
            except:
                pass

            try:
                self.control(r, '远程流量设定', float(self.step['liuliang']))
            except:
                pass

            try:
                self.control(r, '远程强制控制加热器', float(self.step['jiaregonglv']))
            except:
                pass

            # 0 为设备内部循环，1为设备外部循环
            self.control(r, '远程内外循环切换', 1)

            # 启动循环泵， 1启动， 0关闭
            self.control(r, '远程排汽加液_启动循环泵', 1)
        elif self.step['mode'] == '制冷模式':
            # 0 为定值模式，1为程序模式
            self.control(r, '远程定值程序模式选择', 0)

            try:
                self.control(r, '远程定值温度设定', float(self.step['wendu']))
            except:
                pass

            try:
                self.control(r, '远程流量设定', float(self.step['liuliang']))
            except:
                pass

            # 0 为设备内部循环，1为设备外部循环
            self.control(r, '远程内外循环切换', 1)
            self.control(r, '远程启动', 1)
        elif self.step['mode'] == '待机模式':
            self.control(r, '远程停止', 1)
        else:
            logging.error("无法支持的模式:" + self.step['mode'])

    def step_switch_out(self, r, step_name, next_name=None):
        # 工步切出处理
        step = self.solution_json[step_name]
        try:
            next_step = self.solution_json[next_name]
        except:
            next_step = {'mode': "invalid mode"}

        if step['mode'] != next_step['mode']:
            diff_mode = True
        else:
            diff_mode = False

        logging.info("switch out step: {}".format(step_name))
        if step['mode'] == '自动模式' and diff_mode is True:
            self.control(r, '远程停止', 1)
        elif step['mode'] == '循环模式' and diff_mode is True:
            # 启动循环泵， 1启动， 0关闭
            self.control(r, '远程排汽加液_启动循环泵', 0)
        elif step['mode'] == '加热模式' and diff_mode is True:
            # 关闭加热器
            self.control(r, '远程强制控制加热器', 0)
            # 启动循环泵， 1启动， 0关闭
            self.control(r, '远程排汽加液_启动循环泵', 0)
        elif step['mode'] == '制冷模式' and diff_mode is True:
            self.control(r, '远程停止', 1)
        elif step['mode'] == '待机模式':
            self.control(r, '远程停止', 1)
        elif diff_mode is False:
            logging.info("下一工步模式相同，不作处理..")
        else:
            self.control(r, '远程停止', 1)
            logging.error("无法支持的模式:" + step['mode'], "自动停机")

    def get_all_data(self, r):
        # 获取bms数据和受控设备数据
        try:
            self.bms = json.loads(r.get(self.bms_data_path))
        except:
            pass

        self.newline = json.loads(r.get(self.newline_data_path))

    def preprocess(self, x):
        """预处理X，返回一个合理的值"""
        if x == 'True':
            return True

        if x == 'False':
            return False

        if x == 'self.loop':
            return self.step['loop']

        if x.find('newline.') == 0:
            key = x[8:]
            try:
                return self.newline[key]
            except KeyError:
                logging.error("判断条件错误")
                return None

        if x.find('bms.') == 0:
            key = x[4:]
            try:
                return self.bms[key]
            except KeyError:
                logging.error("判断条件错误")
                return None

        if isinstance(x, float):
            return x

        if isinstance(x, int):
            return x

        if isinstance(x, bool):
            return x

        if isinstance(x, str):
            return float(x)

        return None

    def get_true_auto_next(self, step_name):
        number = int(step_name[4:]) + 1
        while True:
            # 处理编号空泡，例如step1, step2, step4, step6, 其中step3, step5就是空泡，这些空泡导致编号无法连续出现
            if number in self.step_idx:
                break

            if number > max(self.step_idx):
                number = None
                break

        return number

    def update_current_step(self, r):
        # 更新当前工步状态
        now = time.time()
        duration = now - self.step['born']
        self.step['duration'] = round(duration, 2)
        self.step['count'] += 1

        # 设置工步状态三秒过期，保证这个数据是最新的
        r.set(self.solution_status_path, json.dumps(self.step, ensure_ascii=False, indent=2), ex=3)

        if duration >= int(self.step['ttl']) and self.step['ttl'] > 0:
            # 工步因产生超时，发生切换
            next_step_name = self.step['true']

            if next_step_name == '$auto':
                # 通知切出事件
                number = self.get_true_auto_next(self.step['name'])
                if number is None:
                    next_step_name = None
                else:
                    next_step_name = 'step%d' % number

            self.step_switch_out(r, self.step['name'], next_step_name)
            if next_step_name is None:
                self.step = None
                return

            self.step_switch_in(r, next_step_name)
            return

        _compare = {
            '>': lambda a, b: a > b,
            '>=': lambda a, b: a >= b,
            '<': lambda a, b: a < b,
            '<=': lambda a, b: a <= b,
            '!=': lambda a, b: a != b,
            '==': lambda a, b: a == b,
            'and': lambda a, b: a and b,
            'or': lambda a, b: a or b
        }

        _a, c1, _b, relation, _e, c2, _f = self.step['tiaojian']

        if '' not in {_a, c1, _b, relation, _e, c2, _f}:
            # a > b and c < d 型
            a, b = self.preprocess(_a), self.preprocess(_b)
            e, f = self.preprocess(_e), self.preprocess(_f)

            if None in {a, b, e, f}:
                logging.error("无效的比较条件")
                self.step = None
                return

            if c1 not in _compare or c2 not in _compare or relation not in _compare:
                logging.error("无效的比较条件")
                self.step = None
                return

            c1_result = _compare[c1](a, b)
            c2_result = _compare[c2](e, f)

            result = _compare[relation](c1_result, c2_result)
        elif '' not in {_a, c1, _b}:
            # a > b 型
            a, b = self.preprocess(_a), self.preprocess(_b)
            if c1 not in _compare:
                logging.error("无效的比较条件")
                self.step = None
                return
            result = _compare[c1](a, b)
        elif _a != '':
            # x 型
            a = self.preprocess(_a)
            if a is None:
                logging.error("无效的比较条件")
                self.step = None
                return
            result = a
        else:
            # 无比较
            return

        if not result:
            next_step_name = self.step['false']
            if next_step_name == '$auto':
                # 条件为假，$auto不切换
                return
        else:
            next_step_name = self.step['true']

        if next_step_name == '$auto':
            number = self.get_true_auto_next(self.step['name'])
            if number is None:
                # 工步全部执行结束了
                self.step = None
                return

            next_step_name = 'step%d' % number

        self.step_switch_out(r, self.step['name'], next_step_name)
        self.step_switch_in(r, next_step_name)

    def run_forever(self):
        r = redis.Redis(connection_pool=settings.redis_pool)

        # 清除命令列表，避免产生设备误动作
        commands_path = "autocontrol:command"
        r.expire(commands_path, 0)

        # 激活入口工步
        self.step_switch_in(r, self.entry_name)

        # 停止原因
        stop_reason = "全部工步执行完成..."
        while self.step:
            # 获取最新的外部命令
            command_txt = r.lpop(commands_path)
            try:
                command = json.loads(command_txt)
                if command['command'] == 'stop':
                    stop_reason = "外部命令导致停止..."
                    break
            except:
                pass

            # 获取最新数据
            self.get_all_data(r)

            # 更新当前工步状态
            self.update_current_step(r)

            # 运行周期为1秒
            time.sleep(1)

        # 最后将设备关机
        self.control(r, '远程停止', 1)
        self.control(r, '远程强制控制加热器', 0)

        logging.info(stop_reason)


def get_solution_object(dev_model, bms_model):
    url = ''.join(['http://' ,settings.web_host, ':', str(settings.web_port),
                   '/v1.0/json/step/solution/device/', dev_model, '/bms/', bms_model, '/'])
    f = urllib.request.urlopen(url)
    resolution_txt = f.read().decode('utf-8')

    return json.loads(resolution_txt)


if __name__ == '__main__':
    FORMAT = '[%(levelname)s %(asctime)-15s] %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)

    solution_json = get_solution_object(settings.modbus_dev_model, settings.bms_model)
    if solution_json is None:
        logging.error("获取工步方案失败")
        exit(1)

    if settings.solution_entry not in solution_json['steps']:
        logging.error("没有找到指定的入口")
        exit(1)

    solution = Solution(settings.solution_entry,
                        solution_json['steps'],
                        settings.modbus_dev_model,
                        settings.modbus_dev_address,
                        settings.bms_model)
    solution.run_forever()
