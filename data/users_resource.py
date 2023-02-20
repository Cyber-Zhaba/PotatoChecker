from flask_restful import Resource, reqparse, abort
from flask import jsonify, Response
from data import db_session
from data.users import User


class UsersResource(Resource):
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

    def delete(self, user_id: int) -> Response:
        self.abort_if_users_not_found(user_id)
        users = self.session.query(User).get(user_id)
        self.session.delete(users)
        self.session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id: int) -> Response:
        self.abort_if_users_not_found(user_id)
        args = self.parser.parse_args()

        user = self.session.query(User).get(user_id)
        new_favourite = ''
        match args['type']:
            case 'add':
                new_favourite = f"{user.favourite_sites},{args['website']}" if user.favourite_sites else args['website']
            case 'delete':
                new_favourite = ','.join([item for item in filter(lambda x: x, user.favourite_sites.replace(
                    args['website'], '').split(','))])

        setattr(user, 'favourite_sites', new_favourite)

        self.session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def __init__(self) -> None:
        self.parser = reqparse.RequestParser()
        self.session = db_session.create_session()
        self.parser.add_argument('username', required=True)
        self.parser.add_argument('name', required=True)
        self.parser.add_argument('email', required=True)
        self.parser.add_argument('password', required=True)

    def get(self) -> Response:
        users = self.session.query(User).all()
        return jsonify({'users': [
            item.to_dict(rules=("-user", "-user")) for item in users
        ]})

    def post(self) -> Response:
        args = self.parser.parse_args()
        users = User(
            username=args['username'],
            name=args['name'],
            email=args['email'],
            favourite_sites=''
        )
        users.set_password(args['password'])
        self.session.add(users)
        self.session.commit()
        return jsonify({'success': 'OK'})
