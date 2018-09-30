#!-*-coding:utf-8-*-
# !@Date: 2018/9/29 20:23
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
/info/modules/passport/views.py

处理注册的业务逻辑的视图函数
"""
from info import redis_store
from . import passport_bp
from flask import request, current_app, abort, make_response
# 导入用于生成验证码图片的类()
from info.utils.captcha.captcha import captcha
# 导入常量
from info import constants


# 127.0.0.1:5000/passport/image_code?code_id=uuid编码
@passport_bp.route('/image_code')
def get_image_code():
	"""
	获取图形验证码(GET请求)

	1. 获取参数
	2. 校验参数
	3. 业务逻辑
	4. 返回值
	"""
	# 从请求request中获取code_id(即uuid码)
	code_id = request.args.get('code_id')

	# 非空判断,为空则404报错
	if not code_id:
		current_app.logger.error('参数不足.')
		abort(404)
	"""
	生成验证码图片,包括名字,验证码值,以及图片(返回的是二进制的数据)
	"""
	image_name, real_image_code, image_data = captcha.generate_captcha()
	# 以code_id作为key,real_image_code作为value存入redis数据库,便于之后的校验,同时加入过期时间
	# 操作数据库可能产生异常,因此均使用try-except语句
	try:
		redis_store.setex('imageCodeId_%s' % code_id, constants.IMAGE_CODE_REDIS_EXPIRES, real_image_code)
	except Exception as e:
		# 记录服务器数据库交互产生的错误
		current_app.logger.error(e)
		abort(500)

	# 为确保返回的二进制格式图片能被所有浏览器识别,将其转换
	response = make_response(image_data)
	# 将响应数据的内容类型Content-Type更改
	response.headers['Content-Type'] = 'image/JPEG'
	return response

