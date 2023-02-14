from flask_restful import Resource, reqparse, abort
from flask import jsonify
from . import db_session
from .users import User


def abort_if_users_not_found(users_id: int) -> None:
    """Returns 404 ERROR if id not found"""
    session = db_session.create_session()
    users = session.query(User).get(users_id)
    if not users:
        abort(404, messsage="User wasn't found")


class UsersResource(Resource):
    def __init__(self) -> None:
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('email', required=True)

    @staticmethod
    def get(user_id: int) -> dict:
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        return jsonify({'users': users.to_dict(rules=("-user", "-user"))})

    @staticmethod
    def delete(user_id: int) -> dict:
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        session.delete(users)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def __init__(self) -> None:
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('email', required=True)

    @staticmethod
    def get() -> dict:
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [
            item.to_dict(rules=("-user", "-user")) for item in users
        ]})

    def post(self) -> dict:
        args = self.parser.parse_args()
        session = db_session.create_session()
        users = User(
            name=args['name'],
            address=args['address'],
            email=args['email']
        )
        session.add(users)
        session.commit()
        return jsonify({'success': 'OK'})
