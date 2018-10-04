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
from flask import current_app, session, jsonify, request
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

	# --------------------------查询新闻分类-------------------------------
	"""
	请求根路由的时候去查询新闻分类,并默认第一个被选中
	"""
	# 获取新闻分类数据
	categories = Category.query.all()
	# 定义列表保存分类数据
	categories_dicts = []

	# TODO: 注意此处与课件的不同
	for category in categories:
		# 拼接内容
		categories_dicts.append(category.to_dict())

	print(categories_dicts)
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
	return current_app.send_static_file('news/favicon.ico')  # TODO: 注意路径是相对于静态目录


"""
新闻列表数据:

点击列表数据需要去获取当前分类下的新闻数据
展示的时候需要更新新闻列表界面,不必整体页面刷新
新闻数据使用ajax的方式去请求后台接口获取

接口设计:

URL：/newslist
请求方式：GET
传入参数：JSON格式
参数:
参数名		类型		是否必须		参数说明
cid			string	是			分类id
page		int		否			页数，不传即获取第1页
per_page	int		否			每页多少条数据，如果不传，默认10条

返回类型：JSON
参数名						类型		是否必须	参数说明
errno						int		是		错误码
errmsg						string	是		错误信息
cid							string	是		当前新闻数据的分类id
total_page					int		否		总页数
current_page				int		否		当前页数
news_dict_list				list	否		新闻列表数据
newsList.title				string	是		新闻标题
newsList.source				string	是		新闻来源
newsList.digest				string	是		新闻摘要
newsList.create_time		string	是		新闻时间
newsList.index_image_url	string	是		新闻索引图

"""


@index_bp.route('/newslist')
def get_news_list():
	"""
	新闻列表的后端接口
	:return:
	"""
	# 获取参数
	args_dict = request.args
	page = args_dict.get('p', '1')
	per_page = args_dict.get('per_page', constants.HOME_PAGE_MAX_NEWS)
	category_id = args_dict.get('cid', '1')

	# 校验参数
	try:
		page = int(page)
		per_page = int(per_page)
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.PARAMERR, errmsg='参数错误')

	# 查询数据并分页
	filters = []
	# 如果分类id不为1,添加分类id的过滤
	if category_id != '1':
		filters.append(News.category_id == category_id)
	try:
		# 分页,根据新闻创建时间倒序,分页函数paginate()
		paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
		# 获取查询出来的数据
		items = paginate.items
		# 获取到总的页数
		total_page = paginate.pages
		current_page = paginate.page
	except Exception as e:
		current_app.logger.error(e)
		return jsonify(erron=RET.DBERR, errmsg='数据查询失败')

	# 新闻列表
	news_li = []
	for news in items:
		news_li.append(news.to_basic_dict())

	# 返回数据
	return jsonify(
		erron=RET.OK,
		errmsg='OK',
		total_page=total_page,
		current_page=current_page,
		newslist=news_li,
		cid=category_id)

