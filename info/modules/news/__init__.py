#!-*-coding:utf-8-*-
# !@Date: 2018/10/6 10:26
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
/info/modules/news/__init__.py

新闻详情页的初始化
"""


# 创建新的蓝图
from flask import Blueprint

news_bp = Blueprint('news', __name__, url_prefix='/news')

# 引入视图
from . import views
