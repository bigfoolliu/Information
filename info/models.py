#!-*-coding:utf-8-*-
# !@Date: 2018/9/28 21:29
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
info/models.py存放所有的模型
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


class User(BaseModel):
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

	@property
	def password(self):
		raise AttributeError('当前属性不可读')

	@password.setter
	def password(self, value):
		self.password_hash = generate_password_hash(value)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def to_dict(self):
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


# TODO: 写新闻模型
