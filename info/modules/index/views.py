#!-*-coding:utf-8-*-
# !@Date: 2018/9/28 15:24
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
/info/modules/index/views.py存放当前模块的所有视图函数
"""
# 导入蓝图
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import index_bp

# import logging
from info import redis_store, constants
from flask import current_app, session, jsonify, request, g
# 导入创建好的模型,即与模型进行关联
from info.models import User, News, Comment, Category, CommentLike

from flask import render_template


@index_bp.route('/')
@user_login_data
def index():
	"""
	返回新闻首页
	:return:
	"""
	# 通过装饰器中的g对象获取当前登录的用户,而将之前的验证代码删除
	user = g.user

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

	# --------------------------查询新闻分类-------------------------------
	"""
	请求根路由的时候去查询新闻分类,并默认第一个被选中
	"""
	categories = None
	try:
		# 获取新闻分类数据
		categories = Category.query.all()
	except Exception as e:
		current_app.logger.error(e)
		jsonify(erron=RET.DBERR, errmsg='mysql查询数据异常')

	# 定义列表保存分类数据
	categories_dicts = []

	# 注意此处与课件的不同
	for category in categories:
		# 拼接内容
		categories_dicts.append(category.to_dict())

	# print(categories_dicts)
	# 组织响应数据字典
	data = {
		'user_info': user.to_dict() if user else None,
		'news_info': news_rank_dict_list,
		'categories': categories_dicts
	}

	# 返回模板
	return render_template('news/index.html', data=data)


@index_bp.route('/favicon.ico')
def favicon():
	"""
	返回网页tab的图标
	:return:
	"""
	return current_app.send_static_file('news/favicon.ico')  # 注意路径是相对于静态目录


"""
新闻列表数据:

点击列表数据需要去获取当前分类下的新闻数据
展示的时候需要更新新闻列表界面,不必整体页面刷新
新闻数据使用ajax的方式去请求后台接口获取

接口设计:

URL：/news_list
请求方式：GET
传入参数：JSON格式
参数:
参数名		类型		是否必须		参数说明
cid			string	是			顶层的类别id
page		int		否			当前页数，不传即获取第1页
per_page	int		否			每页多少条数据，如果不传，默认10条
"""


@index_bp.route('/news_list')
def get_news_list():
	"""
	新闻列表的后端接口
	:return:
	"""
	# 获取参数
	param_dict = request.args  # 参数字典
	page = param_dict.get('p', '1')  # 当前页面,默认为1
	per_page = param_dict.get('per_page', constants.HOME_PAGE_MAX_NEWS)  # 每页的新闻条数,默认为10
	cid = param_dict.get('cid', '1')  # 新闻分类,默认为1,即'最新'

	# 非空判断
	if not cid:
		return jsonify(erron=RET.PARAMERR, errmsg='参数cid不存在')

	try:
		# 数据类型转换
		cid = int(cid)
		page = int(page)
		per_page = int(per_page)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.PARAMERR, errmsg='参数内容格式错误')

	# 查询数据并分页
	filters = []
	# 如果分类id不为1,添加分类id的过滤
	if cid != 1:
		# == 在sqlalchemy底层有重写__eq__方法，改变了该返回值，返回是一个查询条件
		filters.append(News.category_id == cid)

	# 分页查询,利用*filters拆包
	try:
		# 分页,根据新闻创建时间倒序,分页函数paginate(),得到是paginate对象
		paginate = News.query.filter(*filters).\
			order_by(News.create_time.desc()).paginate(page, per_page, False)
		# 获取查询出来页码的所有数据
		news_list = paginate.items
		# 获取到总的页数
		total_page = paginate.pages
		# 获取到当前的页码
		current_page = paginate.page
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.DBERR, errmsg='查询分页数据异常')

	# 对象列表转换成新闻字典列表
	news_dict_list = []
	for news in news_list if news_list else []:
		news_dict_list.append(news.to_dict())

	data = {
		'news_list': news_dict_list,
		'current_page': current_page,
		'total_page': total_page
	}

	# 返回数据
	return jsonify(
		erron=RET.OK,
		errmsg='新闻详细数据查询成功',
		data=data
	)

