#!-*-coding:utf-8-*-
# !@Date: 2018/10/13 13:27
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
info/modules/admin/__init__.py
"""
from flask import Blueprint, request, session, redirect

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from .views import *


@admin_bp.before_request
def is_admin_user():
	"""
	每次请求之前判断该用户是否为管理员用户
	:return:
	"""
	# 如果是访问管理员登录页面,正常引导
	if request.url.endswith('/admin/login'):
		pass
	# 如果不是访问访问管理员登录页面
	else:
		# 获取用户id
		user_id = session.get('user_id')
		# 判断是否为管理员
		is_admin = session.get('is_admin')

		# 用户不存在则引导到新闻首页,用户不是管理员也引导到首页
		if not user_id or not is_admin:
			return redirect('/')
