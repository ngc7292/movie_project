#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'ralph'
__mtime__ = '2020/2/10'
# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
"""
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from py2neo import Graph, Node, Relationship
import jieba
import os
import jieba.posseg as pseg


class Question:
    def __init__(self):
        self.vec = CountVectorizer()
        self.model = MultinomialNB()
        
        jieba.load_userdict("dict.txt")
        jieba.enable_paddle()
        
        self.process_model()
        self.graph = Graph('http://localhost:7474', username='*****', password='*****')
    
    # data init
    
    def load_question(self):
        """
        :return: [data,lable] in a list
        """
        file_list = os.listdir("./question")
        
        res = []
        for file in file_list:
            label = file.split("】")[0].split("【")[1]
            file = "./question/" + file
            
            data = []
            with open(file, "r") as f:
                file_data = f.readlines()
                for file_line in file_data:
                    file_line = file_line.replace("\ufeff", "").replace("\n", "")
                    
                    data.append([file_line, label])
            res += data
        
        return res
    
    def questions_process(self):
        """
        :return: return x_data,y_data
        """
        data_list = self.load_question()
        
        stop_words = ["什么", "是", "的", "多少", "有"]
        
        x_data = []
        y_data = []
        for data in data_list:
            x_data.append(self.question_process(data[0]))
            
            y_data.append(data[1])
        
        return x_data, y_data
    
    def question_process(self, x_data):
        x_data = x_data.replace("nnt", "PER").replace("nnr", "PER").replace("nm", "nw").replace("ng", "n")
        
        cut_data = pseg.cut(x_data)
        
        stop_words = ["什么", "是", "的", "多少", "有"]
        
        words_list = []
        for word, flag in cut_data:
            if word not in stop_words:
                words_list.append(word)
        
        return " ".join(words_list)
    
    # init model
    
    def process_model(self):
        x_data, y_data = self.questions_process()
        
        self.vec = CountVectorizer()
        x_data = self.vec.fit_transform(x_data)
        
        y_data = [int(i) for i in y_data]
        
        self.model.fit(x_data, y_data)
    
    def get_feature_name(self):
        for item in self.vec.get_feature_names():
            print(item)
    
    def predict(self, x_test_data):
        # init test_data
        
        cut_data = pseg.cut(x_test_data)
        stop_words = ["什么", "是", "的", "多少", "有"]
        
        word_list = []
        for word, flag in cut_data:
            if flag == "PER":
                word_list.append("PER")
            elif flag == "nw":
                word_list.append("nw")
            else:
                word_list.append(word)
        
        # print(word_list)
        a = " ".join(word_list)
        x_test_data = self.vec.transform([a])
        
        # print(x_test_data.toarray())
        
        return self.model.predict(x_test_data)
    
    def merge_from_graph(self, question):
        q_type = self.predict(question)[0]
        
        print(q_type)
        cut_data = pseg.cut(question)
        if q_type == 0:
            for item, flag in cut_data:
                if flag == "nw":
                    m_s = self.get_score(item)
                    if not m_s:
                        continue
                    else:
                        return item + "在豆瓣电影上的综合评分为" + m_s[0]['rate']
        elif q_type == 1:
            for item, flag in cut_data:
                if flag == "nw":
                    m_s = self.get_time(item)
                    if not m_s:
                        continue
                    else:
                        return item + "的上映时间为" + m_s[0]['p_date']
        elif q_type == 2:
            for item, flag in cut_data:
                if flag == "nw":
                    m_s = self.get_type(item)
                    if not m_s:
                        continue
                    else:
                        return item + "是" + ",".join(m_s[0]['t_list']) + "之类的电影"
        elif q_type == 3:
            for item, flag in cut_data:
                if flag == "nw":
                    m_s = self.get_des(item)
                    if not m_s:
                        continue
                    else:
                        return m_s[0]['des']
        elif q_type == 4:
            for item, flag in cut_data:
                if flag == "nw":
                    m_s = self.get_movie_actor(item)
                    if not m_s:
                        continue
                    else:
                        return item + "的主要演员有" + ",".join(m_s[0]['actors'])
        elif q_type == 5:
            for item, flag in cut_data:
                if flag == "PER" or flag == "nr":
                    m_s = self.get_actor_des(item)
                    if not m_s:
                        continue
                    else:
                        return m_s[0]['des']
        elif q_type == 15:
            a_flag = 1
            for item, flag in cut_data:
                if a_flag == 1 and (flag == "PER" or flag == "nr"):
                    a_flag = 0
                    person_name = item
                elif a_flag == 0:
                    # print(self.graph.run(f'match (nn:type) where nn.t_name=~"{item}.*" return nn').data())
                    if self.graph.run(f'match (nn:type) where nn.t_name=~"{item}.*" return nn').data():
                        type = item
                        res = self.get_actor_type_to_movie(person_name, type)
                        if not res:
                            continue
                        else:
                            return "该演员演的" + type + "电影主要有" + ",".join(res[0]['m_list'])
        elif q_type == 7 or q_type == 6:
            for item, flag in cut_data:
                if flag == "PER" or flag == "nr":
                    m_s = self.get_actor_movie(item)
                    if not m_s:
                        continue
                    else:
                        return item + "主要演过" + ",".join(m_s[0]['m_list'])
        elif q_type == 8:
            a_flag = 0
            for item, flag in cut_data:
                if flag == "PER" or flag == "nr":
                    person = item
                    a_flag = 1
                elif a_flag == 1:
                    if flag == "m":
                        m_s = self.get_actor_up_movie(person, item)
                        if not m_s:
                            continue
                        else:
                            if not m_s[0]['m_list']:
                                return person + "没有高于该分数的影片"
                            return person + "的电影中超过" + item + "的影片有以下几部:" + ",".join(
                                [m_name + ":" + str(m_score) for m_name, m_score in m_s[0]['m_list']])
        elif q_type == 9:
            a_flag = 0
            for item, flag in cut_data:
                if flag == "PER" or flag == "nr":
                    person = item
                    a_flag = 1
                elif a_flag == 1:
                    if flag == "m":
                        m_s = self.get_actor_low_movie(person, item)
                        if not m_s:
                            continue
                        else:
                            if not m_s[0]['m_list']:
                                return person + "没有低于该分数的影片"
                            else:
                                return person + "的电影中低于" + item + "的影片有以下几部：" + ",".join(
                                    [m_name + ":" + str(m_score) for m_name, m_score in m_s[0]['m_list']])
        elif q_type == 10:
            for item, flag in cut_data:
                if flag == "PER" or flag == "nr":
                    m_s = self.get_actor_type(item)
                    if not m_s:
                        continue
                    else:
                        res = []
                        for i in m_s[0]['t_list']:
                            if i not in res:
                                res.append(i)
                        return item + "主要演过" + ",".join(res)
        elif q_type == 11:
            pass
        elif q_type == 12:
            pass
        elif q_type == 13:
            pass
        elif q_type == 14:
            pass
        
        with open("new_question.log","a") as f:
            f.write(question+"\n")
        return "暂时理解不了你的问题,但是已经放入后台了呢。"
    
    def get_score(self, movie_name):
        r_data = self.graph.run(
            'match (n:movie) where n.m_name=~"%s.*" return n.m_name as m_name, n.m_rate as rate' % movie_name).data()
        return r_data
    
    def get_time(self, movie_name):
        r_data = self.graph.run(
            'match (n:movie) where n.m_name=~"%s.*" return n.m_name as m_name, n.m_p_date as p_date' % movie_name).data()
        return r_data
    
    def get_type(self, movie_name):
        r_data = self.graph.run(
            'match (n:movie)-[r:is]-(nn:type) where n.m_name=~"%s.*" return n.m_name as m_name,nn.t_name as type' % movie_name).data()
        
        res = []
        t_list = []
        m_name = ""
        for i in range(len(r_data) + 1):
            if i < len(r_data):
                t_data = r_data[i]
            if m_name != t_data['m_name'] or i == len(r_data):
                if m_name != "":
                    res.append({
                        'm_name': m_name,
                        't_list': t_list
                    })
                t_list = [t_data['type']]
                m_name = t_data['m_name']
            else:
                t_list.append(t_data['type'])
        return res
    
    def get_des(self, movie_name):
        r_data = self.graph.run(
            'match (n:movie) where n.m_name=~"%s.*" return n.m_name as m_name, n.m_des as des' % movie_name).data()
        return r_data
    
    def get_movie_actor(self, movie_name):
        r_data = self.graph.run(
            'match (nn:person)-[r:act]-(n:movie) where n.m_name=~"%s.*" return n.m_name as m_name,nn.p_name as a_name' % movie_name).data()
        
        res = []
        ac_list = []
        m_name = ""
        for i in range(len(r_data) + 1):
            if i != len(r_data):
                item = r_data[i]
            if m_name != item['m_name'] or i == len(r_data):
                if m_name != "":
                    res.append({
                        'm_name': m_name,
                        'actors': ac_list
                    })
                
                ac_list = [item['a_name']]
                m_name = item['m_name']
            else:
                ac_list.append(item['a_name'])
        
        return res
    
    def get_actor_des(self, a_name):
        r_data = self.graph.run(
            'match (n:person) where n.p_name=~"%s.*" return n.p_name as a_name,n.p_des as des' % a_name).data()
        return r_data
    
    def get_actor_type_to_movie(self, a_name, type):
        r_data = self.graph.run(
            'match (nn:person)-[r:act]-(n:movie)-[rr:is]-(t:type) where nn.p_name=~"%s.*" and t.t_name="%s" return nn.p_name as a_name,n.m_name as m_name' % (
                a_name, type)).data()
        
        res = []
        m_list = []
        actor_name = ""
        
        for i in range(len(r_data) + 1):
            if i < len(r_data):
                item = r_data[i]
            if actor_name != item['a_name'] or i == len(r_data):
                if actor_name != "":
                    res.append({
                        'a_name': actor_name,
                        'm_list': m_list
                    })
                
                m_list = [item['m_name']]
                actor_name = item['a_name']
            else:
                m_list.append(item['m_name'])
        return res
    
    def get_actor_movie(self, a_name):
        r_data = self.graph.run(
            'match (nn:person)-[r:act]-(n:movie) where nn.p_name=~"%s.*" return nn.p_name as a_name,n.m_name as m_name' % a_name).data()
        
        res = []
        m_list = []
        actor_name = ""
        
        for i in range(len(r_data) + 1):
            if i < len(r_data):
                item = r_data[i]
            if actor_name != item['a_name'] or i == len(r_data):
                if actor_name != "":
                    res.append({
                        'a_name': actor_name,
                        'm_list': m_list
                    })
                
                m_list = [item['m_name']]
                actor_name = item['a_name']
            else:
                m_list.append(item['m_name'])
        return res
    
    def get_actor_up_movie(self, a_name, score):
        score = float(score)
        r_data = self.get_actor_movie(a_name)
        
        if r_data:
            res = {
                'a_name': r_data[0]['a_name'],
                'm_list': []
            }
            m_list = r_data[0]['m_list']
            for m in m_list:
                rate = self.get_score(m)
                if rate:
                    rate = float(rate[0]['rate'])
                    if rate > score:
                        res['m_list'].append([m, rate])
            
            return [res]
        else:
            return r_data
    
    def get_actor_low_movie(self, a_name, score):
        score = float(score)
        r_data = self.get_actor_movie(a_name)
        
        if r_data:
            res = {
                'a_name': r_data[0]['a_name'],
                'm_list': []
            }
            m_list = r_data[0]['m_list']
            for m in m_list:
                rate = self.get_score(m)
                if rate:
                    rate = float(rate[0]['rate'])
                    if rate < score:
                        res['m_list'].append([m, rate])
            
            return [res]
        else:
            return r_data
    
    def get_actor_type(self, a_name):
        r_data = self.graph.run(
            'match (nn:person)-[r:act]-(n:movie)-[rr:is]-(t:type) where nn.p_name=~"%s.*" return nn.p_name as a_name,t.t_name as type' % a_name).data()
        
        res = []
        t_list = []
        actor_name = ""
        
        for i in range(len(r_data) + 1):
            if i < len(r_data):
                item = r_data[i]
            if actor_name != item['a_name'] or i == len(r_data):
                if actor_name != "":
                    res.append({
                        'a_name': actor_name,
                        't_list': t_list
                    })
                
                t_list = [item['type']]
                actor_name = item['a_name']
            else:
                t_list.append(item['type'])
        return res
    
    def get_actors_movie(self, a_name1, a_name2):
        m_data1 = self.get_actor_movie(a_name1)
        m_data2 = self.get_actor_movie(a_name2)
        
        if not m_data1 or m_data1[0]['a_name'] != a_name1:
            return []
        elif not m_data2 or m_data2[0]['a_name'] != a_name2:
            return []
        else:
            m_list1 = m_data1[0]['m_list']
            m_list2 = m_data2[0]['m_list']
            
            if not m_list1 or not m_list2:
                return []
            else:
                m_list = []
                for m in m_list2:
                    if m in m_list1:
                        m_list.append(m)
                return [{
                    'a_name1': a_name1,
                    'a_name2': a_name2,
                    'm_list': m_list
                }]
    
    def get_actor_movie_count(self, a_name):
        r_data = self.graph.run(
            'match (nn:person)-[r:act]-(n:movie) where nn.p_name=~"%s.*" return nn.p_name as a_name,count(n) as count' % a_name).data()
        return r_data
    
    def get_actor_birthday(self, a_name):
        return []


if __name__ == '__main__':
    q = Question()
    # a = q.predict("张子枫和刘涛一起演过什么电影")
    # print(a)
    # print(q.get_actor_up_movie("张子枫",2))
    print(q.get_score("我和我的祖国"))
    print(q.get_time("我和我的祖国"))
    print(q.get_type("宠爱"))
    print(q.get_des("宠爱"))
    print(q.get_movie_actor("宠爱"))
    print(q.get_actor_des("张子枫"))
    print(q.get_actor_type_to_movie("张子枫", "爱情"))
    print(q.get_actor_movie("张子枫"))
    print(q.get_actor_up_movie("张子枫", 2))
    print(q.get_actor_low_movie("张子枫", 8))
    print(q.get_actor_type("张子枫"))
    print(q.get_actors_movie("张子枫", "徐峥"))
    print(q.get_actor_movie_count("张子枫"))
    
    print(q.merge_from_graph("宠爱的评分是多少"))
    print(q.merge_from_graph("宠爱什么时间上映"))
    print(q.merge_from_graph("宠爱是什么格调的电影"))
    print(q.merge_from_graph("宠爱的内容有什么"))
    print(q.merge_from_graph("宠爱的演员有哪些"))
    print(q.merge_from_graph("张子枫是谁"))
    print(q.merge_from_graph("张子枫演过什么爱情电影"))
    print(q.merge_from_graph("张子枫演了什么电影"))
    print(q.merge_from_graph("张子枫演的电影评分超过3的有哪些"))
    print(q.merge_from_graph("张子枫演的电影评分低于6的有哪些"))
    print(q.merge_from_graph("张子枫演过那些风格的电影"))
    
    print(q.merge_from_graph("张真诚是谁吗"))
