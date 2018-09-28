#!-*-coding:utf-8-*-
# !@Date: 2018/9/28 15:24
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
views.py存放当前模块的所有视图函数
"""
# 导入蓝图
from . import index_blu


@index_blu.route('/index')
def index():
	return 'Index Page'
