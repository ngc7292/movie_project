#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'ralph'
__mtime__ = '2020/2/10'
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
"""
import jieba
import jieba.posseg as pseg

jieba.load_userdict("dict.txt")
cut_data = pseg.cut("张子枫的评分是多少")

for word,flag in cut_data:
    print(word,flag)