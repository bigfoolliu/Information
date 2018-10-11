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
from info.modules.profile import profile_bp
from info.utils.common import user_login_data
from info.utils.pic_storage import pic_storage

from info.utils.response_code import RET


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
