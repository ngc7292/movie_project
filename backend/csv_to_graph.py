#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'ralph'
__mtime__ = '2020/2/7'
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
"""
from py2neo import Graph, Node, Relationship
import logging
import re

graph = Graph('http://localhost:7474', username='*****', password='*****')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_file(file_name):
    with open(file_name, "r") as f:
        
        while 1:
            item = f.readline().replace("\n","")
            
            if item is None:
                yield None
            
            while item.find("\\") != -1:
                item = item.replace("\\","")
                item += f.readline().replace("\n","")
            
            yield item
            
            


def get_movie():
    g = get_file("./data/movie.csv")
    index = 0
    while 1:
        r = next(g)
        if r is None or r == "":
            break
        
        if index == 0:
            index += 1
            continue
        r = r.split("\",\"")
        
        r[0] = r[0].replace("\"", "")
        r[-1] = r[-1].replace("\"", "")
        
        m_id = r[0]
        m_name = r[1]
        m_des = r[2]
        m_rate = r[3]
        m_p_date = r[4]
        
        n = graph.nodes.match("Movie", m_id=m_id).first()
        if n is None:
            n = Node("Movie",
                     m_id=m_id,
                     m_name=m_name,
                     m_des=m_des,
                     m_p_date=m_p_date,
                     m_rate=m_rate)
    
            graph.create(n)
            logger.info("create movie node"+m_name)
    
        else:
            logger.error(m_name + " is have been created")


def get_genre():
    g = get_file("./data/genre.csv")
    index = 0
    while 1:
        try:
            r = next(g)
            
            if r is None:
                break
                
            if index == 0:
                index += 1
                continue
            r = r.split(",")
            
            t_id = r[0]
            t_name = r[1]
            
            n = graph.nodes.match("Type", t_id=t_id).first()
            if n is None:
                n = Node("Type",
                         t_id=t_id,
                         t_name=t_name,
                         )
                
                graph.create(n)
                logger.info("create movie type" + t_name)
            
            else:
                logger.error(t_name + " is have been created")
        
        except Exception as e:
            print(e)
            break


def get_person():
    g = get_file("./data/person.csv")
    index = 0
    while 1:
        try:
            r = next(g)
            
            if r is None:
                break
            if index == 0:
                index += 1
                continue
            r = r.split("\",\"")
            
            r[0] = r[0].replace("\"", "")
            r[-1] = r[-1].replace("\"", "")
            
            p_id = r[0]
            p_bir = r[1]
            p_name = r[3]
            p_des = r[4]
            p_place = r[5]
            
            n = graph.nodes.match("Person", p_id=p_id).first()
            if n is None:
                n = Node("Person",
                         p_id=p_id,
                         p_name=p_name,
                         p_bir=p_bir,
                         p_des=p_des,
                         p_place=p_place
                         )
                
                graph.create(n)
                logger.info("create person node" + p_name)
            
            else:
                logger.error(p_name + " is have been created")
        
        except Exception as e:
            print(e)
            break

def get_person_to_movie():
    g = get_file("./data/person_to_movie.csv")
    index = 0
    while 1:
        r = next(g)
        
        if r is None or r == "":
            break
        
        if index == 0:
            index += 1
            continue
        
        r = r.split("\",\"")
        
        r[0] = r[0].replace("\"", "")
        r[-1] = r[-1].replace("\"", "")
        
        p_id = r[0]
        m_id = r[1]
        
        p_node = graph.nodes.match("Person",p_id=p_id).first()
        
        m_node = graph.nodes.match("Movie",m_id=m_id).first()
        
        if p_node is None or m_node is None:
            continue
            
        r = Relationship(p_node,"act",m_node)
        
        graph.create(r)
        logger.info("create "+p_id+" to "+m_id+" relationship")
        

def get_movie_to_type():
    g = get_file("./data/movie_to_genre.csv")
    index = 0
    while 1:
        
        r = next(g)
        
        if r is None or r == "":
            break
        
        if index == 0:
            index += 1
            continue
        
        r = r.split("\",\"")
        
        r[0] = r[0].replace("\"", "")
        r[-1] = r[-1].replace("\"", "")
        
        m_id = r[0]
        t_id = r[1]
        
        t_node = graph.nodes.match("Type", t_id=t_id).first()
        
        m_node = graph.nodes.match("Movie", m_id=m_id).first()
        
        if t_node is None or m_node is None:
            continue
            
        r = Relationship(m_node, "is", t_node)
        
        graph.create(r)
        logger.info("create " + t_id + " to " + m_id + " relationship")

if __name__ == '__main__':
    # get_person()
    # get_movie()
    # get_genre()
    # get_movie_to_type()
    get_person_to_movie()
    # get_file("./data/movie.csv")
    
