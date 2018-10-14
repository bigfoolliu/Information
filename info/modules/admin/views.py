#!-*-coding:utf-8-*-
# !@Date: 2018/10/13 13:27
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
info/modules/admin/views.py
"""
from flask import request, render_template, session, redirect, url_for, current_app, g

from info import db
from info.models import User
from info.modules.admin import admin_bp


# 127.0.0.1:5000/admin/login
from info.utils.common import user_login_data


@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
	"""
	管理员账户登录后台接口
	:return:
	"""
	# get请求时展示登录页
	if request.method == 'GET':
		# 判断当前用户是否有登录,如果管理员有登录直接进入管理员首页
		user_id = session.get('user_id')
		is_admin = session.get('is_admin', False)
		if user_id and is_admin:
			return redirect(url_for('admin.admin_index'))
		else:
			# 不是管理员账户
			return render_template('admin/login.html')

	# 当为POST请求时,首先获取参数
	username = request.form.get('username')
	password = request.form.get('password')

	# 参数校验
	if not all([username, password]):
		return render_template('admin/login.html', errmsg='参数不足')

	# 根据username查询用户
	try:
		admin_user = User.query.filter(User.mobile == username, User.is_admin == True).first()
	except Exception as e:
		current_app.logger.error(e)
		# 为查询到用户则重新加载该登录页面
		return render_template('admin/login.html', errmsg='数据库查询管理员账户异常')
	# 用户不存在则重新加载该登录页面
	if not admin_user:
		return render_template('admin/login.html', errmsg='没有查询到该管理员账户')

	# 校验密码
	if not admin_user.check_password(password):
		return render_template('admin/login.html', errmsg='密码错误')

	# 将数据保存回数据库
	try:
		db.session.commit()
	except Exception as e:
		current_app.logger.error(e)
		db.session.rollback()
		return render_template('admin/login.html', errmsg='保存用户对象异常')

	# 管理员用户数据保存到session
	session['nick_name'] = username
	session['user_id'] = admin_user.id
	session['mobile'] = username
	session['is_admin'] = True

	# 重定向至管理首页
	return redirect(url_for('admin.admin_index'))


# 127.0.0.1:5000/admin/index
@admin_bp.route('/index')
@user_login_data
def admin_index():
	"""
	后台管理首页
	:return:
	"""
	user = g.user  # 注意必须要装饰器

	if not user:
		return redirect(url_for('admin.admin_login'))

	data = {
		'user': user.to_dict()
	}
	return render_template('admin/index.html', data=data)
