#!-*-coding:utf-8-*-
# !@Date: 2018/9/28 10:41
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
配置文件
"""

import redis
import os
import logging


class Config(object):
	"""工程配置类, 之后配置太多时将其单独放到一个文件"""
	DEBUG = True

	SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')  # 从系统变量加载以保密
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	REDIS_HOST = '127.0.0.1'
	REDIS_PORT = 6379
	REDIS_NUM = 0  # 使用的redis数据库

	SECRET_KEY = 'hello'

	SESSION = 'redis'  # 指定session保存到redis
	SESSION_USER_SIGNER = True  # 让cookie中的session_id被加密签名处理
	SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_NUM)  # 将redis实例传入
	SESSION_PERMANENT = False  # 关闭永久存储
	PERMANENT_SESSION_LIFETIME = 86400  # session有效期,单位为秒

	# 11. 默认的日志等级,使用DEBUG以尽可能多的显示信息
	LOG_LEVEL = logging.DEBUG


# 针对不同的环境(开发还是生产),需要不同的配置
class DevelopmentConfig(Config):
	"""开发模式下的配置"""
	DEBUG = True
	# 开发环境的项目配置
	LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
	"""生产模式下的配置"""
	DEBUG = False
	# 生产环境的项目配置
	LOG_LEVEL = logging.ERROR


# 10. 定义一个配置字典,同时在info/__init__.py文件中定义一个工厂方法,可以根据传入的配置不同
# 创建其对应的应用实例
config = {
	'development': DevelopmentConfig,
	'production': ProductionConfig
}
