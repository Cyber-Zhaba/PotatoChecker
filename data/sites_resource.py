from flask_restful import Resource, reqparse, abort
from flask import jsonify, Response
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
        self.parser.add_argument('ids_feedback', required=True)

    @staticmethod
    def get(site_id: int) -> Response:
        """API method get"""
        abort_sites_not_found(site_id)
        session = db_session.create_session()
        sites = session.query(Sites).get(site_id)
        return jsonify({'sites': sites.to_dict(rules=("-site", "-site"))})

    @staticmethod
    def delete(site_id: int) -> Response:
        """API method delete"""
        abort_sites_not_found(site_id)
        session = db_session.create_session()
        sites = session.query(Sites).get(site_id)
        session.delete(sites)
        session.commit()
        return jsonify({'success': 'OK'})


class SitesListResource(Resource):
    def __init__(self) -> None:
        """Create sqldb parser"""
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('owner_id', required=False)
        self.parser.add_argument('name', required=False)
        self.parser.add_argument('link', required=False)
        self.parser.add_argument('description', required=False)
        self.parser.add_argument('state', required=False)
        self.parser.add_argument('ids_feedbacks', required=False)

        self.parser.add_argument('type', required=True)
        self.parser.add_argument('favourite_sites', required=False)

    def get(self) -> Response:
        """API method get"""
        args = self.parser.parse_args()
        session = db_session.create_session()

        match args['type']:
            case 'favourite_sites':
                sites = session.query(Sites).filter(Sites.id.in_(args['favourite_sites'].split(','))).all()
            case 'not_favourite_sites':
                sites = session.query(Sites).filter(~ (Sites.id.in_(args['favourite_sites'].split(',')))).all()
            case 'favourite_sites_and_name':
                sites = session.query(Sites).filter(Sites.name.contains(args['name']),
                                                    Sites.id.in_(args['favourite_sites'].split(','))).all()
            case 'not_favourite_sites_and_name':
                sites = session.query(Sites).filter(Sites.name.contains(args['name']),
                                                    ~(Sites.id.in_(args['favourite_sites'].split(',')))).all()
            case 'all':
                sites = session.query(Sites).all()
            case 'name':
                sites = session.query(Sites).filter(Sites.name.contains(args['name'])).all()

        return jsonify({'sites': [
            item.to_dict(rules=("-site", "-site")) for item in sites
        ]})

    def post(self) -> Response:
        """API method post"""
        args = self.parser.parse_args()
        session = db_session.create_session()
        sites = Sites(
            owner_id=args['owner_id'],
            link=args['link'],
            description=args['description'],
            ping=args['ping'],
            ids_feedbacks=args['ids_feedbacks'],
        )
        session.add(sites)
        session.commit()
        return jsonify({'success': 'OK'})
