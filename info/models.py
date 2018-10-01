#!-*-coding:utf-8-*-
# !@Date: 2018/9/28 21:29
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
info/models.py存放所有的模型

User
News
Comment
CommentLike
Category

"""

from datetime import datetime
# 导入生成密码哈希以及检查密码哈希
from werkzeug.security import generate_password_hash, check_password_hash

# 导入本地文件
from info import constants
from . import db


class BaseModel(object):
	"""模型基类,为给个模型补充创建时间与更新时间"""
	# 记录创建的时间,默认为系统当前时间
	create_time = db.Column(db.DateTime, default=datetime.now)
	# 记录的更新时间
	update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


# 用户收藏表,建立用户与收藏新闻多对多的关系
tb_user_collection = db.Table(
	'info_user_collection',  # 表名
	db.Column('user_id', db.Integer, db.ForeignKey('info_user.id'), primary_key=True),  # 新闻编号
	db.Column('news_id', db.Integer, db.ForeignKey('info_news.id'), primary_key=True),  # 分类编号
	db.Column('create_time', db.DateTime, default=datetime.now)  # 收藏创建时间
)

# 用户与其关注者的表
tb_user_follows = db.Table(
	'info_user_fans',
	db.Column('follower_id', db.Integer, db.ForeignKey('info_user.id'), primary_key=True),  # 粉丝id
	db.Column('followed_id', db.Integer, db.ForeignKey('info_user.id'), primary_key=True)  # 被关注人的id
)


class User(BaseModel, db.Model):
	"""用户模型类"""
	__tablename__ = 'info_user'

	id = db.Column(db.Integer, primary_key=True)  # 编号
	nick_name = db.Column(db.String(64), unique=True, nullable=False)  # 昵称
	password_hash = db.Column(db.String(128), nullable=False)  # 哈希加密的密码
	mobile = db.Column(db.String(11), unique=True, nullable=False)  # 手机号
	avatar_url = db.Column(db.String(256))  # 用户头像路径
	last_login = db.Column(db.DateTime, default=datetime.now)  # 最后一次登录的时间
	is_login = db.Column(db.Boolean, default=False)  # 是否为管理员
	signature = db.Column(db.String(512))  # 签名
	gender = db.Column(db.Enum('MAN', 'WOMAN'), default='Man')  # 性别
	"""
	当前用户收藏的所有新闻: user.collection_news
	"""
	collection_news = db.relationship('News', secondary=tb_user_collection, lazy='dynamic')
	"""
	user.followers: 用户的所有粉丝
	user.followed: 用户关注的人
	且为反向引用
	"""
	followers = db.relationship(
		'User',
		secondary=tb_user_follows,
		primaryjoin=id == tb_user_follows.c.followed_id,
		secondaryjoin=id == tb_user_follows.c.follower_id,
		backref=db.backref('followed', lazy='dynamic'),
		lazy='dynamic'
	)  # TODO: 注意此段反向引用的写法,多对多自关联
	"""
	user.news_list: 当前用户发布的新闻
	news.user: 该新闻属于哪个用户
	"""
	news_list = db.relationship(
		'News',
		backref='user',
		lazy='dynamic'
	)

	@property  # 将password方法转化为属性可以通过User.password调用
	def password(self):
		# 显然密码是不能直接被访问的,所以报错
		raise AttributeError('当前属性不可读')

	@password.setter  # password的set方法,即可以直接通过User.password = password定义
	def password(self, value):
		self.password_hash = generate_password_hash(value)

	def check_password(self, password):
		"""
		检查密码的正确性
		:param password:
		:return: True 或者 False
		"""
		return check_password_hash(self.password_hash, password)

	def to_dict(self):
		"""
		将python类的属性转换为字典格式
		:return:
		"""
		resp_dict = {
			'id': self.id,
			'nick_name': self.nick_name,
			'avatar_url': constants.QINIU_DOMIN_PREFIX + self.avatar_url if self.avatar_url else '',
			'mobile': self.mobile,
			'gender': self.gender if self.gender else 'MAN',
			'signature': self.signature if self.signature else '',
			'followers_count': self.followers.count(),
			'news_count': self.news_list.count()
		}
		return resp_dict

	def to_admin_dict(self):
		resp_dict = {
			'id': self.id,
			'nick_name': self.nick_name,
			'mobile': self.mobile,
			'register': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
			'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S')
		}
		return resp_dict


class News(BaseModel, db.Model):
	"""新闻模型"""
	__tablename__ = 'info_news'

	id = db.Column(db.Integer, primary_key=True)  # 新闻编号
	title = db.Column(db.String(256), nullable=False)  # 新闻标题
	source = db.Column(db.String(64), nullable=False)  # 新闻来源
	digest = db.Column(db.String(512), nullable=False)  # 新闻摘要
	content = db.Column(db.Text, nullable=False)  # 新闻内容
	clicks = db.Column(db.Integer, default=0)  # 新闻浏览量
	index_image_url = db.Column(db.String(256))  # 新闻列表图片路径
	category_id = db.Column(db.Integer, db.ForeignKey('info_category.id'))  # 新闻类型id
	user_id = db.Column(db.Integer, db.ForeignKey('info_user.id'))  # 当前新闻的作者id
	status = db.Column(db.Integer, default=0)  # 当前新闻状态(0:审核通过,1:审核中,-1:审核不通过)
	reason = db.Column(db.String(256))  # 审核不通过的原因
	"""
	当前新闻的所有评论
	news.comments
	"""
	comments = db.relationship('Comment', lazy='dynamic')

	def to_review_dict(self):
		resp_dict = {
			'id': self.id,
			'title': self.title,
			'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
			'status': self.status,
			'reason': self.reason,
		}
		return resp_dict

	def to_basic_dict(self):
		resp_dict = {
			'id': self.id,
			'title': self.title,
			'source': self.source,
			'digest': self.digest,
			'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
			'index_image_url': self.index_image_url,
			'clicks': self.clicks,
		}
		return resp_dict

	def to_dict(self):
		resp_dict = {
			'id': self.id,
			'title': self.title,
			'source': self.source,
			'digest': self.digest,
			'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
			'content': self.content,
			'comments_count': self.comments.count(),
			'clicks': self.clicks,
			'category': self.category.to_dict(),
			'index_image_url': self.index_image_url,
			'author': self.user.to_dict() if self.user else None,  # TODO: 注意此处写法
		}
		return resp_dict


class Comment(BaseModel, db.Model):
	"""评论模型类"""
	__tablename__ = 'info_comment'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('info_user.id'))
	news_id = db.Column(db.Integer, db.ForeignKey('info_news.id'))
	content = db.Column(db.Text, nullable=False)
	parent_id = db.Column(db.Integer, db.ForeignKey('info_comment.id'))  # 父评论的id(自关联)
	"""
	comment.parent:该评论的父评论
	"""
	parent = db.relationship('Comment', remote_side=[id])  # 自关联
	like_count = db.Column(db.Integer, default=0)  # 点赞条数

	def to_dict(self):
		resp_dict = {
			'id': self.id,
			'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
			'content': self.content,
			'parent': self.parent.to_dict() if self.parent else None,
			'user': User.query.get(self.user_id).to_dict(),
			'news_id': self.news_id,
			'like_count': self.like_count,
		}
		return resp_dict


class CommentLike(BaseModel, db.Model):
	"""评论点赞模型类"""
	__tablename__ = 'info_comment_like'

	comment_id = db.Column('comment_id', db.Integer, db.ForeignKey('info_comment.id'), primary_key=True)  # 评论编号
	user_id = db.Column('user_id', db.Integer, db.ForeignKey('info_user.id'), primary_key=True)  # 用户编号


class Category(BaseModel, db.Model):
	"""新闻分类模型类"""
	__tablename__ = 'info_category'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), nullable=False)
	"""
	category.news_list: 该分类有哪些新闻
	news.category: 该新闻所属分类
	"""
	news_list = db.relationship(
		'News',
		backref='category',
		lazy='dynamic',
	)

	def to_dict(self):
		resp_dict = {
			'id': self.id,
			'name': self.name
		}
		return resp_dict

