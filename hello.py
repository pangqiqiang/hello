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
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

app = Flask(__name__)
app.config["SECRET_KEY"] = "zVrQqEAEJIUi10A9"
bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(Form):
    name = StringField("What is your name?", validators=[Required()])
    submit = SubmitField("Submit")

@app.route("/", methods=["GET", "POST"])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get("name")
        if old_name is not None and old_name != form.name.data:
            flash("Looks like you have changed your name!")
        session["name"] = form.name.data
        return redirect(url_for("index")) 

    return render_template("index.html",
    current_time=datetime.utcnow(), form=form, name=session.get("name"))

@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

if __name__ == "__main__":
    app.run(port=5000, debug=True)