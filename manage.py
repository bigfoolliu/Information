#!-*-coding:utf-8-*-
# !@Date: 2018/9/26 18:55
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
/manage.py作为主程序的入口
	只做最基本的启动工作,app的创建移动至info的__init__.py中

其中:
	- 1. 2. ...表示程序书写的顺序
"""

# # 1. 基本配置
# from flask import Flask
# # 2. 导入数据库扩展并填写相关配置
# from flask_sqlalchemy import SQLAlchemy
# import os
# # 3. 创建Redis存储对象,并在配置中填写相关配置
# import redis
# # 4. 包含请求体的请求中都要开启CSRF
# # CSRFProtect只做验证工作，cookie中的 csrf_token 和表单中的 csrf_token 需要我们自己实现
# from flask_wtf.csrf import CSRFProtect
# # 5. session数据要保存到Redis中
# from flask_session import Session
# 6. flask_script与数据量迁移
from flask import current_app, jsonify
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
# # 7. 代码抽取,将Config单独作为一个文件,重新导入配置类
# from config import Config
# 8. 业务逻辑独立
# 除启动文件manage.py和配置问价config.py放于根目录,其他文件置于单独的文件夹,与manage.py同级
# 9. 此时需要导入创建好的app对象以及数据库对象
# from info import app, db
# 10. 对配置进行修改,可根据环境不同,快速切换配置
from info import create_app, db

# 11. 增加日志,在配置文件中增加日志等级等
from info.models import User
from info.utils.response_code import RET

app = create_app('development')  # 以开发模式配置来创建app
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)

"""
命令行创建管理员账户的方式使用方法：
	python3 manage.py createsuperuser -n "账号" -p "密码"
	python3 manage.py createsuperuser --name "账号" --password "密码"
"""


"""
使用 flask-script 扩展添加命令行相关逻辑操作
这样做的好处是:
	相对比较安全
	区别于一般用户的创建
	管理员用户的数量都是极少的
"""


# 用装饰器的方式来给manager添加特定的参数
@manager.option('-n', '--name', dest='name')
@manager.option('-p', '--password', dest='password')
def createsuperuser(name, password):
	"""
	创建管理员用户对象
	:param name:
	:param password:
	:return:
	"""
	if not all([name, password]):
		return '参数不足'  # 显示在命令行
	# 开始创建
	admin_user = User()
	admin_user.nick_name = name
	admin_user.mobile = name
	admin_user.password = password
	# 添加一个额外的属性,设置为管理员
	admin_user.is_admin = True

	# 将该管理员保存至数据库
	try:
		db.session.add(admin_user)
		db.session.commit()
	except Exception as e:
		current_app.logger.error(e)
		db.session.rollback()
		return jsonify(erron=RET.DBERR, errmsg='数据库存储管理员用户异常')

	# TODO: 测试
	admin_user_dict = {
		'nick_name': admin_user.nick_name,
		'mobile': admin_user.mobile,
		'is_admin': admin_user.is_admin
	}

	# 成功
	return '创建管理员账户成功', admin_user_dict


if __name__ == '__main__':
	# 在启动中配置参数runserver,以及环境变量
	manager.run()
