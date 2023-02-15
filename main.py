import os

import matplotlib as plt
from flask import make_response
from flask import Flask, request
from flask import render_template, redirect
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_restful import Api

from data import db_session
from data.sites import Sites
from data.users import User

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


@app.route('/About.html')
def about():
    return redirect("/about")


@app.route('/Home.html')
def home():
    return redirect("/")


@app.route('/Personal-account.html')
def personal():
    return redirect("/account")


@app.route('/')
def home_page():
    return render_template('Home.html')


@app.route('/about')
def about_page():
    return render_template('About.html')


@app.route('/account')
def account_page():
    return redirect('/personal_account/search=&&%%')


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
        return render_template('Register.html', title='signup', form=form)

    elif request.method == 'POST':
        form = RegisterForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.username == form.username.data).first():
                return render_template('Register.html', form=form, message="Этот логин уже существует")
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
        return render_template('Register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        form = LoginForm()
        return render_template('Login.html', form=form)

    elif request.method == 'POST':
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.username == form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/", 301)
            return render_template('Login.html', message="Неправильный логин или пароль", form=form)
        return render_template('Login.html', form=form)


@login_required
@app.route('/personal_account/<string:search>', methods=['GET'])
def personal_account(search):
    if request.method == 'GET':
        db_sess = db_session.create_session()
        favourite_sites_names = db_sess.query(Sites).filter(
            Sites.link.contains(search), Sites.id.in_(current_user.favourite_sites.split(','))).all()
        not_favourite_sites_names = db_sess.query(Sites).filter(
            Sites.link.contains(search), ~ (Sites.id.in_(current_user.favourite_sites.split(',')))).all()
        return render_template('personal_account_table.html',
                               favourite_sites=favourite_sites_names,
                               not_favourite_sites=not_favourite_sites_names)


@app.route('/draw_graphic/<int:website_id>', methods=['GET'])
def draw_graphic(website_id):
    print(1)
    return redirect('/personal_account')


if __name__ == '__main__':
    main()
