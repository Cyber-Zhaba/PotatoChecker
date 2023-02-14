from flask_restful import Resource, reqparse, abort
from flask import jsonify
import db_session
from sites import Sites


def abort_sites_not_found(id):
    session = db_session.create_session()
    sites = session.query(Sites).get(id)
    if not sites:
        abort(404, messsage="Site wasn't found")


class SitesResource(Resource):
    def get(self, id):
        abort_sites_not_found(id)
        session = db_session.create_session()
        sites = session.query(Sites).get(id)
        return jsonify({'sites': sites.to_dict(rules=("-site", "-site"))})

    def delete(self, id):
        abort_sites_not_found(id)
        session = db_session.create_session()
        sites = session.query(Sites).get(id)
        session.delete(sites)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('owner_id', required=True)
parser.add_argument('link', required=True)
parser.add_argument('description', required=True)
parser.add_argument('state', required=True)
parser.add_argument('ids_feedback', required=True)


class ListSites(Resource):
    def get(self):
        session = db_session.create_session()
        sites = session.query(Sites).all()
        return jsonify({'sites': [
            item.to_dict(rules=("-site", "-site")) for item in sites
        ]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        sites = Sites(
            owner_id=args['owner_id'],
            link=args['link'],
            description=args['description'],
            state=args['state'],
            ids_feedbacks=args['ids_feedbacks'],
            )
        session.add(sites)
        session.commit()
        return jsonify({'success': 'OK'})
