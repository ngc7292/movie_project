#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'ralph'
__mtime__ = '2020/2/10'
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
"""
from py2neo import Graph, Node, Relationship

graph = Graph('http://localhost:7474', username='****', password='*****')

movie_name = "我和我的祖国"
s = graph.run('match (nn:type) where nn.t_name=~"张子枫.*" return nn').data()

print(type(s))
print(s)