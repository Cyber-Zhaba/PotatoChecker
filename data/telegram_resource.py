from flask_restful import Resource, reqparse, abort
from flask import jsonify, Response
from data import db_session
from data.users import User
from requests import get


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
        self.parser.add_argument('login', required=True)
        self.parser.add_argument('password', required=False)

    def get(self) -> Response:
        args = self.parser.parse_args()
        result = jsonify({'failure': 'API Error'})

        user = self.session.query(User).filter(User.username == args['login']).first()

        match args['type']:
            case 'login':
                if user and user.check_password(args['password']):
                    result = jsonify({'success': 'OK'})
                else:
                    result = jsonify({'failure': 'Incorrect login or password'})

            case 'get_favourite_sites':
                websites = get('http://localhost:5000/api/sites',
                               json={
                                   'type': 'all_by_groups',
                                   'favourite_sites': user.favourite_sites
                               }).json()['favourite_sites']

                mess = 'Подключенние не установленно, попробуйте позже'

                result = jsonify({'sites': [
                    (item['name'], item['link'], (
                        self.status(float(item['ping'].split(',')[-1])) if item['ping'] else mess
                    )) for item in websites
                ]})

        return result

    @staticmethod
    def status(ping: float) -> str:
        if 0 <= ping < 40:
            return 'Подключение Отличное'
        if 40 <= ping < 150:
            return 'Подключение Нормальное'
        if 150 <= ping < 350:
            return 'Подключение Плохое'
        if 350 <= ping < 700:
            return 'Подключение Очень плохое'
        if 700 <= ping < 1000:
            return 'Время соединения очень большое. На сервер возможно производиться атака'
        return 'Время ожидания привышенно. Сервер недоступен'

