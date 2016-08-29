#!/usr/bin/env python
# -*- coding:utf-8 -*-

from threading import Thread
from flask import Flask, render_template
from crawl import PTT_CRAWL
app = Flask(__name__, static_url_path='/static')

ms_th = None
for_th = None

def monitor():
    while(True):
        num = raw_input('Input 1 and 2 to show collection')
        if num == '1':
            ms_th.show_collect()
        elif num =='2':
            for_th.show_collect()
        else:
            pass

def main():
    global for_th
    global ms_th
    for_th = PTT_CRAWL('forsale', 3426)
    for_th.set_filter_content(['iphone'], ['徵','售'])
    for_th.setDaemon(True)
    for_th.start()
    ms_th = PTT_CRAWL('mobilesales', 11350)
    ms_th.set_filter_content(['iphone'], ['徵','售'])
    ms_th.setDaemon(True)
    ms_th.start()
    mth = Thread(target=monitor)
    mth.setDaemon(True)
    mth.start()

@app.route('/')
def show_data():
    return render_template('result.html', mobiles=ms_th.show_collect(), forsales=for_th.show_collect(), top_list=ms_th.new_post )

if __name__ == '__main__':
    main()
    app.debug=True
    app.run(host='0.0.0.0', port=8888)

