#!-*-coding:utf-8-*-
# !@Date: 2018/10/10 20:03
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
info/modules/profile/__init__.py
"""
from flask import Blueprint

profile_bp = Blueprint('profile', __name__, url_prefix='/user')

from .views import *
