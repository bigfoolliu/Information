#!-*-coding:utf-8-*-
# !@Date: 2018/9/26 18:55
# !@Author: Liu Rui
# !@github: bigfoolliu


from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
	return 'Index Page'


if __name__ == '__main__':
	app.run(debug=True)
