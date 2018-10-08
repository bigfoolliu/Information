#!-*-coding:utf-8-*-
# !@Date: 2018/10/6 10:27
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
/info/modules/news/views.py

新闻详情页的视图函数
"""
from flask import render_template

from info.modules.news import news_bp


@news_bp.route('/<int:news_id>')
def news_detail(news_id):
	return render_template('news/detail.html')
