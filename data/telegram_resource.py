from flask_restful import Resource, reqparse, abort
from flask import jsonify, Response
from data import db_session
from data.users import User
from data.sites import Sites
from requests import get
from scriptes.utilities import status


class TelegramResource(Resource):
    def __init__(self) -> None:
        self.parser = reqparse.RequestParser()
        self.session = db_session.create_session()
        self.parser.add_argument('name', required=False)
        self.parser.add_argument('email', required=False)
        self.parser.add_argument('type', required=False)
        self.parser.add_argument('website', required=False)

    def abort_if_users_not_found(self, users_id: int) -> None:
        """Returns 404 ERROR if id not found"""
        users = self.session.query(User).get(users_id)
        if not users:
            abort(404, messsage="User wasn't found")

    def get(self, user_id: int) -> Response:
        self.abort_if_users_not_found(user_id)
        users = self.session.query(User).get(user_id)
        return jsonify({'users': users.to_dict(rules=("-user", "-user"))})

    def put(self, user_id: int) -> Response:
        pass


class TelegramListResource(Resource):
    def __init__(self) -> None:
        self.parser = reqparse.RequestParser()
        self.session = db_session.create_session()
        self.parser.add_argument('type', required=True)
        self.parser.add_argument('telegram_id', required=False)
        self.parser.add_argument('notify', required=False)
        self.parser.add_argument('login', required=False)
        self.parser.add_argument('password', required=False)

    def get(self) -> Response:
        args = self.parser.parse_args()
        result = jsonify({'failure': 'API Error'})

        match args['type']:
            case 'login':
                user = self.session.query(User).filter(User.username == args['login']).first()
                if user and user.check_password(args['password']):
                    result = jsonify({'success': 'OK'})
                    setattr(user, 'telegram_id', args['telegram_id'])
                    self.session.commit()
                else:
                    result = jsonify({'failure': 'Incorrect login or password'})

            case 'change_notify':
                user = self.session.query(User).filter(User.telegram_id == args['telegram_id']).first()
                print(int((1, 0)[int(user.notify)]))
                setattr(user, 'notify', int((1, 0)[int(user.notify)]))
                self.session.commit()
                result = jsonify({'success': int(user.notify)})

            case 'check_login':
                user = self.session.query(User).filter(User.telegram_id == args['telegram_id']).first()
                print(user)
                if user is None:
                    result = jsonify({'status': 'not login'})
                else:
                    result = jsonify({'status': 'logged in'})

            case 'get_data_for_notified_users':
                users = self.session.query(User).filter(User.notify == 1).all()
                result = {}
                for user in users:
                    result[user.telegram_id] = {'favourite_sites': [], 'changed_sites': []}
                    websites = get('http://localhost:5000/api/sites', json={
                                       'type': 'all_by_groups',
                                       'favourite_sites': user.favourite_sites
                                   }).json()['favourite_sites']
                    for site in websites:
                        points = get('http://localhost:5000/api/plot', json={
                            'id_site': site['id']}).json()['plot']['points'].split(',')
                        if len(points) >= 2:
                            result[user.telegram_id]['favourite_sites'].append([site['name'], self.condition(points[-1])])
                            if self.condition(points[-1]) != self.condition(points[2]):
                                result[user.telegram_id]['changed_sites'].append([site['name'],
                                                                                  self.condition(points[-1])])
                result = jsonify(result)
            case 'get_favourites':
                user = self.session.query(User).filter(User.telegram_id == args['telegram_id']).first()
                websites = get('http://localhost:5000/api/sites', json={
                    'type': 'all_by_groups',
                    'favourite_sites': user.favourite_sites
                }).json()['favourite_sites']
                result = {'favourite_sites': []}
                for site in websites:
                    points = get('http://localhost:5000/api/plot', json={
                        'id_site': site['id']}).json()['plot']['points'].split(',')
                    if len(points) >= 1:
                        result['favourite_sites'].append([site['name'], self.condition(points[-1])])
                    else:
                        result['favourite_sites'].append([site['name'], 'Устанавливаем подключение'])
                result = jsonify(result)

        return result

    def put(self):
        args = self.parser.parse_args()
        user = self.session.query(User).filter(User.telegram_id == args['telegram_id'])
        setattr(user, 'telegram_id', '')
        self.session.commit()
        return jsonify({'success': 'OK'})

    @staticmethod
    def condition(ping: str) -> str:
        ping = 100 - int(ping)
        if 90 < ping <= 100:
            res = "Отличное"
        elif 75 < ping <= 90:
            res = "Нормальное"
        elif 65 < ping <= 75:
            res = "Медленное"
        elif 50 <= ping <= 65:
            res = "Плохое"
        elif 25 <= ping < 50:
            res = "Возможна кибератака"
        else:
            res = "Сайт упал"
        return res
