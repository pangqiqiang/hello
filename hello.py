#!/usr/bin/env python3
from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask import session
from flask import redirect
from flask import url_for
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_mail import Message
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
import os
from threading import Thread

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# configs
app.config["SECRET_KEY"] = "zVrQqEAEJIUi10A9"
app.config["SQLALCHEMY_DATABASE_URI"] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "78733149@qq.com"
app.config['MAIL_PASSWORD'] = "????????"
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <78733149@qq.com>'
app.config['FLASKY_ADMIN'] = 'pangqiqiang1234@163.com'


bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
mail = Mail(app)


# class for wtforms
class NameForm(Form):
    name = StringField("What is your name?", validators=[Required()])
    submit = SubmitField("Submit")


# sqlalchemy对象模型类
class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username
# 定义邮件函数
#异步邮件
def send_async_email(app, msg):
	with app.app_context():
		mail.send(msg)

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    #msg.html = render_template(template + '.html', **kwargs)
	thr = Thread(target=send_async_email, args=[app, msg])
	thr.start()
	return thr


@app.route("/", methods=["GET", "POST"])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get("name")
        if old_name is not None and old_name != form.name.data:
            flash("Looks like you have changed your name!")
        if app.config['FLASKY_ADMIN']:
            send_email(app.config['FLASKY_ADMIN'], 'New User',
                       'mail/new_user', user=form.name.data)

        session["name"] = form.name.data
        return redirect(url_for("index"))

    return render_template("index.html",
                           current_time=datetime.utcnow(), form=form, name=session.get("name"))


@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(port=5000, debug=True)
