#!-*-coding:utf-8-*-
# !@Date: 2018/9/28 15:24
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
/info/modules/index/views.py存放当前模块的所有视图函数
"""
# 导入蓝图
from info.utils.response_code import RET
from . import index_bp

# import logging
from info import redis_store, constants
from flask import current_app, session, jsonify
# 导入创建好的模型,即与模型进行关联
from info.models import User, News, Comment, Category, CommentLike

from flask import render_template


@index_bp.route('/')
def index():
	"""
	返回新闻首页
	:return:
	"""
	# --------------------------获取用户登录信息----------------------------
	# 获取当前登录用户的id
	user_id = session.get('user_id')
	user = None  # type:User
	# 通过id查询用户对象
	if user_id:
		try:
			user = User.query.get(user_id)
		except Exception as e:
			current_app.logger.error(e)
			return jsonify(erron=RET.DBERR, errmsg='mysql查询用户对象异常')

	# -------------------------获取新闻点击排行数据--------------------------
	"""
	将新闻在数据库中按照clicks的数字递减,然后获取前一定的条数(此处为6)显示
	"""
	try:
		news_rank_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.DBERR, errmsg='mysql数据库获取news数据异常')

	# 将获取到的新闻列表转换为字典列表[news1, news2, ...]----->[{news1}, {news2}, ...]
	news_rank_dict_list = []
	for news_obj in news_rank_list:
		news_dict = news_obj.to_dict()
		news_rank_dict_list.append(news_dict)

	# 组织响应数据字典
	data = {
		'user_info': user.to_dict() if user else None,
		'news_info': news_rank_dict_list
	}

	# 返回模板
	return render_template('news/index.html', data=data)


@index_bp.route('/favicon.ico')
def favicon():
	"""
	返回网页tab的图标
	:return:
	"""
	return current_app.send_static_file('news/favicon.ico')  # TODO: 注意路径是相对于静态目录
