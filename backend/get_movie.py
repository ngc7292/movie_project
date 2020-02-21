#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'ralph'
__mtime__ = '2020/2/5'
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
"""
import requests
import json
import logging
import time
from py2neo import Node, Relationship, Graph
from bs4 import BeautifulSoup
import re
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_name(s):
    try:
        return re.search(r"[\u4E00-\u9FA5]{2,5}(?:·[\u4E00-\u9FA5]{2,5})*", s).group()
    except Exception as e:
        logger.error(s + "re error as ")
        # print(e)
        return s


class spider():
    def __init__(self):
        self.r_session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/79.0.3945.130 Safari/537.36 '
        }
        
        self.target_list = ["热门", "最新", "经典", "冷门佳片", "华语", "欧美", "韩国", "日本", "动作", "喜剧", "爱情", "科幻", "悬疑", "恐怖", "成长"]
        
        self.movie_list = []
        self.movie_c_list = {}
    
    def get_all_target(self, n):
        for target in self.target_list[:n]:
            self.get_m_list(target)
    
    def get_m_list(self, target):
        url = f"https://movie.douban.com/j/search_subjects?type=movie&tag={target}&page_limit=5000&page_start=0"
        
        r = requests.get(url=url, headers=self.headers)
        
        try:
            j = json.loads(r.text)
            
            movies = j['subjects']
            
            logger.info(f"get {len(movies)} movies about {target}")
            
            movie_list = []
            for m in movies:
                m_id = m['id']
                m_title = m['title']
                m_jpg = m['cover']
                m_url = m['url']
                
                movie_list.append([m_id, m_title, m_jpg, m_url])
                self.movie_list.append([m_id, m_title, m_jpg, m_url])
            
            return movie_list
        
        except Exception as e:
            logger.error(target + " error")
            # print(r.text)
            return []
    
    def save_movielist(self):
        with open("movies.txt", 'wb') as f:
            f.write(json.dumps(self.movie_list).encode("utf-8"))
    
    def load_movielist(self):
        with open("movies.txt", 'rb') as f:
            self.movie_list = json.loads(f.read())
    
    def get_all_movie(self):
        
        for target in self.target_list:
            movie_list = self.get_m_list(target)
            
            for item in movie_list:
                self.get_movie(item[0])
            
            time.sleep(30)
    
    def get_movie(self, m_id):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/79.0.3945.130 Safari/537.36 '
        }
        
        url = f"https://movie.douban.com/subject/{m_id}"
        
        r = requests.get(url, headers=headers)
        
        try:
            a = r.text.split('<script type="application/ld+json">')[1].split("</script>")[0].replace("\n", "")
            
            j = json.loads(a)
            
            movie = {
                'url': j['url'],
                'id': j['url'].split("/")[-2],
                'name': j['name'],
                'director': j['director'],
                'author': j['author'],
                'actor': j['actor'],
                'p_date': j['datePublished'],
                'type': j['genre'],
                'description': j['description'],
                'rate': j['aggregateRating']['ratingValue']
            }

            try:
                b = BeautifulSoup(r.text, 'html.parser')
                des = b.find(property="v:summary").get_text()

                des = des.replace("\n", "")
                des = des.replace(" ", "")
                des = des.replace("\u3000", "")
                
                movie['description'] = des
            except:
                pass
            
            logger.info("saving " + movie['name'] + "into neo4j databases...")
            self.save_movie_to_graph(movie)
        
        except Exception as e:
            logger.error("get movie " + m_id + " error!! ")
            # print(r.text)
    
    def save_movie_to_graph(self, movie):
        graph = Graph('http://localhost:7474', username='neo4j', password='feizhaoye001')
        
        m_id = movie['id']
        
        m_node = graph.nodes.match("movie", m_id=m_id).first()
        if m_node is None:
            m_node = Node("movie", m_id=movie['id'],
                          m_name=movie['name'],
                          m_p_date=movie['p_date'],
                          m_des=movie['description'],
                          m_rate=movie['rate'])
            
            logger.info("create " + movie['name'] + "'s movie node")
            graph.create(m_node)
            
            for director in movie['director']:
                d_id = director['url'].split("/")[-2]
                d_node = graph.nodes.match("person", p_id=d_id).first()
                if d_node is None:
                    d_des = self.get_person(d_id)
                    
                    d_name = get_name(director['name'])
                    d_node = Node("person", p_id=d_id, p_name=d_name, p_des=d_des)
                    
                    logger.info("create " + d_name + "'s person node")
                    graph.create(d_node)
                
                logger.info("create " + director['name'] + " relationship.")
                r = Relationship(d_node, "direct", m_node)
                graph.create(r)
            
            for type in movie['type']:
                t_node = graph.nodes.match("type", t_name=type).first()
                if t_node is None:
                    t_node = Node("type", t_name=type)
                    
                    graph.create(t_node)
                
                r = Relationship(m_node, "is", t_node)
                graph.create(r)
            
            for author in movie['author']:
                a_id = author['url'].split("/")[-2]
                a_node = graph.nodes.match("person", p_id=a_id).first()
                if a_node is None:
                    a_des = self.get_person(a_id)
                    
                    a_name = get_name(author['name'])
                    a_node = Node("person", p_id=a_id, p_name=a_name, p_des=a_des)
                    
                    logger.info("create " + a_name + "'s person node")
                    graph.create(a_node)
                
                r = Relationship(a_node, "write", m_node)
                
                logger.info("create " + author['name'] + " relationship..")
                graph.create(r)
            
            for actor in movie['actor']:
                a_id = actor['url'].split("/")[-2]
                a_node = graph.nodes.match("person", p_id=a_id).first()
                if a_node is None:
                    a_name = get_name(actor['name'])
                    
                    a_des = self.get_person(a_id)
                    a_node = Node("person", p_id=a_id, p_name=a_name, p_des=a_des)
                    
                    logger.info("create " + a_name + "'s person node")
                    graph.create(a_node)
                
                r = Relationship(a_node, "act", m_node)
                
                logger.info("create " + actor['name'] + " relationship..")
                graph.create(r)
        else:
            logger.info(movie['name'] + "have saved...")

    def get_person(self,mid):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/79.0.3945.130 Safari/537.36 '
        }
    
        url = f"https://movie.douban.com/celebrity/{mid}/"
    
        r = requests.get(url, headers=headers)
    
        # print(r.text)
    
        # return movie
        try:
        
            b = BeautifulSoup(r.text, 'html.parser')
        
            des = b.find("div", id="intro").find("div", class_="bd")
        
            if des.find("span", class_="all hidden"): des = des.find("span", class_="all hidden")
        
            des = des.get_text()
        
            des = des.replace(" ", "")
            des = des.replace("\n", "")
            des = des.replace("\u3000", "")
        
            return des
    
        except:
            logger.error("get " + mid + " des is error")
            return ""
        
if __name__ == '__main__':
    a = spider()
    # a.get_m_list(a.target_list[0])
    # a.save_movie()
    # a.load_movie()
    # print(a.movie_list)
    a.get_all_movie()
    # print(get_name("德斯汀·克里顿 Destin Cretton"))
