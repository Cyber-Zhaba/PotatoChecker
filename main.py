import os

import matplotlib.pyplot as plt
from flask import make_response
from flask import Flask, request
from flask import render_template, redirect
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_restful import Api
from data.users_resource import UsersResource,UsersListResource
from data.sites_resource import SitesResource, SitesListResource
from data.feedback_resource import FeedbackResource, FeedbackListResource
from requests import get, post, delete
from forms.registration_forms import RegisterForm, LoginForm
from forms.util_forms import NameWebSiteForm

import PIL

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
    api = Api(app)

    api.add_resource(UsersListResource, '/api/users')
    api.add_resource(UsersResource, '/api/users/<int:user_id>')
    api.add_resource(SitesListResource, '/api/sites')
    api.add_resource(SitesResource, '/api/sites/<int:site_id>')
    api.add_resource(FeedbackListResource, '/api/feedback')
    api.add_resource(FeedbackResource, '/api/feedback/<int:feedback_id>')
    db_session.global_init("data/data.db")

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
    return redirect('/personal_account')


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
            session = db_session.create_session()
            if session.query(User).filter(User.username == form.username.data).first():
                return render_template('Register.html', form=form, message="Этот логин уже существует")
            post('http://localhost:5000/api/users', json={
                'username': form.username.data,
                'name': form.name.data,
                'email': form.email.data,
                'password': form.password.data
            })
            user = session.query(User).filter(User.username == form.username.data).first()
            login_user(user, remember=form.remember_me.data)
            return redirect("/", 301)
        return render_template('Register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('Login.html', form=form)

    elif request.method == 'POST':
        form = LoginForm()
        if form.validate_on_submit():
            session = db_session.create_session()
            user = session.query(User).filter(User.username == form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/personal_account", 301)
            return render_template('Login.html', message="Неправильный логин или пароль", form=form)
        return render_template('Login.html', form=form)


@login_required
@app.route('/<search>', defaults={'search': None})
@app.route('/personal_account/<string:search>', methods=['GET', 'POST'])
def personal_account(search):
    form = NameWebSiteForm()
    image_name = None
    if request.method == 'POST':
        search = form.name.data
    else:
        image_name = f'{current_user.name}.png'

    try:
        if search is None:
            favourite_sites_names = get('http://localhost:5000/api/sites',
                                        json={
                                            'type': 'favourite_sites',
                                            'favourite_sites': current_user.favourite_sites
                                        }).json()
            not_favourite_sites_names = get('http://localhost:5000/api/sites',
                                            json={
                                                'type': 'not_favourite_sites',
                                                'favourite_sites': current_user.favourite_sites
                                            }).json()
        else:
            favourite_sites_names = get('http://localhost:5000/api/sites',
                                        json={
                                            'type': 'favourite_sites_and_name',
                                            'favourite_sites': current_user.favourite_sites,
                                            'name': search
                                        }).json()
            not_favourite_sites_names = get('http://localhost:5000/api/sites',
                                            json={
                                                'type': 'not_favourite_sites_and_name',
                                                'favourite_sites': current_user.favourite_sites,
                                                'name': search
                                            }).json()

        return render_template('personal_account_table.html',
                               favourite_sites=favourite_sites_names['sites'],
                               not_favourite_sites=not_favourite_sites_names['sites'],
                               length=len(favourite_sites_names['sites']),
                               image_name=image_name,
                               form=form)
    except Exception as error:
        if 'split' in error.__str__():
            image_name = None
            if request.method == 'POST':
                search = form.name.data
            else:
                image_name = f'{current_user.name}.png'

            if search is None:
                not_favourite_sites_names = get('http://localhost:5000/api/sites',
                                                json={
                                                    'type': 'all'
                                                })
            else:
                not_favourite_sites_names = get('http://localhost:5000/api/sites',
                                                json={
                                                    'name': search
                                                })
                image_name = f'{current_user.name}.png'
            return render_template('personal_account_table.html',
                                   favourite_sites=[],
                                   not_favourite_sites=not_favourite_sites_names,
                                   length=0,
                                   image_name=image_name)
        else:
            return redirect('/login')


@app.route('/draw_graphic/<int:website_id>', methods=['GET'])
def draw_graphic(website_id):
    time = range(1, 9)
    reports = [0, 0, 1, 3, 0, 5, 4, 5]
    db_sess = db_session.create_session()
    name = get(f'http://localhost:5000/api/sites/{website_id}').json()['sites']['name']
    plt.plot(time, reports)
    fig, ax = plt.subplots(facecolor='#21024c')
    ax.set_title(name.upper(), color='white', size='20')
    ax.set_facecolor(color='#21024c')
    ax.plot(reports, color='#0f497f')
    ax.tick_params(axis='both', colors='white')
    ax.set_xlabel('Часы', color='white', size='13')
    ax.set_ylabel('Количество жалоб', color='white', size='13')
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.spines['right'].set_color('#21024c')
    ax.spines['top'].set_color('#21024c')
    ax.grid(True)
    ax.grid(linestyle='dashdot', linewidth=1, alpha=0.3)
    fig.savefig(f'static/img/{current_user.name}.png', dpi=200)
    return redirect(f'/personal_account/{name}')


if __name__ == '__main__':
    main()
