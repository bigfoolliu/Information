#!-*-coding:utf-8-*-
# !@Date: 2018/9/28 15:24
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
/info/modules/index/views.py存放当前模块的所有视图函数
"""
# 导入蓝图
from . import index_bp

import logging
from info import redis_store
from flask import current_app


@index_bp.route('/')
def hello_world():
	# 使用redis对象存储key-value数据(用作测试redis连接用)
	redis_store.set('name', 'liu')  # TODO: 需要在本地开启redis-server使用

	# python内置logging模块测试用
	logging.debug('debug msg')
	logging.info('info msg')
	logging.warning('warning msg')
	logging.error('error msg')
	logging.critical('critical msg')

	# flask中对logging模块封装的,直接用current_app调用
	current_app.logger.debug('flask debug msg')

	return 'hello world.'
