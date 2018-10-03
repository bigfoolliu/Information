#!-*-coding:utf-8-*-
# !@Date: 2018/10/2 14:28
# !@Author: Liu Rui
# !@github: bigfoolliu


"""
自定义的过滤器
"""


def do_index_class(index):
	"""根据index的下标返回对应的class值"""
	if index == 0:
		return 'first'
	elif index == 1:
		return 'second'
	elif index == 2:
		return 'third'
	else:
		return ''
