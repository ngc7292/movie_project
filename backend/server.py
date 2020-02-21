#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'ralph'
__mtime__ = '2020/2/16'
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
"""
from flask import Flask
from question import Question
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

q = Question()


@app.route('/<question>', methods=['GET'])
def index(question):
    return q.merge_from_graph(question)


if __name__ == "__main__":
    # 这种是不太推荐的启动方式，我这只是做演示用，官方启动方式参见：http://flask.pocoo.org/docs/0.12/quickstart/#a-minimal-application
    
    app.run(host="0.0.0.0", debug=True)
