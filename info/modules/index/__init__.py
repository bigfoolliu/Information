#!-*-coding:utf-8-*-
# !@Date: 2018/9/28 15:27
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
创建自己的蓝图
"""

from flask import Blueprint

index_blu = Blueprint('index', __name__)

# 导入视图
from . import views

