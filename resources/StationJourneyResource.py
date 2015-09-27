from flask_restful import Resource, reqparse, marshal_with, fields

from common.util import api_bool, validate_tiploc, validated_granularity, validate_service

from common.dbqueries import get_cancellations

import datetime

DEFAULT_GRANULARITY="day"
DEFAULT_DAY_WINDOW=7
QUERY_GROUPING="c.tiploc"

query_parser = reqparse.RequestParser()

query_parser.add_argument(
    'apiKey', dest='api_key',
    required=True,
    type=str, help='Your BigData Darwin API Key',
)

query_parser.add_argument(
    'service', dest='service',
    type=str, help='Service ID for the schedule (uid).',
)

query_parser.add_argument(
    'granularity', dest='granularity',
    default=DEFAULT_GRANULARITY,
    type=str, help='Granularity desired. Can be day, week or month.',
)


class StationJourneyResource(Resource):

    def get(self, station=None):

        args = query_parser.parse_args()

        granularity = validated_granularity(args.granularity)
        service = validate_service(args.service)
        station = validate_tiploc(station)

        date_to = datetime.datetime.now().date()
        date_from = date_to - datetime.timedelta(days=DEFAULT_DAY_WINDOW)

        try:
            journeys = get_cancellations(
                    QUERY_GROUPING,
                    granularity, 
                    station, 
                    service, 
                    date_from,
                    date_to)

            response = {
                "service": service,
                "station": station,
                "journeys": journeys,
                "from": str(date_from),
                "to": str(date_to),
                "granularity": granularity
            }

        except Exception as e:
            response = {
                "error": str(e)
            }


        return response



