#!-*-coding:utf-8-*-
# !@Date: 2018/9/29 20:23
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
/info/modules/passport/views.py

处理注册的业务逻辑的视图函数
"""
import random

from info import redis_store
from info.lib.sms import CCP
from info.utils.response_code import RET
from . import passport_bp
from flask import request, current_app, abort, make_response, jsonify
# 导入用于生成验证码图片的类()
from info.utils.captcha.captcha import captcha
# 导入常量
from info import constants
import re
from info.models import User

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


# 注册smscode路由,采用的第三方sdk
"""
设计好与前端的接口:

URL：/passport/sms_code
请求方式：POST

参数
传入参数：JSON格式
参数名			类型		是否必须	参数说明
mobile			string	是		手机号
image_code		string	是		用户输入的图片验证码内容
image_code_id	string	是		真实图片验证码编号

返回类型：JSON
参数名	类型		是否必须	参数说明
errno	int		是		错误码
errmsg	string	是		错误信息
"""


# 127.0.0.1:5000/passport/sms_code
@passport_bp.route('/sms_code', methods=['POST'])
def send_sms_code():
	"""
	点击发送短信验证码后发送短信验证码后端接口

	1. 获取参数
		手机号账号, 填写的图片验证码, uuid
	2. 校验参数
		非空判断, 手机号正则
	3. 逻辑处理
		由uuid查找redis数据库中对应的图片验证码真实值
			真实值存在,则将其删除(防止多次拿同一个验证啊校验)
			真实值不存在, 验证码过期,需重新获取
		比较用户填写验证码与真实验证码对比
			不等, 说明填写错误,返回信息给前端
			相等
				判断用户是否已经注册,注册则不发送短信验证码
				未注册,发送短信验证码
	4. 返回值
		发送验证码成功
	"""
	# 根据上面的接口格式,获取json格式的数据(前端需要根据该接口写ajax返回json格式参数)
	# 首先获取json格式数据,并将其转成python字典类型便于提取参数
	param_dict = request.json
	print("param_dict:", type(param_dict), param_dict)  # TODO: 测试

	# 获取该字典中的所有参数值,为方式报错,使用字典的get方法,从而可以设置默认值为空
	mobile = param_dict.get('mobile', default='')
	image_code = param_dict.get('image_code', default='')
	image_code_id = param_dict.get('image_code_id', default='')

	# 非空判断,所有单个参数都需要有值
	if not all([mobile, image_code, image_code_id]):
		# 参数不足要记录一下,同时将错误信息(按照上述接口格式)返回给前端
		current_app.logger.error('参数不足.')
		# 利用flask中的jsonify模块将字典转换为json数据返回给前端, jsonify函数的两种使用方式,推荐使用参数
		# 错误码为response_code.py文件中定义好的
		return jsonify({'errno': RET.PARAMERR, 'errmsg': '参数不足'})

	# 参数均填写完整
	# 手机号正则校验
	if not re.match('^1[34578][0-9]{9}$', mobile):
		return jsonify(erron=RET.PARAMERR, errmsg='参数不足')

	# 图片验证码校验
	# 将image_code_id(即uuid)作为key传入redis数据库对比image_code
	try:
		# 首先获取redis数据库中的值是否存在,即是否过期
		real_image_code = redis_store.get('imageCodeId_%s' % image_code_id)
	except Exception as e:
		# 获取不到redis数据库数据,说明数据库存在错误
		current_app.logger.error(e)
		return jsonify(erron=RET.DBERR, errmsg='redis数据库异常')

	# 真实值存在,则将redis中的真实值删除
	if real_image_code:
		redis_store.delete('imageCodeId_%s' % image_code_id)
	# 不存在说明过期,报无数据错误
	else:
		return jsonify(erron=RET.NODATA, errmsg='图片验证码过期')

	"""
	将用户的image_code与real_image_code对比:
	1. 不区分大小写
	2. redis对象创建(info/__init__.py)时需要添加参数: decode_responses=True
	"""
	if real_image_code != image_code:
		return jsonify(erron=RET.DATAERR, errmsg='图片验证码填写错误')

	# 判断该用户之前是否已经注册过,注册过则不应该发送短信验证码
	try:
		user = User.query.filter(User.mobile == mobile).first()
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.DBERR, errmsg='mysql数据库查询数据异常')
	# 查询到该用户已经注册
	if user:
		return jsonify(erron=RET.DATAEXIST, errmsg='用户手机号已经注册')

	# 用户未注册,发送6位随机短信验证码,不到六位用0补全
	sms_code = random.randint(0, 999999)
	sms_code = '%6d' % sms_code
	try:
		"""
		使用第三方sdk
		1. CCP类的实例来发送模板短信(此种方式不必创建显示的实例)
		2. 参数含义:
			mobile: 发送目的手机号
			{},1: 发送的短信具体内容(基于模板1)
				sms_code: sdk内置的响应码,000000表示成功,其他的表示对应的错误信息
				constants.SMS_CODE_REDIS_EXPIRES/60: 验证码过期时间,单位为分钟
		"""
		result = CCP().send_template_sms(mobile, {sms_code, constants.SMS_CODE_REDIS_EXPIRES/60}, 1)
	# 发送不了以及返回值result不为0均为错误
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.THIRDERR, errmsg='云通讯平台出现异常')
	if result != 0:
		return jsonify(erron=RET.THIRDERR, errmsg='云通讯平台出现异常')

	# 将生成的随机六位数存储进redis
	try:
		redis_store.setex('SMS_CODE_%s' % sms_code, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.DBERR, errmsg='redis存储短信验证码异常')

	# 返回值
	return jsonify(erron=RET.OK, errmsg='短信验证码发送成功')
