"""Flask main server file"""
import matplotlib.pyplot as plt
from flask import Flask, request
from flask import render_template, redirect
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_restful import Api, abort
from requests import get, post, put, delete
from gevent.pywsgi import WSGIServer
from gevent import monkey
from data import db_session
from data.users import User
from data.sites import Sites
from data.users_resource import UsersResource, UsersListResource
from data.sites_resource import SitesResource, SitesListResource
from data.feedback_resource import FeedbackResource, FeedbackListResource
from data.telegram_resource import TelegramResource, TelegramListResource
from forms.registration_forms import RegisterForm, LoginForm
from forms.add_website_forms import AddWebsiteForm
from forms.util_forms import NameWebSiteForm


monkey.patch_all()
UPLOAD_FOLDER = '/static/img'
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'prev_prof_lovers_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager(app)
login_manager.init_app(app)


@app.errorhandler(401)
def log_redirect(error):
    print(error)
    return redirect('/login')


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
    return render_template('Home.html',
                           users_amount=len(get('http://localhost:5000/api/users').json()['users']),
                           sites_amount=len(get('http://localhost:5000/api/sites',
                                                json={'type': 'all'}).json()['sites']))


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
    """Load user"""
    session = db_session.create_session()
    return session.get(User, user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    message, form = '', RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            session = db_session.create_session()
            if session.query(User).filter(User.username == f'{form.username.data}').first():
                message = "Этот логин уже существует"
            else:
                post('http://localhost:5000/api/users', json={
                    'username': form.username.data,
                    'name': form.name.data,
                    'email': form.email.data,
                    'password': form.password.data
                })
                user = session.query(User).filter(User.username == f'{form.username.data}').first()
                login_user(user, remember=form.remember_me.data)
                return redirect("/account", 301)
    return render_template('Register.html', title='Регистрация', form=form, message=message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    message, form = '', LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            session = db_session.create_session()
            user = session.query(User).filter(User.username == form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/personal_account", 301)
            else:
                message = "Неправильный логин или пароль"
    return render_template('Login.html', form=form, message=message)


@app.route('/<search>', defaults={'search': None}, methods=['GET', 'POST'])
@app.route('/personal_account/<string:search>', methods=['GET', 'POST'])
@login_required
def personal_account(search):
    """User account page
    :var search: string, name of site to search"""
    form = NameWebSiteForm()
    image_name = f'{current_user.name}.png' if search is not None and request != 'POST' else None
    search = form.name.data if request.method == 'POST' else search
    if search is None:
        req = {'type': 'all_by_groups',
               'favourite_sites': current_user.favourite_sites}
    else:
        req = {'type': 'sites_by_name', 'name': search,
               'favourite_sites': current_user.favourite_sites}
    answer = get('http://localhost:5000/api/sites', json=req).json()

    favourite_sites_names = answer['favourite_sites']
    not_favourite_sites_names = answer['not_favourite_sites']

    return render_template('personal_account_table.html',
                           favourite_sites=favourite_sites_names,
                           not_favourite_sites=not_favourite_sites_names,
                           length=len(favourite_sites_names),
                           image_name=image_name,
                           form=form,
                           description="Visit our GayWebsite.com",
                           website_name=search)


@app.route('/draw_graphic/<int:website_id>', methods=['GET'])
def draw_graphic(website_id):
    """Address to draw graph of stability
    :var website_id: int, id of site to plot"""
    time = range(1, 9)
    reports = [0, 0, 1, 3, 0, 5, 4, 5]
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


@app.route('/add_website', methods=['GET', 'POST'])
@login_required
def add_website():
    """Page for adding website"""
    title, message, form = 'Добавление нового сайта', '', AddWebsiteForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            session = db_session.create_session()
            if '.' not in form.link.data:
                message = 'Адресс сайта указан некоректно'
            else:
                name = form.name.data
                form_data = form.link.data.split('.')
                link = form_data[0].split('/')[-1] + '.' + form_data[1].split('/')[0]

                # https://yandex.ru/images/ -> yandex.ru
                if session.query(Sites).filter(
                        (Sites.link == f'{link}') | (Sites.name == f'{name}')).first():
                    message = "Этот сайт уже существует"
                else:
                    post('http://localhost:5000/api/sites',
                         json={
                             'type': 'post',
                             'owner_id': current_user.id,
                             'name': name,
                             'link': link})
                    return 'Ваш запрос был отправлен на модерацию'
                    # TODO https://puzzleweb.ru/css/examples/21-5.php
    return render_template('Add_website.html', title=title, form=form, message=message)


@app.route('/moderation')
def moderation():
    """Moderation page(only admin)"""
    if current_user.id != 1:
        abort(403)
    sites = get('http://localhost:5000/api/sites',
                json={'type': 'to_moderation'}).json()
    return render_template('moderation.html', sites=sites['sites'])


@app.route('/accept/<int:website_id>', methods=['GET', 'PUT'])
@login_required
def accept_website(website_id):
    """Website accepting(moderation)(admin)
        :var website_id: int, id to accept"""
    if current_user.id != 1:
        abort(403)
    put(f'http://localhost:5000/api/sites/{website_id}', json={'moderated': 1})
    return redirect('/moderation')


@app.route('/decline/<int:website_id>', methods=['GET', 'DEL'])
@login_required
def decline_website(website_id):
    """Website declining(moderation)(admin)
        :var website_id: int, id to decline and delete from base"""
    if current_user.id != 1:
        abort(403)
    delete(f'http://localhost:5000/api/sites/{website_id}')
    return redirect('/moderation')


@app.route('/add_to_favourites/<string:website_name>', methods=['GET', 'PUT'])
@login_required
def add_to_favourite(website_name):
    """Adding site to user favourites
        :var website_name: int, id to add in favourite list"""
    website_id = get('http://localhost:5000/api/sites',
                     json={'type': 'sites_by_name',
                           'name': website_name,
                           'favourite_sites': current_user.favourite_sites})
    website_id = website_id.json()['not_favourite_sites']
    if website_id:
        website_id = website_id[0]['id']
        put(f'http://localhost:5000/api/users/{current_user.id}',
            json={
                'type': 'add',
                'website': website_id
            }).json()

    return redirect(f'/personal_account/{website_name}')


@app.route('/delete_from_favourites/<string:website_name>', methods=['GET', 'PUT'])
@login_required
def delete_from_favourites(website_name):
    """Deleting site from favourites
        :var website_name: int, id to delete from favourite list"""
    website_id = get('http://localhost:5000/api/sites',
                     json={'type': 'sites_by_name',
                           'name': website_name,
                           'favourite_sites': current_user.favourite_sites})
    website_id = website_id.json()['favourite_sites']
    if website_id:
        website_id = website_id[0]['id']
        put(f'http://localhost:5000/api/users/{current_user.id}',
            json={
                'type': 'delete',
                'website': website_id
            }).json()

    return redirect(f'/personal_account/{website_name}')


if __name__ == '__main__':
    api.add_resource(UsersListResource, '/api/users')
    api.add_resource(UsersResource, '/api/users/<int:user_id>')
    api.add_resource(SitesListResource, '/api/sites')
    api.add_resource(SitesResource, '/api/sites/<int:site_id>')
    api.add_resource(FeedbackListResource, '/api/feedback')
    api.add_resource(FeedbackResource, '/api/feedback/<int:feedback_id>')
    api.add_resource(TelegramListResource, '/api/telegram')
    api.add_resource(TelegramResource, '/api/telegram/<int:user_id>')
    db_session.global_init("data/data.db")

    http = WSGIServer(('0.0.0.0', 5000), app.wsgi_app)
    http.serve_forever()
