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


class UsersResource(Resource):
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

    @staticmethod
    def delete(user_id: int) -> Response:
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        session.delete(users)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id: int) -> Response:
        abort_if_users_not_found(user_id)
        args = self.parser.parse_args()
        session = db_session.create_session()

        user = session.query(User).get(user_id)
        new_favourite = ''
        match args['type']:
            case 'add':
                new_favourite = f"{user.favourite_sites},{args['website']}" if user.favourite_sites else args['website']
            case 'delete':
                new_favourite = ','.join([item for item in filter(lambda x: x, user.favourite_sites.replace(
                    args['website'], '').split(','))])

        setattr(user, 'favourite_sites', new_favourite)

        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def __init__(self) -> None:
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', required=True)
        self.parser.add_argument('name', required=True)
        self.parser.add_argument('email', required=True)
        self.parser.add_argument('password', required=True)

    @staticmethod
    def get() -> Response:
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [
            item.to_dict(rules=("-user", "-user")) for item in users
        ]})

    def post(self) -> Response:
        args = self.parser.parse_args()
        session = db_session.create_session()
        users = User(
            username=args['username'],
            name=args['name'],
            email=args['email'],
            favourite_sites=''
        )
        users.set_password(args['password'])
        session.add(users)
        session.commit()
        return jsonify({'success': 'OK'})
