"""Flask main server file"""
import asyncio
import datetime
from multiprocessing import Pool
from pythonping import ping

from apscheduler.schedulers.background import BackgroundScheduler
from scriptes.availability_checker import ping_website
from scriptes.email import send_email

import matplotlib.pyplot as plt
import logging

from flask import Flask, request
from flask import render_template, redirect
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_restful import Api, abort

from requests import get, post, delete, put
from gevent import monkey
from gevent.pywsgi import WSGIServer

from data import db_session
from data.feedbacks import Feedbacks
from data.users import User
from data.sites import Sites
from data.users_resource import UsersResource, UsersListResource
from data.sites_resource import SitesResource, SitesListResource
from data.feedback_resource import FeedbackResource, FeedbackListResource
from data.telegram_resource import TelegramResource, TelegramListResource
from data.plot_resource import PlotResource

from forms.registration_forms import RegisterForm, LoginForm
from forms.comment_form import CommentForm
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
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    handlers=[logging.FileHandler("logs.log"), logging.StreamHandler(),]
)
N = 0


@app.errorhandler(401)
def log_redirect(error):
    """Handler for 401 and auto redirect to Login page"""
    print(error)
    return redirect('/login')


@app.route('/')
def home_page():
    """Home page"""
    return render_template('Home.html',
                           users_amount=len(get('http://localhost:5000/api/users',
                                                timeout=(2, 20)).json()['users']),
                           sites_amount=len(get('http://localhost:5000/api/sites',
                                                timeout=(2, 20),
                                                json={'type': 'all'}).json()['sites']))


@app.route('/about')
def about_page():
    """Page with info about service"""
    return render_template('About.html')


@app.route('/logout')
@login_required
def logout():
    """Logout url"""
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
                    'password': form.password.data},
                     timeout=(2, 20))
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
            message = "Неправильный логин или пароль"
    return render_template('Login.html', form=form, message=message)


@app.route('/<search>', defaults={'search': None}, methods=['GET', 'POST'])
@app.route('/personal_account/<string:search>', methods=['GET', 'POST'])
@login_required
def personal_account(search):
    """User account page
    :var search: string, name of site to search"""
    form, form_2 = NameWebSiteForm(), CommentForm()
    feedbacks, users = [], {}

    image_name = f'{current_user.name}.png' if search is not None and request != 'POST' else None
    flag_finder = False
    if request.method == "POST":
        if form.validate_on_submit():
            search = form.name.data
            flag_finder = True
        if form_2.validate_on_submit():
            if form_2.content.data != '':
                site = get('http://localhost:5000/api/sites',
                           json={'type': 'strict_name', 'name': search}, timeout=(2, 20)
                           ).json()['sites'][0]
                form.name.data = search
                feedback = post('http://localhost:5000/api/feedback',
                                json={'content': form_2.content.data, 'owner_id': current_user.id}, timeout=(2, 20)).json()['id']
                put(f'http://localhost:5000/api/sites/{site["id"]}',
                    json={'type': 'add_feedback', 'feedback_id': feedback})
                form_2.content.data = ''
    if search is None:
        req = {'type': 'all_by_groups',
               'favourite_sites': current_user.favourite_sites}
    else:
        req = {'type': 'sites_by_name', 'name': search,
               'favourite_sites': current_user.favourite_sites}
    answer = get('http://localhost:5000/api/sites', json=req, timeout=(2, 20)).json()

    favourite_sites_names = answer['favourite_sites']
    not_favourite_sites_names = answer['not_favourite_sites']
    db_sess = db_session.create_session()
    if not flag_finder:
        answer = get('http://localhost:5000/api/sites',
                     json={'type': 'strict_name',
                           'name': search}, timeout=(2, 20)).json()['sites']
        if answer:
            site = answer[0]
            feedback = site['ids_feedbacks']
            # feedback = [feedback for feedback in site['ids_feedbacks'].split(',') if feedback]
            if feedback:
                feedbacks = get('http://localhost:5000/api/feedback',
                                json={'feedback': feedback}, timeout=(2, 20)).json()['feedbacks']
        for i in feedbacks:
            users[i['id']] = get(f'http://localhost:5000/api/users/{i["owner_id"]}', timeout=(
                2, 20)).json()['users']['name']
    return render_template('personal_account_table.html',
                           favourite_sites=favourite_sites_names,
                           not_favourite_sites=not_favourite_sites_names,
                           length=len(favourite_sites_names),
                           image_name=image_name,
                           form=form,
                           form_2=form_2,
                           website_name=search,
                           description="Visit our GayWebsite.com",
                           feedbacks=feedbacks,
                           users=users)


@app.route('/draw_graphic/<int:website_id>', methods=['GET'])
def draw_graphic(website_id):
    """Address to draw graph of stability
    :var website_id: int, id of site to plot"""
    website = get(f'http://localhost:5000/api/plot', json={'id_site': website_id},
               timeout=(2, 20)).json()['plot']
    time = []
    reports = []

    for tm, ping_ in zip(reversed(website['point_time'].split(',')), reversed(website['points'].split(','))):
        delta = datetime.datetime.now() - datetime.datetime.strptime(tm, '%m/%d/%Y/%H/%M')
        if delta <= datetime.timedelta(hours=8):
            time.append(datetime.datetime.strptime(tm, '%m/%d/%Y/%H/%M'))
            reports.append(float(ping_))

    time.reverse()
    reports.reverse()

    print(f'{time=}')

    name = get(f'http://localhost:5000/api/sites/{website_id}').json()['sites']['name']
    plt.plot(time, reports)
    fig, axes = plt.subplots(facecolor='#21024c')
    axes.set_title(name.upper(), color='white', size='20')
    axes.set_facecolor(color='#21024c')
    axes.plot(reports, color='#0f497f')
    axes.tick_params(axis='both', colors='white')
    axes.set_xlabel('Часы', color='white', size='13')
    axes.set_ylabel('Пинг', color='white', size='13')
    axes.spines['left'].set_color('white')
    axes.spines['bottom'].set_color('white')
    axes.spines['right'].set_color('#21024c')
    axes.spines['top'].set_color('#21024c')
    axes.grid(True)
    axes.grid(linestyle='dashdot', linewidth=1, alpha=0.3)
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
                         json={'type': 'post',
                               'owner_id': current_user.id,
                               'name': name,
                               'link': link},
                         timeout=(2, 20))
                    id_ = get('http://localhost:5000/api/sites', json={'type': 'strict_name',
                                                                       'name': name})['sites'][0]['id']
                    post('http://localhost:5000/api/plot', json={'site_id': id_})
                    message = 'Ваш запрос был отправлен на модерацию'
    return render_template('Add_website.html', title=title, form=form, message=message)


@app.route('/moderation')
def moderation():
    # TODO design for moderation page
    """Moderation page(only admin)"""
    if current_user.id != 1:
        abort(403)
    sites = get('http://localhost:5000/api/sites',
                json={'type': 'to_moderation'}, timeout=(2, 20)).json()
    return render_template('moderation.html', sites=sites['sites'])


@app.route('/accept/<int:website_id>', methods=['GET', 'PUT'])
@login_required
def accept_website(website_id):
    """Website accepting(moderation)(admin)
        :var website_id: int, id to accept"""
    if current_user.id != 1:
        abort(403)
    put(f'http://localhost:5000/api/sites/{website_id}',
        json={'type': 'mod', 'moderated': 1},
        timeout=(2, 20))
    return redirect('/moderation')


@app.route('/decline/<int:website_id>', methods=['GET', 'DEL'])
@login_required
def decline_website(website_id):
    """Website declining(moderation)(admin)
        :var website_id: int, id to decline and delete from base"""
    if current_user.id != 1:
        abort(403)
    delete(f'http://localhost:5000/api/sites/{website_id}', timeout=(2, 20))
    return redirect('/moderation')

#
# @app.route('/edit_feedback/<int:feedback_id>', methods=['GET'])
# @login_required
# def edit_comment(feedback_id):
#     form = NameWebSiteForm()


@app.route('/delete_feedback/<int:feedback_id>', methods=['GET', 'DELETE', 'PUT'])
@login_required
def delete_comment(feedback_id):
    req = {'type': 'feedback_in_site',
           'feedback_id': str(feedback_id)}
    site = get('http://localhost:5000/api/sites', json=req).json()
    delete(f'http://localhost:5000/api/feedback/{feedback_id}')
    put('http://localhost:5000/api/sites', json={'feedback_id': str(feedback_id), 'site_name': site["sites"][0]["name"]})
    return redirect(f'/personal_account/{site["sites"][0]["name"]}')


@app.route('/add_to_favourites/<string:website_name>', methods=['GET', 'PUT'])
@login_required
def add_to_favourite(website_name):
    """Adding site to user favourites
        :var website_name: int, id to add in favourite list"""
    website_id = get('http://localhost:5000/api/sites',
                     json={'type': 'strict_name',
                           'name': website_name,
                           'favourite_sites': current_user.favourite_sites},
                     timeout=(2, 20))
    website_id = website_id.json()['sites']
    # TODO check multiply addition
    if website_id:
        website_id = website_id[0]['id']
        put(f'http://localhost:5000/api/users/{current_user.id}',
            json={'type': 'add',
                  'website': website_id},
            timeout=(2, 20)).json()

    return redirect(f'/personal_account/{website_name}')


@app.route('/delete_from_favourites/<string:website_name>', methods=['GET', 'PUT'])
@login_required
def delete_from_favourites(website_name):
    """Deleting site from favourites
        :var website_name: int, id to delete from favourite list"""
    website_id = get('http://localhost:5000/api/sites',
                     json={'type': 'strict_name',
                           'name': website_name,
                           'favourite_sites': current_user.favourite_sites},
                     timeout=(2, 20))
    website_id = website_id.json()['sites']
    if website_id:
        # TODO multiply deletion
        website_id = website_id[0]['id']
        put(f'http://localhost:5000/api/users/{current_user.id}',
            json={'type': 'delete',
                  'website': website_id},
            timeout=(2, 20)).json()

    return redirect(f'/personal_account/{website_name}')


def ping_websites():
    global N
    logging.info(f'N = {N + 1}')

    count, timeout = 1, 1

    logging.debug('made response for ping')
    websites = get('http://localhost:5000/api/sites', json={'type': 'all'}).json()["sites"]
    websites = list(map(lambda x: list(x.values()) + [count, timeout], websites))

    result = [ping_website(item) for item in websites]

    print(f'{result=}')
    logging.debug(str(result))

    for res in result:
        put(f'http://localhost:5000/api/sites/{res[0]}',
            json={'type': 'update_ping', 'ping': res[1], 'check_time': str(datetime.datetime.now())},
            timeout=(2, 20))
    send_email(result)

    if (N := N + 1) % 5 == 0:
        logging.debug('Entered (N := N + 1) % 5 == 0')
        all_ping = get('http://localhost:5000/api/sites', json={'type': 'all_ping_clear'}).json()['sites']
        users_n = len(get('http://localhost:5000/api/users', json={'type': 'all'}).json()['users'])

        print(all_ping)
        print(users_n)

        for site_ping in all_ping:
            id_, ping_, reports = site_ping.values()
            ping_ = list(map(float, [item for item in ping_.split(',') if item]))
            reports = reports.split(',')

            ping_r = sum(ping_) / len(ping_) / 1000
            reports_r = len(reports) / users_n

            point = (ping_r + reports_r) / 2

            if abs(ping_r - reports_r) >= 0.5:
                point = max(ping_r, reports_r)

            put('http://localhost:5000/api/plot',
                json={'id_site': id_, 'points': round(point * 100),
                      'point_time': datetime.datetime.now().strftime('%m/%d/%Y/%H/%M')})


if __name__ == '__main__':
    api.add_resource(UsersListResource, '/api/users')
    api.add_resource(UsersResource, '/api/users/<int:user_id>')
    api.add_resource(SitesListResource, '/api/sites')
    api.add_resource(SitesResource, '/api/sites/<int:site_id>')
    api.add_resource(FeedbackListResource, '/api/feedback')
    api.add_resource(FeedbackResource, '/api/feedback/<int:feedback_id>')
    api.add_resource(TelegramListResource, '/api/telegram')
    api.add_resource(TelegramResource, '/api/telegram/<int:user_id>')

    api.add_resource(PlotResource, '/api/plot')

    db_session.global_init("data/data.db")

    scheduler = BackgroundScheduler()
    scheduler.add_job(ping_websites, 'interval', seconds=90)
    scheduler.start()

    http = WSGIServer(('0.0.0.0', 5000), app.wsgi_app)
    http.serve_forever()
