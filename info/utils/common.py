#!-*-coding:utf-8-*-
# !@Date: 2018/10/2 14:28
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
自定义的过滤器
"""
from flask import session, current_app, jsonify, g

from info.utils.response_code import RET


def do_index_class(index):
	"""根据index的下标返回对应的class值"""
	if index == 0:
		return 'first'
	elif index == 1:
		return 'second'
	elif index == 2:
		return 'third'
	else:
		return ''


import functools


# 获取当前登录用户信息的装饰器,使用其将所有需要验证用户登录的地方进行装饰
# 解决代码重复率过高的问题
def user_login_data(view_func):
	"""
	使用装饰器改变被装饰函数的一些特性,比如函数名称,
	为了解决该问题,使用functools模块解决该问题
	:param view_func:
	:return:
	"""
	@functools.wraps(view_func)
	def wrapper(*args, **kwargs):
		# 1. 实现装饰器的功能

		# 获取当前用户的信息
		user_id = session.get('user_id')
		user = None  # type:User

		# 延迟导入,解决循环导入db的问题
		from info.models import User
		if user_id:
			try:
				user = User.query.get(user_id)
			except Exception as e:
				current_app.logger.error(e)
				return jsonify(erron=RET.DBERR, errmsg='查询用户信息异常')

		# 将用户保存到flask的g对象中,从而在全局都可以进行访问
		g.user = user

		# 2. 实现被装饰函数的原有功能
		result = view_func(*args, **kwargs)
		return result

	return wrapper

