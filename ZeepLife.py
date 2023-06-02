import datetime
import os
import sys
import random

import pymysql
import yaml
import redis
import requests


def myPrint(info, grade=0):
    nowDate = lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if grade == 0:
        content = "[%s] info %s" % (nowDate(), info)
    elif grade == 1:
        content = "[%s] error %s" % (nowDate(), info)
    elif grade == 2:
        content = "[%s] warning %s" % (nowDate(), info)
    else:
        content = "[%s] unknown %s" % (nowDate(), info)
    log_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], "ZeepLife.log")
    log = content + '\n'
    print(content)
    with open(log_dir, 'a+') as f:
        f.write(log)


class ZeeLife(object):
    def __init__(self):
        # 加载配置文件
        config_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.yaml")
        try:
            config_content = open(config_dir)
            self.config_info = yaml.load(config_content.read(), Loader=yaml.FullLoader)
            config_content.close()
        except FileNotFoundError:
            myPrint(grade=1, info="Configuration file does not exist, program exits. %s" % config_dir)
            sys.exit()
        except yaml.scanner.ScannerError:
            myPrint(grade=1, info="Configuration file loading error, please check the configuration file format.")
            sys.exit()

        # 加载数据库
        try:
            self.redis = redis.Redis(
                host=str(self.config_info.get("db_redis").get("host")),
                port=int(self.config_info.get("db_redis").get("port")),
                password=str(self.config_info.get("db_redis").get("password")),
                db=int(self.config_info.get("db_redis").get("db"))
            )
        except redis.ConnectionError as err:
            myPrint(grade=1, info="Redis server connection failed. Please check the redis, %s" % err)
            sys.exit()

        try:
            self.db = pymysql.connect(
                host=str(self.config_info.get("db_mysql").get("host")),
                port=int(self.config_info.get("db_mysql").get("port")),
                user=str(self.config_info.get("db_mysql").get("user")),
                password=str(self.config_info.get("db_mysql").get("password")),
                database=str(self.config_info.get("db_mysql").get("database")),
                charset=str(self.config_info.get("db_mysql").get("charset"))
            )
            self.cursor = self.db.cursor()
        except pymysql.err.OperationalError as err:
            myPrint(grade=1, info="MySQL server connection failed. Please check the database,%s" % err)

    def start_step(self, step):
        sql = "SELECT user_agant FROM headers ORDER BY RAND() limit 1;"
        self.cursor.execute(sql)
        headers = {"User-Agent": self.cursor.fetchone()[0]}

        url = "https://apis.jxcxin.cn/api/mi"

        params = {
            "user": self.config_info.get("user_info").get("username"),
            "password": self.config_info.get("user_info").get("password"),
            "step": step
        }
        response = requests.get(headers=headers, url=url, params=params).json()

        if response.get("code") == "200":
            status = "success"
        else:
            status = "failed"

        nowDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sql = "INSERT INTO log(step, status, today, message) VALUE (%s,%s, %s, %s);"
        self.cursor.execute(sql, [step, status, nowDate, response["msg"]])
        self.db.commit()
        myPrint(info="Currently taking %d steps." % int(step))

    def step(self):
        # 根据配置文件随机获取每个时段需要刷新的步数
        try:
            minimum_steps = int(self.config_info.get("step").get("minimum_steps"))
            max_steps = int(self.config_info.get("step").get("max_steps"))
            steps = int(self.config_info.get("step").get("steps"))
        except ValueError:
            myPrint(grade=1, info="'step' error in configuration file, just numbers.")
            sys.exit()

        # 规划当前步数
        info = random.randint(minimum_steps, max_steps)
        key_name = "zeep_life:" + str(datetime.datetime.now().strftime('%Y%m%d'))
        status = self.redis.exists(key_name)
        if status == 0:
            # 不存在键值的情况分两种，一种是还未开始，一种是已经结束
            self.cursor.execute("SELECT COUNT(*) FROM log WHERE TO_DAYS(today) = TO_DAYS(NOW());")
            if self.cursor.fetchone()[0] == 0:
                steps_info = []
                for item in range(1, steps+1):
                    steps_info.append(int(info / steps) * item)
                for step in steps_info:
                    self.redis.lpush(key_name, step)
                myPrint(info="The plan for today's brush steps has been deployed!")
            else:
                myPrint(info="The task of the day has been completed.")
        else:
            self.start_step(self.redis.rpop(key_name))

    def main(self):
        step_info = self.step()

    def __del__(self):
        try:
            self.cursor.close()
            self.db.close()
        except AttributeError:
            pass