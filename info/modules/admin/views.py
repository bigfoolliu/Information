#!-*-coding:utf-8-*-
# !@Date: 2018/10/13 13:27
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
info/modules/admin/views.py
"""
import datetime
import time
from flask import request, render_template, session, redirect, url_for, current_app, g, jsonify, abort

from info import db, constants
from info.models import User, News
from info.modules.admin import admin_bp

from info.utils.common import user_login_data


from info.utils.response_code import RET


# 127.0.0.1:5000/admin/news_review_detail?news_id=新闻id
@admin_bp.route('/news_review_detail', methods=['GET', 'POST'])
def news_review_detail():
	"""
	新闻审核细节后端接口
	:return:
	"""
	# 请求方式为get则显示待审核新闻详情
	if request.method == 'GET':
		news_id = request.args.get('news_id')
		if not news_id:
			return Exception('参数不足')

		try:
			news = News.query.get(news_id)
		except Exception as e:
			current_app.logger.error(e)
			return jsonify(erron=RET.DBERR, errmsg='数据库查询新闻对象异常')

		if not news:
			abort(404)

		# 对象转字典
		news_dict = news.to_dict() if news else None

		data = {
			'news': news_dict
		}
		return render_template('admin/news_review_detail.html', data=data)

	# post请求审核新闻
	params_dict = request.json
	news_id = params_dict.get('news_id')
	action = params_dict.get('action')  # 审核通过还是不通过

	if not all([news_id, action]):
		return jsonify(erron=RET.PARAMERR, errmsg='参数不足')

	if action not in ['accept', 'reject']:
		return jsonify(erron=RET.PARAMERR, errmsg='action参数错误')

	# 根据新闻id查询新闻对象
	try:
		news = News.query.get(news_id)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.DBERR, errmsg='查询新闻对象错误')

	if not news:
		return jsonify(erron=RET.NODATA, errmsg='没有新闻对象')

	# 新闻是否审核通过逻辑
	if action == 'accept':
		news.status = 0
	else:
		reason = request.json.get('reason')
		if reason:
			news.status = 1
			news.reason = reason
		else:
			return jsonify(erron=RET.PARAMERR, errmsg='需要填写审核不通过原因')

	# 将新闻对象重新保存回数据库
	try:
		db.session.commit()
	except Exception as e:
		current_app.logger.error(e)
		db.session.rollback()
		return jsonify(erron=RET.DBERR, errmsg='数据库存储新闻对象异常')

	# 返回值
	return jsonify(erron=RET.OK, errmsg='OK')


# 127.0.0.1:5000/admin/news_review?p=页码
@admin_bp.route('/news_review')
def news_review():
	"""
	新闻审核后端接口
	:return:
	"""
	p = request.args.get('p', 1)
	try:
		p = int(p)
	except Exception as e:
		current_app.logger.error(e)
		p = 1

	news_list = []
	current_page = 1
	total_page = 1
	# 获取查询关键字
	keywords = request.args.get('keywords')
	# 查询条件列表
	filters = [News.status != 0]  # 审核的新闻状态不能为'通过'

	if keywords:
		# 如果是关键字查询,该新闻应该包含该关键字
		filters.append(News.title.contains(keywords))
	try:
		paginate = News.query.filter(*filters).order_by(News.create_time.desc())\
			.paginate(p, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
		news_list = paginate.items
		current_page = paginate.page
		total_page = paginate.pages
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.DBERR, errmsg='数据库查询新闻分页错误')

	# 模型对象转字典列表
	news_dict_list = []
	for news in news_list if news_list else []:
		news_dict_list.append(news.to_review_dict())

	# 组织响应数据
	data = {
		'news_list': news_dict_list,
		'current_page': current_page,
		'total_page': total_page
	}

	return render_template('admin/news_review.html', data=data)


# 127.0.0.1:5000/admin/user_list?p=页码
@admin_bp.route('/user_list')
def user_list():
	"""
	查询用户列表
	:return: 
	"""
	p = request.args.get('p', 1)
	try:
		p = int(p)
	except Exception as e:
		current_app.logger.error(e)
		p = 1

	user_list = []
	current_page = 1
	total_page = 1

	try:
		paginate = User.query.filter(User.is_admin == False).order_by(User.last_login.desc())\
			.paginate(p, constants.ADMIN_USER_PAGE_MAX_COUNT, False)
		user_list = paginate.items
		current_page = paginate.page
		total_page = paginate.pages
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.DBERR, errmsg='数据库查询用户数据异常')

	# 对象列表转字典列表
	user_dict_list = []
	for user in user_list if user_list else []:
		user_dict_list.append(user.to_admin_dict())

	# 组织响应数据
	data = {
		'users': user_dict_list,
		'current_page': current_page,
		'total_page': total_page
	}

	# 返回值
	return render_template('admin/user_list.html', data=data)


# 127.0.0.1:5000/admin/user_count
@admin_bp.route('/user_count')
def user_count():
	"""
	用户统计后端接口
	:return:
	"""
	total_count = 0   # 查询总人数
	try:
		total_count = User.query.filter(User.is_admin == False).count()
	except Exception as e:
		current_app.logger.error(e)

	# 月新增用户数：获取到本月第1天0点0分0秒的时间对象，然后查询最后一次登录比其大的所有数据
	mon_count = 0
	try:
		now = time.localtime()
		mon_begin = '%d-%02d-01' % (now.tm_year, now.tm_mon)  # 当前月份的第一天
		mon_begin_date = datetime.datetime.strptime(mon_begin, '%Y-%m-%d')  # 将时间字符串转换为时间格式
		mon_count = User.query.filter(User.is_admin == False, User.create_time >= mon_begin_date).count()
	except Exception as e:
		current_app.logger.error(e)

	# 查询日新增数: 获取到当日0点0分0秒时间对象，然后查询最后一次登录比其大的所有数据
	day_count = 0
	try:
		now = time.localtime()
		day_begin = '%d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday)
		day_begin_date = datetime.datetime.strptime(day_begin, '%Y-%m-%d')  # 将时间字符串转换为时间格式
		day_count = User.query.filter(User.is_admin == False, User.create_time >= day_begin_date).count()
	except Exception as e:
		current_app.logger.error(e)

	# 图表查询：遍历查询数据每一天的数据(当前天数，减去某些天)
	now_date = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
	active_date = []
	active_count = []

	# 依次添加数据
	for i in range(0, 31):
		# 一天的开始时间
		begin_date = now_date - datetime.timedelta(days=i)
		# 一天的结束时间
		end_date = begin_date + datetime.timedelta(days=i)
		active_date.append(begin_date.strftime('%Y-%m-%d'))
		count = 0
		try:
			count = User.query.filter(
				User.is_admin == False,
				User.last_login >= begin_date,
				User.last_login <= end_date
			).count()
		except Exception as e:
			current_app.logger.error(e)
		# 添加每一天的活跃人数
		active_count.append(count)

	# 数据反转
	active_date.reverse()
	active_count.reverse()

	# 组织响应数据
	data = {
		'total_count': total_count,
		'mon_count': mon_count,
		'day_count': day_count,
		'active_date': active_date,
		'active_count': active_count
	}

	# 返回值
	return render_template('admin/user_count.html', data=data)


# 127.0.0.1:5000/admin/login
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
	user = g.user
	data = {
		'user': user.to_dict()
	}
	return render_template('admin/index.html', data=data)
