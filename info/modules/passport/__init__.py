#!-*-coding:utf-8-*-
# !@Date: 2018/9/29 16:04
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
/info/modules/passport/__init__.py

注册蓝图的初始化
"""
from flask import Blueprint

passport_bp = Blueprint('passport', __name__, url_prefix='/passport')

# 导入视图函数
from . import views

