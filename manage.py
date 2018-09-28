#!-*-coding:utf-8-*-
# !@Date: 2018/9/26 18:55
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
/manage.py作为主程序的入口
	只做最基本的启动工作,app的创建移动至info的__init__.py中

其中:
	- 1. 2. ...表示程序书写的顺序
"""

# # 1. 基本配置
# from flask import Flask
# # 2. 导入数据库扩展并填写相关配置
# from flask_sqlalchemy import SQLAlchemy
# import os
# # 3. 创建Redis存储对象,并在配置中填写相关配置
# import redis
# # 4. 包含请求体的请求中都要开启CSRF
# # CSRFProtect只做验证工作，cookie中的 csrf_token 和表单中的 csrf_token 需要我们自己实现
# from flask_wtf.csrf import CSRFProtect
# # 5. session数据要保存到Redis中
# from flask_session import Session
# 6. flask_script与数据量迁移
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
# # 7. 代码抽取,将Config单独作为一个文件,重新导入配置类
# from config import Config
# 8. 业务逻辑独立
# 除启动文件manage.py和配置问价config.py放于根目录,其他文件置于单独的文件夹,与manage.py同级
# 9. 此时需要导入创建好的app对象以及数据库对象
# from info import app, db
# 10. 对配置进行修改,可根据环境不同,快速切换配置
from info import create_app, db
# 11. 增加日志,在配置文件中增加日志等级等

# 导入模型
from info import modules


app = create_app('development')  # 以开发模式配置来创建app
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
	manager.run()  # 在启动中配置参数runserver
