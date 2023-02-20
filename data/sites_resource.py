from flask_restful import Resource, reqparse, abort
from flask import jsonify, Response
from data import db_session
from data.sites import Sites


class SitesResource(Resource):
    def __init__(self) -> None:
        """Create sqldb parser"""
        self.parser = reqparse.RequestParser()
        self.session = db_session.create_session()
        self.parser.add_argument('owner_id', required=False)
        self.parser.add_argument('link', required=False)
        self.parser.add_argument('description', required=False)
        self.parser.add_argument('ping', required=False)
        self.parser.add_argument('check_time', required=False)
        self.parser.add_argument('ids_feedback', required=False)
        self.parser.add_argument('feedback_id', required=False)
        self.parser.add_argument('type', required=False)

    def abort_sites_not_found(self, index: int) -> None:
        """Returns 404 ERROR if id not found"""
        sites = self.session.query(Sites).get(index)
        if not sites:
            abort(404, messsage="Site wasn't found")

    def get(self, site_id: int) -> Response:
        """API method get"""
        self.abort_sites_not_found(site_id)
        sites = self.session.query(Sites).get(site_id)
        return jsonify({'sites': sites.to_dict(rules=("-site", "-site"))})

    def delete(self, site_id: int) -> Response:
        """API method delete"""
        self.abort_sites_not_found(site_id)
        sites = self.session.query(Sites).get(site_id)
        self.session.delete(sites)
        self.session.commit()
        return jsonify({'success': 'OK'})

    def put(self, site_id: int) -> Response:
        self.abort_sites_not_found(site_id)
        args = self.parser.parse_args()
        site = self.session.query(Sites).get(site_id)

        match args['type']:
            case 'mod':
                setattr(site, 'moderated', 1)
            case 'update_ping':
                setattr(site, 'ping', ','.join(
                    [item for item in site.ping.split(',') + [args['ping']] if item]))
            case 'add_feedback':
                zheleboba = ','.join(
                    [item for item in filter(lambda x: x, (site.ids_feedbacks.split(',') + [args['feedback_id']]))])
                setattr(site, 'ids_feedbacks', zheleboba)

        self.session.commit()
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
        self.parser.add_argument('feedback_id', required=False)
        self.parser.add_argument('id', required=False)

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
                result = jsonify({
                    'favourite_sites': [item.to_dict(
                        only=('name', 'id', 'link', 'ping')) for item in favourite_sites_set],
                    'not_favourite_sites': [item.to_dict(
                        only=('name', 'id', 'link', 'ping')) for item in sites_not_favourite]
                })
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
                result = jsonify({'sites': [item.to_dict(
                    only=('name', 'id', 'link', 'ids_feedbacks')) for item in strict]})
            case 'feedback_in_site':
                site = self.session.query(Sites).all()
                for i in site:
                    if args['feedback_id'] in i.ids_feedbacks.split(','):
                        site = i
                result = jsonify({'sites': [site.to_dict(only=('name', 'id', 'link', 'ids_feedbacks'))]})
            case 'all_ping_clear':
                all_ping = self.session.query(Sites).filter(Sites.moderated == 1).all()
                result = jsonify({'sites': [site.to_dict(only=('id', 'ping', 'reports')) for site in all_ping]})
                for site in all_ping:
                    setattr(site, 'ping', '')
                    setattr(site, 'reports', '')
                self.session.commit()

        return result

    def post(self) -> Response:
        """API method post"""
        args = self.parser.parse_args()
        sites = Sites(
            owner_id=args['owner_id'],
            name=args['name'],
            link=args['link'],
            ids_feedbacks='',
            ping='',
            check_time='',
            moderated=0
        )
        self.session.add(sites)
        self.session.commit()
        return jsonify({'success': 'OK'})

    def put(self) -> Response:
        args = self.parser.parse_args()
        if args['type'] == 'report':
            site = self.session.query(Sites).filter(Sites.name == args['name']).first()
            if str(args['id']) not in site.reports.split(','):
                setattr(site, 'reports', (
                    site.reports + ',' + args['id'] if site.reports else args['id']
                ))
        else:
            site = self.session.query(Sites).filter(Sites.name == args['name']).first()
            feedbacks = site.ids_feedbacks.split(',')
            feedbacks.remove(args['feedback_id'])
            zheleboba = '' if len(feedbacks) == 0 else ','.join(feedbacks)
            setattr(site, 'ids_feedbacks', zheleboba)
        self.session.commit()
        return jsonify({'success': 'OK'})
