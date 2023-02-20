from flask_restful import Resource, reqparse, abort
from flask import jsonify
from data import db_session
from data.feedbacks import Feedbacks


class FeedbackResource(Resource):
    def __init__(self) -> None:
        """Create sqldb parser"""
        self.parser = reqparse.RequestParser()
        self.session = db_session.create_session()
        self.parser.add_argument('owner_id', required=False)
        self.parser.add_argument('time', required=False)
        self.parser.add_argument('content', required=False)
        self.parser.add_argument('feedback_id', required=False)

    def abort_feedback_not_found(self, index: int) -> None:
        """Returns 404 ERROR if id not found"""
        feedbacks = self.session.query(Feedbacks).get(index)
        if not feedbacks:
            abort(404, messsage="Feedback wasn't found")

    def get(self, feedback_id: int) -> dict:
        """API method get"""
        self.abort_feedback_not_found(feedback_id)
        feedbacks = self.session.query(Feedbacks).get(feedback_id)
        return jsonify({'sites': feedbacks.to_dict(rules=("-feedback", "-feedback"))})

    def delete(self, feedback_id: int) -> dict:
        """API method delete"""
        self.abort_feedback_not_found(feedback_id)
        feedbacks = self.session.query(Feedbacks).get(feedback_id)
        self.session.delete(feedbacks)
        self.session.commit()
        return jsonify({'success': 'OK'})


class FeedbackListResource(Resource):
    def __init__(self) -> None:
        """Create sqldb parser"""
        self.parser = reqparse.RequestParser()
        self.session = db_session.create_session()
        self.parser.add_argument('owner_id', required=False)
        self.parser.add_argument('time', required=False)
        self.parser.add_argument('content', required=False)
        self.parser.add_argument('feedback', required=False)

    def get(self) -> dict:
        """API method get"""
        args = self.parser.parse_args()
        feedbacks = self.session.query(Feedbacks).filter(Feedbacks.id.in_(args['feedback'].split(','))).all()
        return jsonify({'feedbacks': [
            item.to_dict(rules=("-feedback", "-feedback")) for item in feedbacks]})

    def post(self) -> dict:
        """API method post"""
        args = self.parser.parse_args()
        feedback = Feedbacks(
            content=args['content'],
            owner_id=args['owner_id']
        )
        self.session.add(feedback)
        self.session.commit()
        return jsonify({'id': self.session.query(Feedbacks).all()[-1].id})
