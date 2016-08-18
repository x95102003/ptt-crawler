from flask import Flask, render_template
from crawl import 
app = Flask(__name__)

@app.route('/')
def show_data():
    return render_template('show.html', collect_data=mydata)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8888')
