#!-*-coding:utf-8-*-
# !@Date: 2018/10/6 10:27
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
/info/modules/news/views.py

新闻详情页的视图函数
"""
from flask import render_template, g, current_app, jsonify, request

from info import constants, db
from info.models import News
from info.modules.news import news_bp
from info.utils.common import user_login_data


# 访问接口: 127.0.0.1:5000/news/23
from info.utils.response_code import RET


@news_bp.route('/<int:news_id>')
@user_login_data  # 使用装饰器,从而可以直接获取到其中的用户登录的消息
def news_detail(news_id):
	"""
	访问新闻详情的后端接口
	:param news_id:
	:return:
	"""
	# 获取用户的登录信息
	user = g.user

	# -----------------------获取新闻点击排行数据---------------------------
	try:
		news_rank_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.DBERR, errmsg='数据库获取新闻新闻点击排行数据异常')

	# 字典列表初始化
	news_rank_dict_list = []
	# 将新闻对象列表转换为字典列表
	for news_obj in news_rank_list if news_rank_list else []:
		# 将新闻对象转换为字典
		news_dict = news_obj.to_dict()
		# 构建字典列表
		news_rank_dict_list.append(news_dict)

	# -----------------------获取新闻详情数据---------------------------
	try:
		news = News.query.get(news_id)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.DBERR, errmsg='数据库获取新闻详情数据异常')
	# 新闻详情对象转换为字典
	news_dict = news.to_dict() if news else None

	# 每浏览一次该新闻则浏览量加1(因为配置文件中的SQLALCHEMY_COMMIT_ON_TEARDOWN = True 配置)
	news.clicks += 1

	# -----------------------查询当前用户是否收藏当前新闻---------------------------
	is_collected = False
	# 若当前用户已登录
	if user:
		# 当前新闻在用户的新闻收藏列表里则说明已经收藏
		if news in user.collection_news:
			is_collected = True

	# 组织响应数据字典
	data = {
		'user_info': user.to_dict() if user else None,
		'news_rank_list': news_rank_dict_list,
		'news': news_dict,
		'is_collected': is_collected
	}

	return render_template('news/detail.html', data=data)


# 127.0.0.1:5000/news/news_collect
@news_bp.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
	"""
	新闻收藏后端接口,点击收藏按钮,向此接口发送post请求

	1. 获取参数
		新闻id, 新闻是否收藏的动作action
	2. 校验参数
		非空判断
		action只能为收藏或非收藏[collect, cancel_collect]
	3. 逻辑处理
		根据新闻id查询到新闻
		收藏: 将当前新闻添加到user.collection_news
		取消收藏: 将当前新闻从user.collection_news中移除
	4. 返回值

	:return:
	"""
	param_dict = request.json
	news_id = param_dict.get('news_id')
	action = param_dict.get('action')

	user = g.user

	# 非空判断
	if not all([news_id, action]):
		return jsonify(erron=RET.PARAMERR, errmsg='参数不足')
	# 判断用户是否登录
	if not user:
		return jsonify(erron=RET.SESSIONERR, errmsg='用户为登录')
	# action只能有两种选择
	if action not in ['collect', 'cancel_collect']:
		return jsonify(erron=RET.PARAMERR, errmsg='参数内容错误')

	# 根据新闻id来查询新闻对象
	try:
		news = News.query.get(news_id)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.DBERR, errmsg='数据库查询新闻异常')

	if not news:
		return jsonify(erron=RET.NODATA, errmsg='新闻不存在')

	# 收藏,将新闻添加至user.collection_news中
	if action == 'collect':
		user.collection_news.append(news)
	else:
		# 取消收藏则将其从中移除
		if news in user.collection_news:
			user.collection_news.remove(news)

	# 将用户收藏列表的修改操作提交数据库
	try:
		db.session.commit()
	except Exception as e:
		current_app.logger.error(e)
		db.session.rollback()  # 注意: 数据库提交异常的回滚操作
		return jsonify(erron=RET.DBERR, errmsg='数据库保存新闻列表数据异常...')

	# 返回值
	return jsonify(erron=RET.OK, errmsg='OK')
