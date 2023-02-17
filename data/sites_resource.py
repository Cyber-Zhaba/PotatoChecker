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
        self.parser.add_argument('owner_id', required=False)
        self.parser.add_argument('link', required=False)
        self.parser.add_argument('description', required=False)
        self.parser.add_argument('ping', required=False)
        self.parser.add_argument('check_time', required=False)
        self.parser.add_argument('ids_feedback', required=False)

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

    def put(self, site_id: int) -> Response:
        abort_sites_not_found(site_id)
        args = self.parser.parse_args()
        session = db_session.create_session()

        site = session.query(Sites).get(site_id)

        setattr(site, 'moderated', 1)

        session.commit()
        return jsonify({'success': 'OK'})


class SitesListResource(Resource):
    def __init__(self) -> None:
        """Create sqldb parser"""
        self.session = db_session.create_session()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('owner_id', required=False)
        self.parser.add_argument('name', required=False)
        self.parser.add_argument('link', required=False)
        self.parser.add_argument('type', required=True)
        self.parser.add_argument('favourite_sites', required=False)

    def get(self) -> Response:
        """API method get"""
        args = self.parser.parse_args()
        result = jsonify({'status': 'Failed'})
        if args['favourite_sites'] is None:
            favourite = []
        else:
            favourite = args['favourite_sites'].split(',')
        all_sites = self.session.query(Sites)
        match args['type']:
            case 'all_by_groups':
                sites_set = set(all_sites.filter(Sites.moderated == 1).all())
                favourite_sites_set = set(all_sites.filter(Sites.id.in_(favourite), Sites.moderated == 1).all())
                sites_not_favourite = sites_set - favourite_sites_set
                result = jsonify(
                    {'favourite_sites': [item.to_dict(only=('name', 'id', 'link')) for item in favourite_sites_set],
                     'not_favourite_sites': [item.to_dict(only=('name', 'id', 'link')) for item in sites_not_favourite]})
            case 'sites_by_name':
                sites_favourite = all_sites.filter(Sites.name.contains(args['name']),
                                                   Sites.id.in_(favourite), Sites.moderated == 1).all()
                sites_not_favourite = all_sites.filter(Sites.name.contains(args['name']),
                                                       ~Sites.id.in_(favourite), Sites.moderated == 1).all()
                result = jsonify({'favourite_sites': [item.to_dict(only=('name', 'id', 'link'))
                                                      for item in sites_favourite],
                                  'not_favourite_sites': [item.to_dict(only=('name', 'id', 'link'))
                                                          for item in sites_not_favourite]})
            case 'all':
                all_sites = self.session.query(Sites).filter(Sites.moderated == 1).all()
                result = jsonify({'sites': [item.to_dict(only=('name', 'id', 'link')) for item in all_sites]})
            case 'name':
                name_sites = self.session.query(Sites).filter(Sites.name.contains(args['name']),
                                                              Sites.moderated == 1).all()
                result = jsonify({'sites': [item.to_dict(only=('name', 'id', 'link')) for item in name_sites]})
            case 'to_moderation':
                mod = self.session.query(Sites).filter(Sites.moderated == 0).all()
                result = jsonify({'sites': [item.to_dict(rules=("-site", "-site")) for item in mod]})
            case 'strict_name':
                strict = self.session.query(Sites).filter(Sites.name == args['name'])
                result = jsonify({'sites': [item.to_dict(only=('name', 'id', 'link', 'ids_feedbacks')) for item in strict]})
        return result

    def post(self) -> Response:
        """API method post"""
        args = self.parser.parse_args()
        session = db_session.create_session()
        sites = Sites(
            owner_id=args['owner_id'],
            name=args['name'],
            link=args['link'],
            ids_feedbacks='',
            moderated=0
        )
        session.add(sites)
        session.commit()
        return jsonify({'success': 'OK'})
