#!-*-coding:utf-8-*-
# !@Date: 2018/9/28 15:27
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
/info/modules/index/__init__.py

首页模块的蓝图初始化
"""

from flask import Blueprint

index_bp = Blueprint('index', __name__)

# 导入视图
from .views import *


