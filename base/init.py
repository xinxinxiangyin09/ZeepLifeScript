# 初始化所有基础环境

import sys
import re
import datetime
import os


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

    print(content)


class Init(object):
    def __init__(self):
        pass

    def py_version(self):
        # 检查Python版本是否兼容
        version = re.match("(\d+\.\d+.\d+)", sys.version).group()
        if version == "3.6.5":
            myPrint(info="Your Python version was personally tested by the author and you can successfully run the script !")
            return 0
        else:
            myPrint(grade=2, info="Your Python version was %s but need version was %s, inform you that the author of your Python version has not yet tested it !" % (version, "3.6.5"))
            return 1

    def pip(self):
        # 检查pip依赖
        myPrint(info="Staring upgrade pip version...")
        pip_list = os.popen("/root/.virtualenvs/py3env/bin/python3 -m pip list").read()
        pip_list = re.findall("(.*)\s+(\d.*\d)", pip_list)
        pip_list_content = []
        for pip in pip_list:
            pip_list_content.append({"name": pip[0].replace(" ", ''), "version": pip[1].replace(" ", "")})
        requirement = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "requirements.txt")
        with open(requirement, "r") as f:
            requirement_content = f.read()
        pip_list = re.findall("(.*)==(.*)", requirement_content)
        pip_list_content_new = []
        for pip in pip_list:
            pip_list_content_new.append({"name": pip[0].replace(" ", ''), "version": pip[1].replace(" ", "")})

        # print(len(pip_list_content), pip_list_content)
        # print(pip_list_content_new)

        def install_pip(name, version, new=True):
            if new is True:
                status = os.popen("/root/.virtualenvs/py3env/bin/python3 -m pip install %s==%s"  % (name, version)).read()
                if re.findall("Successfully installed (.*)-(.*)", status) is None:
                    myPrint(grade=1, info="%s not successfully installed, please check the version of %s" % (name, version))
                else:
                    return name,version
            else:
                status = os.popen("/root/.virtualenvs/py3env/bin/python3 -m pip uninstall -y %s" % name).read()
                if re.findall("Successfully uninstalled (.*)-(.*)", status) is None:
                    myPrint(grade=1, info="%s not successfully uninstalled, Please manually uninstall and reinstall the correct version %s" % (name, version))
                else:
                    return name,version
                status = os.popen("/root/.virtualenvs/py3env/bin/python3 -m pip install %s==%s" % (name, version)).read()
                if re.findall("Successfully uninstalled (.*)-(.*)", status) is None:
                    myPrint(grade=1, info="%s not successfully uninstalled, Please manually uninstall and reinstall the correct version %s" % (name, version))
                else:
                    return name,version

        for pip in pip_list_content_new:
            if pip in pip_list_content:
                myPrint(info="%s is installed，knowing version is %s, version matching and no action required." % (pip.get("name"), pip.get("version")))
            else:
                for item in pip_list_content:
                    if pip.get("name") == item.get("name"):
                        result = install_pip(name=pip.get("name"), version=pip.get("version"), new=False)
                        myPrint(grade=2, info="%s is installed, but version %s is not trying, This installation %s version %s." % (result[0], item.get("version"), result[0], result[1]))
                        break
                    else:
                        continue
                result = install_pip(name=pip.get("name"), version=pip.get("version"), new=True)
                myPrint(grade=2, info="%s is uninstalled, This installation %s version %s." % (result[0], result[0], result[1]))

    def db_init(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")
        try:
            import yaml
        except Exception:
            myPrint(info="The environment lacks dependencies %s and cannot load the yaml configuration file." % "PyYAML")
            sys.exit()

        try:
            f = open(config_path, 'r')
        except Exception:
            myPrint(grade=1, info="The configuration file does not exist, please check %s" % config_path)
            sys.exit()

        try:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
            myPrint(info="Current configuration information was %s." % config)
            f.close()
        except yaml.YAMLError as err:
            myPrint(grade=1, info="Configuration file loading failed, possibly due to formatting error, %s" % err)
            sys.exit()

        # 检查redis
        try:
            import redis
        except Exception as err:
            myPrint(grade=1, info="Redis checked is failed, Please install the dependent package redis. %s" % err)
            sys.exit()

        try:
            redis = redis.Redis(
                host=str(config.get("db_redis").get("host")),
                port=int(config.get("db_redis").get("port")),
                username=str(config.get("db_redis").get("user")),
                password=str(config.get("db_redis").get("password")),
                db=int(config.get("db_redis").get("db"))
            )
            myPrint(info="Congratulations, your redis server is ready to use !")
        except Exception:
            myPrint(grade=1, info="Redis server checked is failed, Please confirm the connection information, %s" % config.get("db_redis"))
            sys.exit()

        redis.close()

        # 检查MySQL
        try:
            import pymysql
        except Exception as err:
            myPrint(grade=1, info="PyMySQL checked is failed, Please install the dependent package PyMySQL. %s" % err)
            sys.exit()

        try:
            db = pymysql.connect(
                host=str(config.get("db_mysql").get("host")),
                port=int(config.get("db_mysql").get("port")),
                user=str(config.get("db_mysql").get("user")),
                password=str(config.get("db_mysql").get("password")),
                # database=str(config.get("db_mysql").get("database")),
                database="mysql",
                charset=str(config.get("db_mysql").get("charset"))
            )

            myPrint(info="Congratulations, your MySQL server is ready to use !")
        except pymysql.Error as err:
            myPrint(grade=1, info="MySQL server connection failed, Please confirm the connection information, %s" % err)
            sys.exit()

        # 创建数据库
        cursor = db.cursor()
        try:
            cursor.execute("CREATE DATABASE `%s` CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci';" % config.get("db_mysql").get("database"))
            db.commit()
            myPrint(info="Successfully created database %s." % config.get("db_mysql").get("database"))
        except pymysql.Error as err:
            if "database exists" in str(err):
                myPrint(grade=0, info="MySQL database %s already exists, no need to create it again." % config.get("db_mysql").get("database"))
            else:
                myPrint(grade=1, info="MySQL created database %s was failed. Please check account %s permissions for %s" % (config.get("db_mysql").get("database"), config.get("db_mysql").get("user"), err))
                sys.exit()
        cursor.close()
        db.close()


        # 创建表结构
        db = pymysql.connect(
            host=str(config.get("db_mysql").get("host")),
            port=int(config.get("db_mysql").get("port")),
            user=str(config.get("db_mysql").get("user")),
            password=str(config.get("db_mysql").get("password")),
            database=str(config.get("db_mysql").get("database")),
            # database="mysql",
            charset=str(config.get("db_mysql").get("charset"))
        )
        cursor = db.cursor()

        sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "init.sql")
        f = open(sql_path, "r", encoding="gbk")
        sql = f.read().replace("(\n", "(").replace(",\n", ",").replace(")\n", ")").replace("(\n", "").replace(",\n", ",").replace("  ","")
        f.close()

        create_table_sql_list = []
        insert_data_sql_list = []
        for sql in sql.split(";\n"):
            sql = sql.replace("\n", "").replace("\r", "")
            if "CREATE TABLE" in sql:
                create_table_sql_list.append(sql + ";")
            elif "INSERT INTO" in sql:
                insert_data_sql_list.append(sql + ";")

        # 创建数据表
        myPrint(info="Starting create table...")
        for sql in create_table_sql_list:
            try:
                cursor.execute(sql)

                myPrint(info="done-----%s" % sql)
            except pymysql.err.OperationalError as err:
                table_name = re.findall("Table '(.*)'", str(err))[0]
                if "already exists" in str(err):
                    myPrint(info="The data table %s already exists." % table_name)
                else:
                    myPrint(grade=1, info="unknown error, %s. %s" % (err, sql))
                    sys.exit()

        myPrint(info="Starting insert data...")
        for sql in insert_data_sql_list:
            try:
                cursor.execute(sql)
                myPrint(info="done----%s" % sql)
            except pymysql.err.ProgrammingError as err:
                if "You have an error in your SQL syntax" in str(err):
                    myPrint(grade=1, info="SQL syntax error. %s" % sql)
                    sys.exit()
                else:
                    myPrint(grade=1, info="unknown error. %s" % sql)
                    sys.exit()
            except Exception as err:
                myPrint(grade=1, info="unknown error, %s. %s" % (err, sql))
                sys.exit()
        db.commit()
        myPrint(info="MySQL database initialization completed.")

        cursor.close()
        db.close()

    def main(self):

        # 开始检查PY版本
        myPrint(info="Starting checking Python version...")
        pip_result = self.py_version()
        while True:
            if pip_result == 0:
                break
            else:
                while True:
                    select_number = input("Please enter whether to continue<Y is Contine, N is Stop>:").upper()
                    try:
                        if select_number is not None:
                            break
                        else:
                            continue
                    except ValueError:
                        print("Please enter the correct option")
                        continue
                if select_number == "Y":
                    break
                elif select_number == "N":
                    myPrint(grade=1, info="User actively exits !")
                    sys.exit()
                else:
                    myPrint(grade=1, info="Exception occurred, exiting the program !")
                    sys.exit()

        # 开始检查PIP环境
        myPrint(info="Starting checking Python pip...")
        try:
            self.pip()
        except Exception as err:
            myPrint(grade=1, info="Pip dependency environment detection failed, Please rerun the initialization script. %s" % err)

        # 开始初始化数据库
        myPrint(info="Starting init db environment...")
        self.db_init()