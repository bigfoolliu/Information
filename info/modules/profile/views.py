#!-*-coding:utf-8-*-
# !@Date: 2018/10/10 20:07
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
info/modules/profile/views.py

用于个人中心的视图函数
"""
from flask import g, render_template, request, jsonify, session, current_app

from info import db, constants
from info.models import Category, News
from info.modules.profile import profile_bp
from info.utils.common import user_login_data
from info.utils.pic_storage import pic_storage

from info.utils.response_code import RET


# 127.0.0.1:5000/user/news_list
@profile_bp.route('/news_list')
@user_login_data
def news_list():
	"""
	用户中心展示该用户发布的新闻的后端接口
	:return:
	"""
	user = g.user
	p = request.args.get('p', 1)  # 页码,默认设置为1

	# 参数类型判断
	try:
		p = int(p)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.PARAMERR, errmsg='参数内容错误')

	# 当前用户存在的时候则采取查询
	news_list1 = []
	current_page = 1
	total_page = 1
	if user:
		try:
			# 创建一个数据库分页对象
			paginate = News.query.filter(News.user_id == user.id).paginate(p, constants.OTHER_NEWS_PAGE_MAX_COUNT, False)
			# 获取当前页码的所有数据
			news_list1 = paginate.items
			# 当前页码
			current_page = paginate.page
			# 总的页码
			total_page = paginate.pages
		except Exception as e:
			current_app.logger.error(e)
			return jsonify(erron=RET.DBERR, errmsg='数据库查询分页数据失败')

	# 将对象列表转成字典列表
	news_dict_list = []
	for news in news_list1 if news_list1 else []:
		news_dict_list.append(news.to_review_dict())

	# 组织响应数据
	data = {
		'news_list': news_dict_list,
		'current_page': current_page,
		'total_page': total_page
	}

	# 返回值
	return render_template('profile/user_news_list.html', data=data)


# 127.0.0.1:5000/user/news_release
@profile_bp.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
	"""
	用户发布新闻
	:return:
	"""
	user = g.user

	# get请求时展示新闻发布页面
	if request.method == 'GET':
		# 查询分类数据
		try:
			categories = Category.query.all()
		except Exception as e:
			current_app.logger.error(e)
			return jsonify(erron=RET.DBERR, errmsg='数据库查询分类数据异常')
		# 对象列表转字典列表
		category_dict_list = []
		for category in categories if categories else []:
			category_dict_list.append(category.to_dict())
		# 移除分类中的'最新'分类
		category_dict_list.pop(0)
		# 组织响应数据
		data = {
			'categories': category_dict_list
		}
		return render_template('profile/user_news_release.html', data=data)

	# 为post请求时发布新闻
	# 获取参数
	title = request.form.get('title')  # 新闻标题
	category_id = request.form.get('category_id')  # 新闻分类id
	digest = request.form.get('digest')  # 新闻摘要
	content = request.form.get('content')  # 新闻具体内容
	index_image = request.files.get('index_image')  # 新闻主图片
	source = '个人发布'  # 将新闻来源设置为固定值

	# 参数校验
	if not all([title, category_id, digest, content, index_image]):
		return jsonify(erron=RET.PARAMERR, errmsg='参数不足')

	if not user:
		return jsonify(erron=RET.SESSIONERR, errmsg='用户未登录')

	# 获取新闻主图片的二进制数据
	try:
		pic_data = index_image.read()
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.DATAERR, errmsg='新闻主图片数据不能为空')

	# 将获取的主新闻图片上传至七牛云
	try:
		pic_name = pic_storage(pic_data)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.THIRDERR, errmsg='新闻主图片上传至七牛云失败')

	# 创建新闻对象,并对其属性赋值
	news = News()
	news.title = title
	news.category_id = category_id
	news.digest = digest
	news.content = content
	news.index_image_url = constants.QINIU_DOMIN_PREFIX + pic_name
	news.source = source
	news.user_id = user.id
	"""
	新闻状态(status)
	0: 审核通过
	1: 审核中,默认的状态
	"""
	news.status = 1

	# 将新闻对象保存到数据库
	try:
		db.session.add(news)
		db.session.commit()
	except Exception as e:
		current_app.logger.error(e)
		db.session.rollback()
		return jsonify(erron=RET.DBERR, errmsg='保存新闻对象异常')

	# 返回值
	return jsonify(erron=RET.OK, errmsg='新闻发布成功')


# 127.0.0.1:5000/user/collection?p=页码
@profile_bp.route('/collection')
@user_login_data
def user_collection_news():
	"""
	获取当前用户新闻的收藏列表
	:return:
	"""
	user = g.user
	p = request.args.get('p', 1)  # 页码,默认设置为1

	# 参数类型判断
	try:
		p = int(p)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.PARAMERR, errmsg='参数类型错误')

	# 查询用户收藏的新闻列表
	news_collections = []
	current_page = 1
	total_page = 1

	if user:
		try:
			# TODO: paginate需要加深了解
			paginate = user.collection_news.paginate(p, constants.USER_COLLECTION_MAX_NEWS, False)
			# 当前页码所有数据
			news_collections = paginate.items
			# 总页数
			total_page = paginate.pages
			# 当前页码
			current_page = paginate.page
		except Exception as e:
			current_app.logger.error(e)
			return jsonify(erron=RET.DBERR, errmsg='数据库查询收藏新闻分页数据异常')

	# 对象列表转字典列表
	news_dict_collections = []
	for news in news_collections if news_collections else []:
		news_dict_collections.append(news.to_basic_dict())

	# 组织响应数据
	data = {
		'collections': news_dict_collections,
		'current_page': current_page,
		'total_page': total_page
	}

	# 返回值
	return render_template('profile/user_collection.html', data=data)


# 127.0.0.1:5000/user/pass_info
@profile_bp.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
	"""
	更改用户原始密码
	:return:
	"""
	user = g.user
	if request.method == 'GET':
		return render_template('profile/user_pass_info.html')

	# post请求修改用户密码接口
	old_password = request.json.get('old_password')
	new_password = request.json.get('new_password')

	# 参数校验
	if not all([old_password, new_password]):
		return jsonify(erron=RET.PARAMERR, errmsg='参数不足')

	if not user:
		return jsonify(erron=RET.SESSIONERR, errmsg='用户未登录')
	# 校验旧密码是否正确
	if not user.check_password(old_password):
		return jsonify(erron=RET.DATAERR, errmsg='原始密码输入错误')

	# 将新密码赋值到user对象
	user.password = new_password
	# 保存数据至数据库
	try:
		db.session.commit()
	except Exception as e:
		current_app.logger.error(e)
		db.session.rollback()
		return jsonify(erron=RET.DBERR, errmsg='数据库保存密码异常')

	# 返回值
	return jsonify(erron=RET.OK, errmsg='密码修改成功')


# 127.0.0.1:5000/user/pic_info
@profile_bp.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
	"""
	上传用户头像
	:return:
	"""
	user = g.user

	# 为get请求时
	if request.method == 'GET':
		return render_template('profile/user_pic_info.html')

	# 为post请求时
	"""
	1. 获取参数
		avatar, user
	2. 校验参数
	3. 逻辑处理
		借助七牛云,将二进制图片数据上传
		将返回的图片url保存至用户对象
		完整的图片url返回至前端
	4. 返回值
	"""
	# 获取用户上传的图片数据
	try:
		pic_data = request.files.get('avatar').read()
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.PARAMERR, errmsg='获取图片异常')

	# 将图片上传至七牛云
	try:
		pic_name = pic_storage(pic_data)  # 返回值为七牛云为图片创建的一个名称
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.THIRDERR, errmsg='七牛云上传图片失败')

	# 将图片的url保存至用户对象(此处为相对路径,在后面拼接完整路径)
	user.avatar_url = pic_name
	try:
		db.session.commit()
	except Exception as e:
		current_app.logger.error(e)
		db.session.rollback()
		return jsonify(erron=RET.DBERR, errmsg='数据库存储照片信息异常')

	# 创建完整的头像url并传给前端
	full_url = constants.QINIU_DOMIN_PREFIX + pic_name
	# 组织返回数据
	data = {
		'avatar_url': full_url
	}
	# 返回值
	return jsonify(erron=RET.OK, errmsg='上传头像成功', data=data)


# 127.0.0.1:5000/user/info
@profile_bp.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def user_base_info():
	"""
	展示用户基本信息页面
	:return:
	"""
	user = g.user

	# 请求为get时,展示基本信息
	if request.method == 'GET':
		data = {
			'user_info': user.to_dict() if user else None
		}
		return render_template('profile/user_base_info.html', data=data)

	# 请求为post时,修改用户基本资料
	# 获取参数
	params_dict = request.json
	signature = params_dict.get('signature')
	nick_name = params_dict.get('nick_name')
	gender = params_dict.get('gender')

	# 参数校验
	if not all([signature, nick_name, gender]):
		return jsonify(erron=RET.PARAMERR, errmsg='参数不足')

	if not user:
		return jsonify(erron=RET.SESSIONERR, errmsg='用户未登录')

	if gender not in ['MAN', 'WOMAN']:
		return jsonify(erron=RET.PARAMERR, errmsg='gender参数错误')

	# 将获取到的属性保存到当前登录的用户中
	user.signature = signature
	user.nick_name = nick_name
	user.gender = gender

	# 更新session中的nick_name数据
	session['nick_name'] = nick_name

	# 将用户数据保存到数据库
	try:
		db.session.commit()
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.DBERR, errmsg='数据库保存用户数据异常')

	# 返回值
	return jsonify(erron=RET.OK, errmsg='用户资料修改成功')


# 127.0.0.1:5000/user/info
@profile_bp.route('/info')
@user_login_data
def user_info():
	"""
	展示用户中心信息
	:return:
	"""
	user = g.user

	# 组织返回数据
	data = {
		'user_info': user.to_dict() if user else None
	}

	return render_template('profile/user.html', data=data)
