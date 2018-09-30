#!-*-coding:utf-8-*-
# !@Date: 2018/9/28 10:48
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
info/__init__.py主要做app的创建,初始化工作
"""

# 1. 基本配置
from flask import Flask
# 2. 导入数据库扩展并填写相关配置
from flask_sqlalchemy import SQLAlchemy
# 3. 创建Redis存储对象,并在配置中填写相关配置
import redis
# 4. 包含请求体的请求中都要开启CSRF
# CSRFProtect只做验证工作，cookie中的 csrf_token 和表单中的 csrf_token 需要我们自己实现
from flask_wtf.csrf import CSRFProtect
# 5. session数据要保存到Redis中
from flask_session import Session

# 7. 代码抽取,将Config单独作为一个文件,重新导入配置类
from config import config

# 11. 日志相关
import logging
from logging.handlers import RotatingFileHandler


# db = SQLAlchemy(app)
# # redis存储对象
# redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

db = SQLAlchemy()
"""
redis存储对象
# type: redis.StrictRedis 使的即使未具体定义,仍可以申明类型
"""
redis_store = None  # type: redis.StrictRedis


# 11. 添加日志配置的相关方法
def setup_log(config_name):
	"""配置日志"""
	# 设置日志的记录等级
	logging.basicConfig(level=config[config_name].LOG_LEVEL)
	# 创建日志记录器,指明日志保存的路径,每个日志文件的最大大小,保存的日志文件个数上限
	file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024 * 1024 * 100, backupCount=10)
	# 创建日志管理的格式, 日志等级,输入日志信息的文件名,行数,日志信息
	formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
	# 为刚创建的日志记录器设置日志记录格式
	file_log_handler.setFormatter(formatter)
	# 为全局的日志工具对象(flask app使用的)添加日志记录器
	logging.getLogger().addHandler(file_log_handler)


# 10. 工厂方法
def create_app(config_name):
	"""根据传入不同的配置名字,初始化其对应配置的app实例"""
	# 首先配置项目日志
	setup_log(config_name)

	app = Flask(__name__)

	app.config.from_object(config[config_name])

	# 重新配置数据库
	db.init_app(app)
	# 重新配置redis
	global redis_store
	redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)

	"""
	开启csrf保护
	1. 自动开启csrf保护机制
	2. 自动获取ajax请求头中的csrf_token
	3. 自动校验这两个值,相等为正常请求,不等为非法请求
	"""
	csrf = CSRFProtect(app)
	# 设置session保存位置
	Session(app)

	"""
	注册蓝图
	当需要蓝图的时候才导入,防止其他位置导入错误
	"""
	from info.modules.index import index_bp
	app.register_blueprint(index_bp)
	# 将注册蓝图注册到app
	from info.modules.passport import passport_bp
	app.register_blueprint(passport_bp)

	return app
