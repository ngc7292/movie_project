#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'ralph'
__mtime__ = '2020/1/27'
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
             ┏┓   ┏┓
            ┏┛┻━━━┛┻┓
            ┃       ┃
            ┃ ┳┛ ┗┳ ┃
            ┃   ┻   ┃
            ┗━┓   ┏━┛
              ┃   ┗━━━┓
              ┃神兽保佑┣┓
              ┃永无BUG  ┏┛
              ┗┓┓┏━┳┓┏━┛
               ┃┫┫ ┃┫┫
               ┗┻┛ ┗┻┛
"""
import requests
from bs4 import BeautifulSoup
from py2neo import Node, Relationship, Graph
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_friend_from_page(url, cookie, page):
    if page != 1:
        url += f"?page={page}"
    
    headers = {
        'Cookie': cookie,
    }
    
    r = requests.get(url, headers=headers)
    
    soup = BeautifulSoup(r.text, "html.parser")
    
    users = []
    
    for user in soup.find_all('table'):
        i = 5
        while(i):
            try:
                name = user.text.split("粉丝")[0]
                name = name.replace("(备注)","")
                users.append([name, user.a['href'].split('/')[-1]])
                break
            except:
                logger.error(f"重试{i}...")
                time.sleep(1)
    
    return users


class get_friend:
    def __init__(self, username="15254487108", password="feizhaoye"):
        self.login_cookie = self.login(username, password)
    
    def login(self, username, password):
        global login_cookie
        headers = {
            'Host': 'passport.weibo.cn',
            'Connection': 'close',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        url = "https://passport.weibo.cn/signin/login"
        r = requests.get(url, headers=headers)
        for i in r.headers['Set-Cookie'].split('; '):
            # print(i)
            taget, context = i.split('=')
            if taget == "login":
                login_cookie = context
                break
        
        headers = {
            'Host': 'passport.weibo.cn',
            'Connection': 'keep-alive',
            'Content-Length': '148',
            'Origin': 'https://passport.weibo.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/79.0.3945.130 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://passport.weibo.cn/signin/login',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cookie': f'login={login_cookie}'
        }
        
        post_data = {
            'username': username,
            'password': password,
            'savestate': '1',
            'r': '',
            'ec': '0',
            'pagerefer': '',
            'entry': 'mweibo',
            'wentry': '',
            'loginfrom': '',
            'client_id': '',
            'code': '',
            'qq': '',
            'mainpageflag': '1',
            'hff': '',
            'hfp': ''
        }
        
        r = requests.post("https://passport.weibo.cn/sso/login", post_data, headers=headers)
        
        # print(r.headers)
        res = r.headers['Set-Cookie']
        logger.info("login success!")
        return res
    
    def get_friends(self, u):
        cookie = self.login_cookie
        
        headers = {
            'Cookie': cookie
        }
        
        url = f"https://weibo.cn/{u}/fans"
        
        r = requests.get(url, headers=headers)
        
        soup = BeautifulSoup(r.text, "html.parser")
        i = 3
        while i:
            try:
                page_num = soup.find('div', class_='pa').find('input')['value']
                break
            except Exception as e:
                print(r.text)
                logger.error(e)
                time.sleep(30)
                i -= 1
                if i == 0:
                    page_num = 2
                    break
                logger.info(f"retry {2-i} times...")
        user = []
        
        for i in range(1, int(page_num)):
            user += get_friend_from_page(url, cookie, i)
        
        return user


def load_friends(u, username, index, g_class, graph):
    if index == 0: return
    
    logger.info(f"get {username}'s firends...")
    
    friends = g_class.get_friends(u)
    host = graph.nodes.match("User", user_id=u).first()
    if host is None:
        host = Node("User", name=username, user_id=u)
        graph.create(host)
        
        logger.info(f"create node {username}")
    
    for name, user_id in friends:
        node = graph.nodes.match("User", user_id=user_id).first()
        if node is None:
            node = Node("User", name=name, user_id=user_id)
            graph.create(node)
            
            logger.info(f"create node {name}")
        
        r = Relationship(node, "FOLLOWS", host)
        
        logger.info(f"create relation from {name} to {username}")
        
        graph.create(r)
        load_friends(user_id, name, index-1, g_class, graph)


if __name__ == '__main__':
    a = get_friend()
    graph = Graph('http://localhost:7474', username='neo4j', password='feizhaoye001')
    load_friends("3730166170", "英子和鸭头", 2, a, graph)
