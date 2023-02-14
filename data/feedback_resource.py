from flask_restful import Resource, reqparse, abort
from flask import jsonify
import db_session
from feedbacks import Feedbacks


def abort_feedback_not_found(index: int) -> None:
    """Returns 404 ERROR if id not found"""
    session = db_session.create_session()
    feedbacks = session.query(Feedbacks).get(index)
    if not feedbacks:
        abort(404, messsage="Feedback wasn't found")


class SitesResource(Resource):
    def __init__(self) -> None:
        """Create sqldb parser"""
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('owner_id', required=True)
        self.parser.add_argument('time', required=True)
        self.parser.add_argument('content', required=True)

    @staticmethod
    def get(index: int) -> dict:
        """API method get"""
        abort_feedback_not_found(index)
        session = db_session.create_session()
        feedbacks = session.query(Feedbacks).get(index)
        return jsonify({'sites': feedbacks.to_dict(rules=("-feedback", "-feedback"))})

    @staticmethod
    def delete(index: int) -> dict:
        """API method delete"""
        abort_feedback_not_found(index)
        session = db_session.create_session()
        feedbacks = session.query(Feedbacks).get(index)
        session.delete(feedbacks)
        session.commit()
        return jsonify({'success': 'OK'})


class ListSites(Resource):
    def __init__(self) -> None:
        """Create sqldb parser"""
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('owner_id', required=True)
        self.parser.add_argument('time', required=True)
        self.parser.add_argument('content', required=True)

    @staticmethod
    def get() -> dict:
        """API method get"""
        session = db_session.create_session()
        feedbacks = session.query(Feedbacks).all()
        return jsonify({'feedbacks': [
            item.to_dict(rules=("-feedback", "-feedback")) for item in feedbacks
        ]})

    def post(self) -> dict:
        """API method post"""
        args = self.parser.parse_args()
        session = db_session.create_session()
        feedbacks = Feedbacks(
            owner_id=args['owner_id'],
            time=args['time'],
            content=args['content'],
        )
        session.add(feedbacks)
        session.commit()
        return jsonify({'success': 'OK'})

