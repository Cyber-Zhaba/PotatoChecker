"""Flask main server file"""
import configparser
import datetime
import logging
from os import getcwd

import matplotlib.dates as dates
import matplotlib.pyplot as plt
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, url_for
from flask import render_template, redirect
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_restful import Api, abort
from gevent import monkey
from gevent.pywsgi import WSGIServer
from requests import get, post, delete, put

from data.__init__ import *
from scripts.__init__ import *
from forms.add_website_forms import AddWebsiteForm
from forms.comment_form import CommentForm
from forms.registration_forms import RegisterForm, LoginForm
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
    handlers=[logging.FileHandler("logs.log"),
              logging.StreamHandler()])
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
    result = session.get(User, user_id)
    session.close()
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
            session.close()
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
            session.close()
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
    submit_comment_btn = 'Добавить отзыв'
    comment_title = 'Добавьте отзыв:'

    if 'messages' in request.args:
        submit_comment_btn = 'Редактировать отзыв'
        comment_title = 'Редактируйте отзыв:'

    if request.method == "GET":
        if 'messages' in request.args:
            form_2.content.data = request.args['messages']

    if request.method == "POST":
        if form.validate_on_submit():
            search = form.name.data.lower()
            flag_finder = True
        if form_2.validate_on_submit():
            if form_2.content.data != '':
                site = get('http://localhost:5000/api/sites',
                           json={'type': 'strict_name', 'name': search}, timeout=(2, 20)
                           ).json()['sites'][0]
                form.name.data = search
                feedback = post('http://localhost:5000/api/feedback',
                                json={'content': form_2.content.data, 'owner_id': current_user.id},
                                timeout=(2, 20)).json()['id']
                put(f'http://localhost:5000/api/sites/{site["id"]}',
                    json={'type': 'add_feedback', 'feedback_id': feedback})
                form_2.content.data = ''
                submit_comment_btn = 'Добавить отзыв'
                comment_title = 'Добавьте отзыв:'
    if search is None:
        req = {'type': 'all_by_groups',
               'favourite_sites': current_user.favourite_sites}
    else:
        req = {'type': 'sites_by_name', 'name': search,
               'favourite_sites': current_user.favourite_sites}
    answer = get('http://localhost:5000/api/sites', json=req, timeout=(2, 20)).json()
    favourite_sites_names = answer['favourite_sites']
    not_favourite_sites_names = answer['not_favourite_sites']
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
                           feedbacks=feedbacks,
                           users=users,
                           submit_comment_btn=submit_comment_btn,
                           comment_title=comment_title,
                           flag_finder=flag_finder)


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
            reports.append(100 - int(ping_))
        else:
            break

    time.reverse()
    reports.reverse()

    logging.info(f'{time=}')

    name = get(f'http://localhost:5000/api/sites/{website_id}').json()['sites']['name']
    fig, axes = plt.subplots()

    axes.set_title(name.upper(), color='white', size='20')

    axes.tick_params(axis='both', colors='white')

    axes.set_xlabel('Часы', color='white', size='13')
    axes.set_ylabel('Эффективность', color='white', size='13')

    axes.spines['left'].set_color('white')
    axes.spines['bottom'].set_color('white')
    axes.spines['right'].set_color('#21024c')
    axes.spines['top'].set_color('#21024c')

    axes.grid(True)
    axes.grid(linestyle='dashdot', linewidth=1, alpha=0.3)

    axes.xaxis.set_major_formatter(dates.DateFormatter('%m.%d %H:%M'))

    axes.plot(time, reports, color='#0f497f')

    # plt.ylim([0, 100])

    plt.gcf().autofmt_xdate()
    png_path = ('WebApp' if getcwd().split('\\')[-1] != 'WebApp' else '') + f'/static/img/{current_user.name}.png'
    fig.savefig(png_path, dpi=200, transparent=True)
    return redirect(f'/personal_account/{name}')


@app.route('/report/<string:website_name>')
@login_required
def report(website_name):
    put('http://localhost:5000/api/sites',
        json={
            'type': 'report',
            'name': website_name,
            'id': current_user.id
        })
    return redirect(f'/personal_account/{website_name}')


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
                    id_ = get('http://localhost:5000/api/sites',
                              json={'type': 'strict_name',
                                    'name': name}).json()['sites'][0]['id']
                    post('http://localhost:5000/api/plot', json={'site_id': id_})
                    message = 'Ваш запрос был отправлен на модерацию'
            session.close()
    return render_template('Add_website.html', title=title, form=form, message=message)


@app.route('/moderation')
def moderation():
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


@app.route('/edit_feedback/<int:feedback_id>', methods=['GET'])
@login_required
def edit_comment(feedback_id):
    req = {'type': 'feedback_in_site',
           'feedback_id': str(feedback_id)}
    site = get('http://localhost:5000/api/sites', json=req).json()
    feedback = get(f'http://localhost:5000/api/feedback/{feedback_id}').json()
    messages = feedback['sites']['content']
    name = site["sites"][0]["name"]
    put('http://localhost:5000/api/sites',
        json={'type': '',
              'feedback_id': feedback_id,
              'name': name,
              'type': 'try_hard'})
    delete(f'http://localhost:5000/api/feedback/{feedback_id}')
    return redirect(url_for(f'personal_account', search=site["sites"][0]["name"], messages=messages))


@app.route('/delete_feedback/<int:feedback_id>', methods=['GET', 'DELETE', 'PUT'])
@login_required
def delete_comment(feedback_id):
    req = {'type': 'feedback_in_site',
           'feedback_id': str(feedback_id)}
    site = get('http://localhost:5000/api/sites', json=req).json()
    name = site["sites"][0]["name"]
    put('http://localhost:5000/api/sites',
        json={'type': '',
              'feedback_id': feedback_id,
              'name': name})
    delete(f'http://localhost:5000/api/feedback/{feedback_id}')
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
        website_id = website_id[0]['id']
        put(f'http://localhost:5000/api/users/{current_user.id}',
            json={'type': 'delete',
                  'website': website_id},
            timeout=(2, 20)).json()

    return redirect(f'/personal_account/{website_name}')


def ping_websites():
    global N
    logging.info(f'N = {N + 1}')

    count, timeout = 1, 0.5

    logging.debug('made response for ping')
    websites = get('http://localhost:5000/api/sites', json={'type': 'all'}, timeout=(2, 20)).json()["sites"]
    websites = list(map(lambda x: list(x.values()) + [count, timeout], websites))

    result = [ping_website(item) for item in websites]

    print(f'{result=}')
    logging.debug(str(result))

    for res in result:
        put(f'http://localhost:5000/api/sites/{res[0]}',
            json={'type': 'update_ping', 'ping': res[1], 'state': status(res[1])},
            timeout=(2, 20))
    send_email(result)

    if (N := N + 1) % 5 == 0:
        logging.debug('Entered (N := N + 1) % 5 == 0')
        all_ping = get('http://localhost:5000/api/sites', json={'type': 'all_ping_clear'}).json()['sites']
        users_n = len(get('http://localhost:5000/api/users', json={'type': 'all'}).json()['users'])

        for site_ping in all_ping:
            id_, ping_, reports, state = site_ping.values()
            ping_ = list(map(float, [item for item in ping_.split(',') if item]))
            reports_r = 0
            if reports and reports is not None:
                reports = reports.split(',')
                reports_r = len(reports) / users_n

            ping_r = sum(ping_) / len(ping_) / 500
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

    if sys.platform.startswith('win'):
        db_path = ('WebApp' if getcwd().split('\\')[-1] != 'WebApp' else '') + r'\data\data.db'
    else:
        db_path = ('WebApp' if getcwd().split(r'/')[-1] != 'WebApp' else '') + r'/data/data.db'

    db_session.global_init(db_path)

    scheduler = BackgroundScheduler()
    scheduler.add_job(ping_websites, 'interval', seconds=90)
    scheduler.start()

    config = configparser.ConfigParser()
    cfg_path = ('../' if getcwd().split('\\')[-1] == 'WebApp' else '') + 'config.cfg'
    config.read(cfg_path)

    if config['FlaskWebApp']['first_setup'] == '1':
        config.set('FlaskWebApp', 'first_setup', '0')
        with open(cfg_path, 'w') as file:
            config.write(file)

        session = db_session.create_session()

        user = User()
        user.name, user.username = 'Admin', config['FlaskWebApp']['admin_login']
        user.email = config['FlaskWebApp']['admin_email']
        user.set_password(config['FlaskWebApp']['admin_password'])

        current_time = datetime.datetime.now().strftime('%m/%d/%Y/%H/%M')

        sites_1 = Sites(
            owner_id=1,
            name='МГУ',
            link='msu.ru',
            ids_feedbacks='',
            ping=f'{ping_website((1, "msu.ru", 0, 0, 1, 0.5))}',
            moderated=1
        )

        point_1 = Plot(
            id_site=1,
            points='11',
            point_time=current_time
        )

        sites_2 = Sites(
            owner_id=1,
            name='МФТИ',
            link='mipt.ru',
            ids_feedbacks='',
            ping=f'{ping_website((2, "mipt.ru", 0, 0, 1, 0.5))}',
            moderated=1
        )

        point_2 = Plot(
            id_site=2,
            points='11',
            point_time=current_time
        )

        sites_3 = Sites(
            owner_id=1,
            name='МФЮА',
            link='mfua.ru',
            ids_feedbacks='',
            ping=f'{ping_website((3, "mfua.ru", 0, 0, 1, 0.5))}',
            moderated=1
        )

        point_3 = Plot(
            id_site=3,
            points='61',
            point_time=current_time
        )

        sites_4 = Sites(
            owner_id=1,
            name='МЭИ',
            link='mpei.ru',
            ids_feedbacks='',
            ping=f'{ping_website((4, "mpei.ru", 0, 0, 1, 0.5))}',
            moderated=1
        )

        point_4 = Plot(
            id_site=4,
            points='11',
            point_time=current_time
        )

        sites_5 = Sites(
            owner_id=1,
            name='ВШЭ',
            link='hse.ru',
            ids_feedbacks='',
            ping=f'{ping_website((5, "hse.ru", 0, 0, 1, 0.5))}',
            moderated=1
        )

        point_5 = Plot(
            id_site=5,
            points='11',
            point_time=current_time
        )

        sites_6 = Sites(
            owner_id=1,
            name='МИСИС',
            link='misis.ru',
            ids_feedbacks='',
            ping=f'{ping_website((6, "misis.ru", 0, 0, 1, 0.5))}',
            moderated=1
        )

        point_6 = Plot(
            id_site=6,
            points='21',
            point_time=current_time
        )

        sites_7 = Sites(
            owner_id=1,
            name='МГТУ им. Н. Э. Баумана',
            link='bmstu.ru',
            ids_feedbacks='',
            ping=f'{ping_website((7, "bmstu.ru", 0, 0, 1, 0.5))}',
            moderated=1
        )

        point_7 = Plot(
            id_site=7,
            points='11',
            point_time=current_time
        )

        session.add(user)
        session.add(sites_1)
        session.add(point_1)
        session.add(sites_2)
        session.add(point_2)
        session.add(sites_3)
        session.add(point_3)
        session.add(sites_4)
        session.add(point_4)
        session.add(sites_5)
        session.add(point_5)
        session.add(sites_6)
        session.add(point_6)
        session.add(sites_7)
        session.add(point_7)

        session.commit()

    http = WSGIServer((config['FlaskWebApp']['serverIP'], int(config['FlaskWebApp']['serverPORT'])), app.wsgi_app)
    http.serve_forever()
