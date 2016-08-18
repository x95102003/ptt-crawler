#!/usr/bin/env python
# -*-coding:utf-8-*-

from requests import get, HTTPError, ConnectionError
from bs4 import BeautifulSoup as bs
from sys import argv
from re import search
from time import sleep
from threading import Thread
from flask import Flask, render_template
app = Flask(__name__)

base = 'https://www.ptt.cc'
last_pgnum = 3500
collect_dict = {}

def get_lastpage():
    url = "{0}/bbs/{1}/index.html".format(base, 'forsale') 
    res = get(url)
    soup = bs(res.text.encode('utf-8'), "html.parser")
    last_page = str(soup.select('.btn')[3].get('href'))
    m = search('.*index([0-9]*).html', last_page)
    last_pgnum = int(m.group(1))+1
    return last_pgnum

def crawl_assign(pgfrom, pgto):
    last_pgnum = pgto+1
    for i in xrange(pgfrom, pgto+1):
        #print "{0} crawl".format(i)
        crawl('forsale', i)

def crawl(board, index=None):
    sample = 3545
    if index == None:
        index=''
    url = "{0}/bbs/{1}/index{2}.html".format(base, board, index)
    try:
        res = get(url)
        res.raise_for_status()
        soup = bs(res.text.encode('utf-8'), "html.parser")
        for line in soup.select('.r-ent'):
            title_div = line.select('.title')[0]
            link = base+title_div.a['href']
            title = title_div.a.text.encode('utf-8')
            price = filter_title(title, link)
            if price and not title in collect_dict:
                collect_dict.update({title:[price,link]})
                #record(title, link, price)
                print title, link, price
    except HTTPError:
        print "No New board"
    except TypeError as e:
        pass
    except ConnectionError:
        pass
#        print "another error"
    #for k,v in collect_dict.items():
       # print k,v

def show_collect():
    sort_product = sorted(collect_dict.items(), key=lambda x:x[1][0]) 
    for tup in sort_product:
        #key, value = tup
        print "{0: <50}\t\t{1}\t\t{2}".format(tup[0], tup[1][0], tup[1][1].decode('utf-8'))
    return sort_product
#    for k, (p, l) in collect_dict.items():
#        print "{0: <50}\t{1}\t{2}".format(k, p, l)

def wait_newPost():
    while(True):
        tmp_pgnum= get_lastpage()
        if last_pgnum < tmp_pgnum:
            crawl_assign(last_pgnum, tmp_pgnum)
            print "New page found"
        else:
            print "No new page"
            crawl('forsale')
        sleep(120)

def get_price(url):
    res = get(url)
    soup = bs(res.text.encode('utf-8'), "html.parser")
    content = soup.select('.bbs-screen')[0].text.encode('utf-8')
    m = search(u'\u50f9\u683c[^0-9]*([0-9]*,?[0-9])',content.decode('utf-8'))
    if m:
        price = int(m.group(1).replace(',',''))
        if price < 14000 and price > 3500:
            return price
        
def filter_title(title, url):
    if 'iphone' in title.lower():
        return get_price(url)

def main():
    th = Thread(target=wait_newPost)
    th.setDaemon(True)
    th.start()
    mth = Thread(target=monitor)
    mth.setDaemon(True)
    mth.start()

def monitor():
    while(True):
        num = raw_input("Input 1 to show collect\n")
        if num == '1':
            show_collect()
        elif num =='0':
            break
        else:
            pass

def record(title, link, price):
    with open("record.txt", 'a+') as f:
        f.write("{0}\t{1}\t{2}\n".format(title, link, price))

@app.route('/')
def show_data():
    return render_template('show.html', collect_data=show_collect())

if __name__ == '__main__':
    main()
    app.debug=True
    app.run(host='0.0.0.0', port=8888)

