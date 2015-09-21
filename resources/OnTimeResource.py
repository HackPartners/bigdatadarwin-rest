from flask_restful import Resource, reqparse, marshal_with, fields

from common.util import api_bool

from bigdatadarwin.models import Schedule, CallingPoint

query_parser = reqparse.RequestParser()

query_parser.add_argument(
    'apiKey', dest='api_key',
    required=True,
    type=str, help='Your BigData Darwin API Key',
)

query_parser.add_argument(
    'service', dest='service',
    required=True,
    type=str, help='The TSDB ID (uid) of the service',
)

query_parser.add_argument(
    'station', dest='station',
    type=api_bool, help='Either the TIPLOC or CRS code for the station.',
)

class OnTimeResource(Resource):

    def get(self):

        args = query_parser.parse_args()

        service = args.service
        station = args.station

        return {
            "TODO": "Still work in progress"
        }