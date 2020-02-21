#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'ralph'
__mtime__ = '2020/2/8'
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
"""
from py2neo import Graph,Node,Relationship
import re

graph = Graph('http://localhost:7474', username='*****', password='*****')

def get_name(s):
    return re.search(r"[\u4E00-\u9FA5]*",s).group()

def save_word(word,type):
    with open("dict.txt","a") as f:
        f.write("\n"+word+" "+type)
        
def get_movie():
    
    movie_match = graph.nodes.match("movie")
    
    for movie in movie_match:
        movie_name = get_name(movie['m_name'])
        if movie_name != "":
            save_word(movie_name,"nw")
        
    
def get_person():
    person_match = graph.nodes.match("person")
    
    for movie in person_match:
        person_name = get_name(movie['p_name'])
        if person_name != "":
            save_word(person_name, "PER")


if __name__ == '__main__':
    get_movie()
    get_person()
    