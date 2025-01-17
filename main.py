import extract_features as ef
from flask import Flask, request, render_template, redirect, url_for, session, flash
import psycopg2
import credentials as cr
from datetime import date, timedelta
from flask_mail import *

app = Flask(__name__)
app.secret_key = cr.secret_key
app.permanent_session_lifetime = timedelta(hours=cr.time)
app.config['MAIL_SERVER'] = cr.mail_server
app.config['MAIL_PORT'] = cr.mail_port
app.config['MAIL_USERNAME'] = cr.mail_username
app.config['MAIL_PASSWORD'] = cr.mail_password
app.config['MAIL_USE_TLS'] = cr.mail_use_tls
app.config['MAIL_USE_SSL'] = cr.mail_use_ssl

con = psycopg2.connect(host=cr.host, database=cr.db_name, user=cr.username, password=cr.password)
cur = con.cursor()
mail = Mail(app)


@app.route('/')
def run_index():
    return render_template('index.html')


@app.route('/aboutUs')
def run_aboutUs():
    return render_template('aboutUs.html')


@app.route('/admin', methods=['POST', 'GET'])
def run_admin():
    if request.method == 'POST':
        id = request.form.get('id')
        password = request.form.get('password')
        query = "select * from admin where id='" + id + "' and password='" + password + "';"
        cur.execute(query)
        result = cur.fetchall()
        if result:
            session.permanent = True
            session['id'] = id
            return redirect(url_for('login'))
        else:
            return render_template('admin.html')
    else:
        if 'id' in session:
            return redirect(url_for('login'))
        return render_template('admin.html')


@app.route('/contactUs', methods=['GET', 'POST'])
def run_contactUs():
    if request.method == 'GET':
        return render_template('contactUs.html')
    else:
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        company = request.form.get('company')
        message = request.form.get('message')
        msg = Message('CONTACT US', sender=cr.mail_username, recipients=[cr.mail_username])
        msg.body = f'Hey I am {name}.\n\n{message}\n\nFrom {company}\n{phone}\n{email}'
        mail.send(msg)
        flash(f'Congratulations {name}!! Mail Sent.')
        return redirect(url_for('run_contactUs'))


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
            flash('PHISHING URL')
            return redirect(url_for('run_index'))
    result = ef.go(url)
    ef.data = []
    if result == 'PHISHING URL':
        query = "insert into phishing_urls(url,date) values('" + url + "',DATE '" + str(date.today()) + "');"
        cur.execute(query)
        con.commit()
    flash(result)
    return redirect(url_for('run_index'))


@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('run_admin'))


@app.route('/login')
def login():
    if 'id' in session:
        return redirect(url_for('viewlist'))
    return redirect(url_for('run_admin'))


@app.route('/viewlist')
def viewlist():
    query = "select * from phishing_urls;"
    cur.execute(query)
    blacklist = cur.fetchall()
    return render_template('viewlist.html', blacklist=blacklist)


@app.route('/feedback', methods=['POST', 'GET'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('fname')
        email = request.form.get('email')
        comments = request.form.get('comments')
        query = f"select email from Feedback where email='{email}';"
        cur.execute(query)
        for i in cur.fetchall():
            if i:
                flash(f'Sorry {name}! You have already given your valuable feedback to us.')
                return redirect(url_for('feedback'))
        query = f"insert into Feedback(Name,Email,Comments) values('{name}','{email}','{comments}');"
        cur.execute(query)
        con.commit()
        flash(f'Thank You {name}. Your Feedback is Submitted')
        return redirect(url_for('feedback'))
    else:
        return render_template('feedback.html')


@app.route('/viewusers')
def viewusers():
    query = "select * from feedback;"
    cur.execute(query)
    users = cur.fetchall()
    return render_template('viewusers.html', users=users)


@app.route('/add', methods=['GET', 'POST'])
def add_to_blacklist():
    if request.method == 'GET':
        return render_template('add_to_blacklist.html')
    else:
        url = request.form.get('url')
        query = "select * from phishing_urls where url='" + url + "';"
        cur.execute(query)
        for i in cur.fetchall():
            if i:
                flash('Entered URL is already been blacklisted')
                return redirect(url_for('add_to_blacklist'))
        query = "insert into phishing_urls(url,date) values('" + url + "',DATE '" + str(date.today()) + "');"
        cur.execute(query)
        con.commit()
        flash('Entered URL is added to blacklist successfully')
        return redirect(url_for('add_to_blacklist'))


@app.route('/feedbacks')
def feedbacks():
    query = "select * from feedback;"
    cur.execute(query)
    feedbacks = cur.fetchall()
    return render_template('viewfeedback.html', feedbacks=feedbacks)


@app.route('/remove', methods=['GET', 'POST'])
def remove_from_blacklist():
    if request.method == 'GET':
        return render_template('remove_from_blacklist.html')
    else:
        url = request.form.get('url')
        query = "select * from phishing_urls where url='" + url + "';"
        cur.execute(query)
        for i in cur.fetchall():
            if i:
                query = "delete from phishing_urls where url='" + url + "';"
                cur.execute(query)
                flash('Entered URL has been removed from the blacklist')
                return redirect(url_for('remove_from_blacklist'))
        flash('FAIL..entered URL is not present in the blacklist')
        return redirect(url_for('remove_from_blacklist'))
