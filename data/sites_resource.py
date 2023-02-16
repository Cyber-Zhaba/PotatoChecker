from flask_restful import Resource, reqparse, abort
from flask import jsonify
from data import db_session
from data.sites import Sites


def abort_sites_not_found(index: int) -> None:
    """Returns 404 ERROR if id not found"""
    session = db_session.create_session()
    sites = session.query(Sites).get(index)
    if not sites:
        abort(404, messsage="Site wasn't found")


class SitesResource(Resource):
    def __init__(self) -> None:
        """Create sqldb parser"""
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('owner_id', required=True)
        self.parser.add_argument('link', required=True)
        self.parser.add_argument('description', required=True)
        self.parser.add_argument('ping', required=True)
        self.parser.add_argument('check_time')
        self.parser.add_argument('ids_feedback', required=True)

    @staticmethod
    def get(index: int) -> dict:
        """API method get"""
        abort_sites_not_found(index)
        session = db_session.create_session()
        sites = session.query(Sites).get(index)
        return jsonify({'sites': sites.to_dict(rules=("-site", "-site"))})

    @staticmethod
    def delete(index: int) -> dict:
        """API method delete"""
        abort_sites_not_found(index)
        session = db_session.create_session()
        sites = session.query(Sites).get(index)
        session.delete(sites)
        session.commit()
        return jsonify({'success': 'OK'})


class ListSites(Resource):
    def __init__(self) -> None:
        """Create sqldb parser"""
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('owner_id', required=True)
        self.parser.add_argument('link', required=True)
        self.parser.add_argument('description', required=True)
        self.parser.add_argument('ping', required=True)
        self.parser.add_argument('check_time', required=True)
        self.parser.add_argument('ids_feedback', required=True)

    @staticmethod
    def get() -> dict:
        """API method get"""
        session = db_session.create_session()
        sites = session.query(Sites).all()
        return jsonify({'sites': [
            item.to_dict(rules=("-site", "-site")) for item in sites
        ]})

    def post(self) -> dict:
        """API method post"""
        args = self.parser.parse_args()
        session = db_session.create_session()
        sites = Sites(
            owner_id=args['owner_id'],
            link=args['link'],
            description=args['description'],
            ping=args['ping'],
            check_time=args['check_time'],
            ids_feedbacks=args['ids_feedbacks'],
        )
        session.add(sites)
        session.commit()
        return jsonify({'success': 'OK'})
