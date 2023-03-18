from flask import jsonify, Response
from flask_restful import Resource, reqparse

import db_session
from plot import Plot


class PlotResource(Resource):
    def __init__(self) -> None:
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id_site', required=True)
        self.parser.add_argument('points', required=False)
        self.parser.add_argument('point_time', required=False)
        self.session = db_session.create_session()

    def get(self) -> Response:
        args = self.parser.parse_args()
        plots = self.session.query(Plot).get(args['id_site'])

        return jsonify({'plot': plots.to_dict(rules=("-plot", "-plot"))})

    def put(self) -> Response:
        args = self.parser.parse_args()
        plot = self.session.query(Plot).get(args['id_site'])
        if plot is not None:
            new_points = plot.points + ',' + args['points'] if plot.points else args['points']
            new_point_time = plot.point_time + ',' + args['point_time'] if plot.point_time else args['point_time']

            setattr(plot, 'points', new_points)
            setattr(plot, 'point_time', new_point_time)
        else:
            plot = Plot(
                id_site=args['id_site'],
                points=args['points'],
                point_time=args['point_time'],
            )
            self.session.add(plot)

        self.session.commit()

        return jsonify({'success': 'OK'})

    def post(self) -> Response:
        args = self.parser.parse_args()

        point = Plot(
            id_site=args['id_site'],
            points='',
            point_time=''
        )

        self.session.add(point)
        self.session.commit()

        return jsonify({'success': 'OK'})
