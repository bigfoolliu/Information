# -*- coding:utf-8 -*-

# TODO: 自己设置的基于python3的特性#, 全局取消证书验证
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from info.lib.CCPRestSDK import REST

# 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
_accountSid = '8aaf070866235bc501662599f326045d'

# 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
_accountToken = '669505a0c9784e8a925986aab3f0e35b'

# 请使用管理控制台首页的APPID或自己创建应用的APPID
_appId = '8aaf070866235bc501662599f38e0464'

# 说明：请求地址，生产环境配置成app.cloopen.com
_serverIP = 'sandboxapp.cloopen.com'

# 说明：请求端口 ，生产环境为8883
_serverPort = "8883"

# 说明：REST API版本号保持不变
_softVersion = '2013-12-26'


# 云通讯官方提供的发送短信代码实例
# # 发送模板短信
# # @param to 手机号码
# # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# # @param $tempId 模板Id
#
# def sendTemplateSMS(to, datas, tempId):
#     # 初始化REST SDK
#     rest = REST(serverIP, serverPort, softVersion)
#     rest.setAccount(accountSid, accountToken)
#     rest.setAppId(appId)
#
#     result = rest.sendTemplateSMS(to, datas, tempId)
#     for k, v in result.iteritems():
#
#         if k == 'templateSMS':
#             for k, s in v.iteritems():
#                 print '%s:%s' % (k, s)
#         else:
#             print '%s:%s' % (k, v)


class CCP(object):
	"""发送短信的辅助类"""

	def __new__(cls, *args, **kwargs):
		# 判断是否存在类属性_instance，_instance是类CCP的唯一对象，即单例,单例确保该类只有一个实例存在
		if not hasattr(CCP, "_instance"):
			cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)
			cls._instance.rest = REST(_serverIP, _serverPort, _softVersion)
			cls._instance.rest.setAccount(_accountSid, _accountToken)
			cls._instance.rest.setAppId(_appId)
		return cls._instance

	def send_template_sms(self, to, datas, temp_id):
		"""发送模板短信实际函数"""
		# @param to 手机号码
		# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
		# @param temp_id 模板Id
		result = self.rest.sendTemplateSMS(to, datas, temp_id)
		print(result)
		# 如果云通讯发送短信成功，返回的字典数据result中statusCode字段的值为"000000"
		if result.get("statusCode") == "000000":
			# 返回0 表示发送短信成功
			return 0
		else:
			# 返回-1 表示发送失败
			return -1


if __name__ == '__main__':
	ccp = CCP()
	# 注意： 测试的短信模板编号为1(2, 3为标准模板,也可以在云平台自定义模板)
	# ['6666为验证码, 2为过期时间'],选取的模板不同,可能会有差异
	ccp.send_template_sms('13135651103', ['6666', 2], 1)
