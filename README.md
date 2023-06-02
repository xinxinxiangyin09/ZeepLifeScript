# ZeepLifeScript

![](https://img.shields.io/badge/python-v3.6.5-green)![](https://img.shields.io/badge/redis-v7.0.9-green)![](https://img.shields.io/badge/MySQL-v8.0.29-green)

![](https://img.shields.io/badge/PyMySQL-v1.0.2-blue)![](https://img.shields.io/badge/PyYAML-v6.0-blue)![](https://img.shields.io/badge/redis-v4.3.4-blue)![](https://img.shields.io/badge/cryptography-v2.4.2-blue)![](https://img.shields.io/badge/requests-v2.27.1-blue)

> 该脚本根据实际时间段刷步数，可同步VX、ZFB平台，并可部署一键全天自动刷

项目地址：[点击跳转](https://github.com/xinxinxiangyin09/ZeepLifeScript)

## 一、依赖环境

|   名称   |  版本号   |
|:------:|:------:|
| PYTHON | 3.6.5  |
| REDIS  | 7.0.9  |
| MYSQL  | 8.0.29 |

## 二、PIP依赖

|      名称      |  版本号   |
|:------------:|:------:|
|   PyMySQL    | 1.0.2  |
|    PyYAML    |  6.0   |
|    redis     | 4.3.4  |
| cryptography | 2.4.2  |
 |   requests   | 2.27.1 | 

## 三、脚本简介

1. 文件目录树

   ```bash
   .
   └── ZeepLifeScript
       ├── base
       │   ├── init.py
       │   ├── init.sql
       │   ├── __pycache__
       │   │   └── init.cpython-36.pyc
       │   └── startInit.py
       ├── config.yaml
       ├── __pycache__
       │   └── ZeepLife.cpython-36.pyc
       ├── README.md
       ├── requirements.txt
       ├── start_for_linux.sh
       ├── start_for_windows.bat
       ├── start.py
       ├── ZeepLife.log
       └── ZeepLife.py
   
   ```

2. 本开发环境为CentOS7.6，在windows7中成功测试。

3. PYTHON版本问题，只要大版本不变，其他都没事，应该能正常运行（虽然没试过）
> 比如需要的环境是3.6.5，而你部署的环境PYTHON为3.6.7，理论上是可以正常运行的。 但是大版本不一致有大概率不能运行，比如3.10
3. 脚本中富含了环境初始化，所以只需要安装好`MYSQL`、`REDIS`和`PYTHON`即可一键初始化环境
4. 运行的流程为：当日首次运行则会创建当日计划，每一小时刷新一次，全部计划在`REDIS`的`DB0`中，每次执行完就会在`MySQL`的`zeep_life.log`中生成记录，记录不要删除，因为是根据记录判断当天是否完成计划任务
5. 目前将`redis`作为执行的计划，`MYSQL`主要记录日志，避免出现死循环。
6. 本脚本准备不定期迭代版本，也是为了更稳定，这一版为初期，有很多不足，还望大佬`ISSUE`

## 四、基础环境安装

1. 安装PYTHON
    安装PYTHON方法有很多，这里不详细介绍，可以[看我](https://www.cnblogs.com/chancey/p/9848867.html)
> 这里需要注意，安装的PYTHON虚拟解释器需要在`/root/.virtualenv/py3env/bin/python3`，只能暂时写成死的了，后边再慢慢改吧
2. 安装REDIS
> 可以[前往参考](https://www.cnblogs.com/chancey/p/9848903.html)
3. 安装MYSQL
> 可以[前往参考](https://www.cnblogs.com/chancey/p/17207506.html)

## 五、ZeepLife准备

1. 手机下载`Zeep Life`APP，在应用商店都可以搜到

   ![微信图片_20230602184001](https://s2.loli.net/2023/06/02/Y3LP1tUBTSFQrKa.jpg)

2. 注册账号，尽量使用邮箱注册，并牢记用户名和密码，后边会用到

   ![微信图片_20230602183927](https://s2.loli.net/2023/06/02/bK7WYP1AdmyQIcS.jpg)

3. 登录

   ![微信图片_20230602183932](https://s2.loli.net/2023/06/02/LRpIV84ou17GQFs.jpg)

## 六、部署

1. 编辑`./config.yaml`文件

   ```yaml
   user_info:
     username:
     password:
   
   step:
     minimum_steps: 26800
     max_steps: 29000
     steps: 8
   
   db_redis:
     host: 127.0.0.1
     port: 12308
     password: 0
     db: 0
   
   db_mysql:
     host: 127.0.0.1
     port: 12306
     user: root
     password: 0
     database: zeep_life
     charset: utf8mb4
   ```

   > `user_info`：zeeplife的账户信息
   >
   > `step`：每天要刷的节奏信息，`minimum_steps`为最小，`max_steps`为最大，`steps`为步长（也就是一天需要分几次刷）
   >
   > `db_redis`：redis的配置信息
   >
   > `db_mysql`：MySQL的配置信息

2. 初始化环境

   ```bash
   # LINUX下初始化：
   cd .../ZeepLifeScript/base
   /root/.virtualenv/py3env/bin/python3 startInit.py
   
   # Windows下初始化：
   cd .../ZeepLifeScript
   pip install -r requirements.txt -i https://pypi.douban.com/simple
   cd base
   C:\Users\chancey\AppData\Local\Programs\Python\Python36\python.exe startInit.py
   ```

   > 这里初始化会自动安装pip依赖和自动生产MySQL表结构并检测redis环境

3. 运行

   linux下

   ```bash
   cd .../ZeepLifeScript
   
   sh start_for_linux.sh
   ```

   windows下

   双击`start_for_windows.bat`即可

## 七、定时任务

### 1. WINDOWS下

1. 在本地找到`任务计划程序`，左侧选项栏中右击`创建任务`

   ![image-20230603014818138](https://s2.loli.net/2023/06/03/zaGFOBUxgMq6VfY.png)

2. 名称和描述随意填写

   常规

   > 值得注意的地方是，要勾选`不管用户是否登录都要运行`和`使用最高权限运行`

   ![image-20230603015124995](https://s2.loli.net/2023/06/03/1DzVeRwF2BYoiOq.png)

   触发器

   > 这里设置一小时运行一次，且无限期

   ![image-20230603015328648](https://s2.loli.net/2023/06/03/xbnCwVLPuvGrFRz.png)

   ![image-20230603015424349](https://s2.loli.net/2023/06/03/lb4Cy895Usp2Gjz.png)

   操作

   > 程序或脚本：选择`start_for_windows.bat`
   >
   > 其他参数为空即可

   ![image-20230603015833230](https://s2.loli.net/2023/06/03/gC2GbxUy5XNhJMD.png)

   条件

   ![image-20230603015925342](https://s2.loli.net/2023/06/03/U5wGKI9WoMT1BzQ.png)

3. 点击确定，提示输入密码，输入即可保存计划

4. 查看运行状态，直接打开日志文件查看

### 2.LINUX下

1. 安装`crontabs`

   ```bash
   # 查看是否已安装
   rpm -qa | grep crontabs
   
   # YUM安装crontabs
   yum install -y crontabs
   ```

   ![image-20230603020533470](https://s2.loli.net/2023/06/03/iqzQVBnMWu2j1m3.png)

2. 设置状态

   ```bash
   # 开机自启
   systemctl enable crond
   
   # 启动crontabs
   systemctl start crond
   ```

3. 配置定时任务文件

   `crontab -e`编辑计划任务

   ![image-20230603021903790](https://s2.loli.net/2023/06/03/RLgYlrzhTq8BwtN.png)

   > 配置相关说明：
   >
   > 用户的定时任务分6段, 分别是：分，时，日，月，周，执行的命令
   >
   > 1. 第1列表示分钟1～59 (每分钟用*或者 */1表示)
   > 2. 第2列表示小时1～23 (0表示0点)
   > 3. 第3列表示日期1～31 (具体哪一天)
   > 4. 第4列表示月份1～12 (具体哪一月)
   > 5. 第5列标识号星期0～6 (0表示星期天，依此类推)
   > 6. 第6列要运行的shell命令
   >
   > `*`：表示任意时间，就是“每”的意思。可以代表00-23小时或者00-12每月或者00-59分；
   >
   > `-`：表示区间，是一个范围，例如：00 17-19 * * * reboot，就是每天17,18,19 点的整点执行重启命令；
   >
   > `,`：是分割时段，例如：30 3,19,21 * * * cmd，就是每天凌晨3和晚上19,21点的30分时执行命令；
   >
   > `/n`：表示分割，可以看成除法。例如：*/5 * * * * cmd，每隔五分钟执行一次；

4. 保存配置并即刻生效

   ```bash
   crontab /etc/crontab
   ```

## 八、注意事项

1. `ZeepLife`必须要和VX或者ZFB在同一个设备，不然无法同步，且不能卸载

2. 运行环境尽量在Linux下，可以避免很多不必要的麻烦

3. 运行的流程为：当日首次运行则会创建当日计划，每一小时刷新一次，全部计划在`REDIS`的`DB0`中，每次执行完就会在`MySQL`的`zeep_life.log`中生成记录，记录不要删除，因为是根据记录判断当天是否完成计划任务

4. 在Windows下初始化环境需要手动安装PIP包，暂时将解释器路径写死了，后期考虑做自动化识别，具体安装方法如下

   ```
   # 切换到项目根目录下
   cd .../ZeepLifeScript
   
   # 指定安装源安装，PYTHON官方PYPI太慢了，需要确保脚本能正常识别到requirements.txt文件
   pip install -r requirements.txt -i https://pypi.douban.com/simple
   
   # 切换到基础环境初始化目录下
   cd base
   
   # 再次执行startInit.py
   python startInit.py
   ```

   > 在执行`startInit.py`出现`系统找不到指定目录`不用理会，这是PYTHON解释器路径在Linux下的，其实就是为了PIP安装依赖包，只要`redis`和`mysql`初始化不报错就没事。

5. 如果使用过程中有问题，请协图`ISSUE`我

6. 觉得好用的话请来个`star`鼓励鼓励，毕竟BP的，哈哈哈