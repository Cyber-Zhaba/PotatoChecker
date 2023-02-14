from flask_restful import Resource, reqparse, abort
from flask import jsonify
import db_session
from feedbacks import Feedbacks


def abort_feedback_not_found(id):
    session = db_session.create_session()
    feedbacks = session.query(Feedbacks).get(id)
    if not feedbacks:
        abort(404, messsage="Feedback wasn't found")


class SitesResource(Resource):
    def get(self, id):
        abort_feedback_not_found(id)
        session = db_session.create_session()
        feedbacks = session.query(Feedbacks).get(id)
        return jsonify({'sites': feedbacks.to_dict(rules=("-feedback", "-feedback"))})

    def delete(self, id):
        abort_feedback_not_found(id)
        session = db_session.create_session()
        feedbacks = session.query(Feedbacks).get(id)
        session.delete(feedbacks)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('owner_id', required=True)
parser.add_argument('time', required=True)
parser.add_argument('content', required=True)


class ListSites(Resource):
    def get(self):
        session = db_session.create_session()
        feedbacks = session.query(Feedbacks).all()
        return jsonify({'feedbacks': [
            item.to_dict(rules=("-feedback", "-feedback")) for item in feedbacks
        ]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        feedbacks = Feedbacks(
            owner_id=args['owner_id'],
            time=args['time'],
            content=args['content'],
        )
        session.add(feedbacks)
        session.commit()
        return jsonify({'success': 'OK'})

