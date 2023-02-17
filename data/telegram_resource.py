from flask_restful import Resource, reqparse, abort
from flask import jsonify, Response
from data import db_session
from data.users import User


def abort_if_users_not_found(users_id: int) -> None:
    """Returns 404 ERROR if id not found"""
    session = db_session.create_session()
    users = session.query(User).get(users_id)
    if not users:
        abort(404, messsage="User wasn't found")


class TelegramResource(Resource):
    def __init__(self) -> None:
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', required=False)
        self.parser.add_argument('email', required=False)
        self.parser.add_argument('type', required=False)
        self.parser.add_argument('website', required=False)

    @staticmethod
    def get(user_id: int) -> Response:
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        return jsonify({'users': users.to_dict(rules=("-user", "-user"))})

    def put(self, user_id: int) -> Response:
        pass


class TelegramListResource(Resource):
    def __init__(self) -> None:
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', required=True)
        self.parser.add_argument('password', required=True)

    def get(self) -> Response:
        args = self.parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).filter(User.username == args['username']).first()

        if user and user.check_password(args['password']):
            return jsonify({'success': 'OK'})
        return jsonify({'failure': 'Incorrect login or password'})

    def post(self) -> Response:
        pass
