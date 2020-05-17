import extract_features as ef
from flask import Flask, request, render_template
import psycopg2
import credentials as cr
from datetime import date

app = Flask(__name__)

con = psycopg2.connect(host='localhost', database=cr.db_name, user=cr.username, password=cr.password)
cur = con.cursor()
state = 0


@app.route('/')
def run_index():
    global state
    state = 0
    return render_template('index.html')


@app.route('/aboutUs')
def run_aboutUs():
    return render_template('aboutUs.html')


@app.route('/admin')
def run_admin():
    global state
    if state == 1:
        return render_template('admin2.html')
    return render_template('admin.html')


@app.route('/feedback')
def run_feedback():
    return render_template('feedback.html')


@app.route('/contactUs')
def run_contactUs():
    return render_template('contactUs.html')


@app.route('/faq')
def run_faq():
    return render_template('faq\'s.html')


@app.route('/geturl')
def geturl():
    url = request.args.get('url')
    print('URL: ', url)
    query = "select * from phishing_urls where url='" + url + "';"
    cur.execute(query)
    for i in cur.fetchall():
        if i:
            print('Found in DATABASE')
            return 'Phishing URL'
    result = ef.go(url)
    ef.data = []
    if result == 'Phishing URL':
        query = "insert into phishing_urls(url,date) values('" + url + "',DATE '" + str(date.today()) + "');"
        cur.execute(query)
        con.commit()
    return result


@app.route('/admindetails', methods=['POST'])
def admin_deatils():
    id = request.form.get('id')
    password = request.form.get('password')

    query = "select * from admin where id='" + id + "' and password='" + password + "';"
    cur.execute(query)
    for i in cur.fetchall():
        if i:
            global state
            state = 1
            return render_template('admin2.html')
    return render_template('admin.html')


url = input('Enter a url: ')
print('URL: ', url)
ef.go(url)
