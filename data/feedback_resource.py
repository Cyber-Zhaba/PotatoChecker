from flask_restful import Resource, reqparse, abort
from flask import jsonify
from data import db_session
from data.feedbacks import Feedbacks


def abort_feedback_not_found(index: int) -> None:
    """Returns 404 ERROR if id not found"""
    session = db_session.create_session()
    feedbacks = session.query(Feedbacks).get(index)
    if not feedbacks:
        abort(404, messsage="Feedback wasn't found")


class FeedbackResource(Resource):
    def __init__(self) -> None:
        """Create sqldb parser"""
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('owner_id', required=False)
        self.parser.add_argument('time', required=False)
        self.parser.add_argument('content', required=False)
        self.parser.add_argument('feedback_id', required=False)

    @staticmethod
    def get(index: int) -> dict:
        """API method get"""
        abort_feedback_not_found(index)
        session = db_session.create_session()
        feedbacks = session.query(Feedbacks).get(index)
        return jsonify({'sites': feedbacks.to_dict(rules=("-feedback", "-feedback"))})

    @staticmethod
    def delete(feedback_id: int) -> dict:
        """API method delete"""
        abort_feedback_not_found(feedback_id)
        session = db_session.create_session()
        feedbacks = session.query(Feedbacks).get(feedback_id)
        session.delete(feedbacks)
        session.commit()
        return jsonify({'success': 'OK'})


class FeedbackListResource(Resource):
    def __init__(self) -> None:
        """Create sqldb parser"""
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('owner_id', required=False)
        self.parser.add_argument('time', required=False)
        self.parser.add_argument('content', required=False)
        self.parser.add_argument('feedback', required=False)

    def get(self) -> dict:
        """API method get"""
        session = db_session.create_session()
        args = self.parser.parse_args()
        feedbacks = session.query(Feedbacks).filter(Feedbacks.id.in_(args['feedback'].split(','))).all()
        return jsonify({'feedbacks': [
            item.to_dict(rules=("-feedback", "-feedback")) for item in feedbacks]})

    def post(self) -> dict:
        """API method post"""
        args = self.parser.parse_args()
        session = db_session.create_session()
        feedback = Feedbacks(
            content=args['content'],
            owner_id=args['owner_id']
        )
        session.add(feedback)
        session.commit()
        return jsonify({'id': session.query(Feedbacks).all()[-1].id})