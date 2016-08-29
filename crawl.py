#!/usr/bin/env python
# -*-coding:utf-8-*-

from requests import get, HTTPError, ConnectionError
from bs4 import BeautifulSoup as bs
from sys import argv
from re import search, findall
from time import sleep
from threading import Thread
ms_th = None
for_th = None

class PTT_CRAWL(Thread):
   
    def __init__(self, board, last_index):
        super(PTT_CRAWL, self).__init__()
        self.count = 0
        self.base = 'https://www.ptt.cc'
        self.board = board
        self.last_pgnum = last_index
        self.collect_dict = {}
        self.new_post = {}
        self.include_list = []
        self.exclude_list = []

    def run(self):
        print "Start Crawl the board %s\n" %self.board
        self.crawl_timing() 

    def __str__(self):
        print self.board, self.last_pgnum, self.collect_dict
        print self.collect_dict
        return '{0}'.format(self.board)

    def set_filter_content(self, include_list, exclude_list):
        self.include_list = include_list
        self.exclude_list = exclude_list
        
    def get_lastpage(self):
        url = "{0}/bbs/{1}/index.html".format(self.base, self.board) 
        res = get(url)
        soup = bs(res.text.encode('utf-8'), "html.parser")
        last_page = str(soup.select('.btn')[3].get('href'))
        m = search('.*index([0-9]*).html', last_page)
        last_num = int(m.group(1))+1
        return last_num

    def crawl_range(self, pgfrom, pgto):
        self.last_pgnum = pgto+2
        for i in xrange(pgfrom, pgto+2):
            print "Page num:%d" %i
            self.crawl(i)

    def crawl(self, index=None):
        if index == None:
            index=''
        url = "{0}/bbs/{1}/index{2}.html".format(self.base, self.board, index)
        try:
            res = get(url)
            res.raise_for_status()
            soup = bs(res.text.encode('utf-8'), "html.parser")
            for title_div in soup.select('.title'):
                if title_div.a:
                    link = self.base+title_div.a['href']
                    title = title_div.a.text.encode('utf-8')
                    content= self.filter_title(title, link)
                    if content and not filter(lambda x: \
                            title in x,self.collect_dict.values()):
                        self.collect_dict.update({self.count:[title,\
                                content[0],link, content[1]]})
                        tmp = self.count % 5
                        self.new_post.update({tmp:[title,\
                            content[0], link, content[1]]})
                        self.count += 1
        except HTTPError:
            print "No New board"
        except ConnectionError:
            print "ConnectionError"
            pass

    def crawl_timing(self):
        while(True):
            new_pgnum= self.get_lastpage()
            if self.last_pgnum < new_pgnum:
                self.crawl_range( self.last_pgnum,new_pgnum)
                print "New page found"
            else:
                print "No new page"
                self.crawl()
            sleep(120)

    def get_content(self, url):
        res = get(url)
        soup = bs(res.text.encode('utf-8'), "html.parser")
        content = soup.select('.bbs-screen')[0].text.encode('utf-8')
        contn_list = [x.strip() for x in str(content).split('\n')]
        ### The unicode is '價格' 
        price_list = findall(u'\u50f9\u683c[^0-9]*([0-9]*,?[0-9]*)',content.decode('utf-8')) 
        if price_list:
            price_list = map(lambda i:int(i.strip('u').encode('utf-8').replace(',','')), price_list)
            check_price = lambda x:True if x >= 4200 and x <= 14000 else False
            if len(price_list)>=2 and check_price(price_list[1]):
                return [price_list[1], contn_list]
            elif check_price(price_list[0]):
                return [price_list[0], contn_list]
            else:
                return None

    def filter_title(self, title, url):
        low_title = title.lower()
        if self.include_list == None:
            print "You need to set filter_list by used Class.set_filter_content"
            return self.get_content(url)

        if filter(lambda x:x in low_title, self.include_list) \
                and not filter(lambda x:x.lower() in low_title, self.exclude_list):
            return self.get_content(url)

    def show_collect(self):
        sort_product = sorted(self.collect_dict.items(), key=lambda x:x[1][1]) 
        for tup in sort_product:
            print "{0: <50}\t\t{1}\t\t{2}".format(tup[1][0], tup[1][1], tup[1][2].decode('utf-8'))
        return sort_product
