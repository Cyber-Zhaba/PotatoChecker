import os

from flask import make_response
from flask import Flask, request
from flask import render_template, redirect
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_restful import Api
from requests import delete, post, patch, get
from werkzeug.exceptions import Unauthorized
from data import db_session, feedback_resource, sites_resource, users_resource
from data.feedbacks import Feedbacks
from data.sites import Sites
from data.users import User
from scriptes.availability_checker import availability_checker
from templates import html

from forms.registration_forms import RegisterForm, LoginForm

UPLOAD_FOLDER = '/static/img'
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'prev_prof_lovers_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager(app)
login_manager.init_app(app)


def main():
    db_session.global_init("data/data.db")
    # api.add_resource(users_resource.UsersListResource, '/api/v2/users')
    # api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    """load user"""
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        form = RegisterForm()
        return render_template('signup.html', title='signup', form=form)

    elif request.method == 'POST':
        form = RegisterForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.username == form.username.data).first():
                return render_template('signup.html', form=form, message="Этот логин уже существует")
            user = User(
                username=form.username.data,
                name=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            login_user(user, remember=form.remember_me.data)
            return redirect("/", 301)
        return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        form = LoginForm()
        return render_template('signin.html', form=form)

    elif request.method == 'POST':
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.username == form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/", 301)
            return render_template('signin.html', message="Неправильный логин или пароль", form=form)
        return render_template('signin.html', form=form)


@login_required
@app.route('/personal_account', methods=['GET', 'POST'])
def personal_account():
    db_sess = db_session.create_session()
    for site_id in current_user.favourite_sites:
        site = db_sess.query(Sites).filter(Sites.id == site_id).first()

        answer = availability_checker(site.url)

        site.state = answer[0]
        if answer[0] != "Website is working fine":
            pass
            # send_mail(site, answer[0])
    return 0



if __name__ == '__main__':
    main()
