#!/usr/bin/env python
# -*-coding:utf-8-*-

from requests import get, HTTPError, ConnectionError
from bs4 import BeautifulSoup as bs
from sys import argv
from re import search, findall
from time import sleep
from threading import Thread
from flask import Flask, render_template
app = Flask(__name__,static_url_path='/static')

ms_th = None
for_th = None

class PTT_CRAWL(Thread):
   
    def __init__(self, board, last_index):
        super(PTT_CRAWL, self).__init__()
        self.base = 'https://www.ptt.cc'
        self.board = board
        self.last_pgnum = last_index
        self.collect_dict = {}

    def run(self):
        print "Start Crawl the board %s\n" %self.board
        self.wait_newPost() 

    def __str__(self):
        print self.board, self.last_pgnum, self.collect_dict
        print self.collect_dict
        return '{0}'.format(self.board)

    def get_lastpage(self):
        url = "{0}/bbs/{1}/index.html".format(self.base, self.board) 
        res = get(url)
        soup = bs(res.text.encode('utf-8'), "html.parser")
        last_page = str(soup.select('.btn')[3].get('href'))
        m = search('.*index([0-9]*).html', last_page)
        last_num = int(m.group(1))+1
        return last_num
        
    def crawl_assign(self, pgfrom, pgto):
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
                    if content and not title in self.collect_dict:
                        self.collect_dict.update({title:[content[0],link, content[1]]})
                    #record(title, link, price)
        except HTTPError:
            print "No New board"
        except ConnectionError:
            pass

    def show_collect(self):
        sort_product = sorted(self.collect_dict.items(), key=lambda x:x[1][0]) 
        for tup in sort_product:
            print "{0: <50}\t\t{1}\t\t{2}".format(tup[0], tup[1][0], tup[1][1].decode('utf-8'))
        return sort_product

    def wait_newPost(self):
        while(True):
            tmp_pgnum= self.get_lastpage()
            print tmp_pgnum, self.last_pgnum
            if self.last_pgnum < tmp_pgnum:
                self.crawl_assign( self.last_pgnum,tmp_pgnum)
                print "New page found"
            else:
                print "No new page"
                self.crawl()
            sleep(120)
           # print self.collect_dict

    def get_price(self, url):
        res = get(url)
        soup = bs(res.text.encode('utf-8'), "html.parser")
        content = soup.select('.bbs-screen')[0].text.encode('utf-8')
        cont = str(content)
        tot_con = [x.strip() for x in cont.split('\n')]
        price_list = findall(u'\u50f9\u683c[^0-9]*([0-9]*,?[0-9]*)',content.decode('utf-8')) 
        if price_list:
            price_list = map(lambda i:int(i.strip('u').encode('utf-8').replace(',','')), price_list)
            check_price = lambda x:True if x >= 4200 and x <= 14000 else False
            if len(price_list)>=2 and check_price(price_list[1]):
                return [price_list[1], tot_con]
            elif check_price(price_list[0]):
                return [price_list[0], tot_con]
            else:
                return None
    def filter_title(self, title, url):
        #print title
        if 'iphone' in title.lower() and '徵' not in title \
            and '售' not in title:
            return self.get_price(url)

def main():
    global for_th
    global ms_th
    for_th = PTT_CRAWL('forsale', 3500)
    for_th.setDaemon(True)
    for_th.start()
    ms_th = PTT_CRAWL('mobilesales', 11320)
    ms_th.setDaemon(True)
    #ms_th.get_price('https://www.ptt.cc/bbs/mobilesales/M.1472127453.A.164.html')
    ms_th.start()
    mth = Thread(target=monitor)
    mth.setDaemon(True)
    mth.start()

def monitor():
    while(True):
        num = raw_input("Input 1 to show collect\n")
        if num == '1':
            ms_th.show_collect()
            #print ms_th
        elif num =='2':
            for_th.show_collect()
        else:
            pass

def record(title, link, price):
    with open("record.txt", 'a+') as f:
        f.write("{0}\t{1}\t{2}\n".format(title, link, price))

@app.route('/')
def show_data():
    return render_template('result.html', mobiles=ms_th.show_collect(), forsales=for_th.show_collect())


if __name__ == '__main__':
    main()
    app.debug=True
    app.run(host='0.0.0.0', port=8888)

