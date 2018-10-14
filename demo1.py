#!-*-coding:utf-8-*-
# !@Date: 2018/10/13 17:41
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
用于创建多个虚拟用户用于测试
"""
import datetime
import random

from info import db
from info.models import User
from manage import app


def add_test_users():
	"""
	添加测试用户
	:return:
	"""
	users = []
	now = datetime.datetime.now()

	# 创建100个用户
	for num in range(0, 100):
		try:
			user = User()
			user.nick_name = "%011d" % num
			user.mobile = '%011d' % num
			user.password_hash = 'pbkdf2:sha256:50000$SgZPAbEj$a253b9220b7a916e03bf27119d401c48ff4a1c81d7e00644e0aaf6f3a8c55829'
			"""
			2678400秒为一个月(31天)的秒数
			用户上次的登录时间为现在-上个月的现在
			"""
			user.last_login = now - datetime.timedelta(seconds=random.randint(0, 2678400))
			users.append(user)
			print(user.mobile)
		except Exception as e:
			print(e)

	# 手动开启应用上下文
	with app.app_context():
		db.session.add_all(users)
		db.session.commit()

	print('添加用户完成')


if __name__ == '__main__':
	add_test_users()
