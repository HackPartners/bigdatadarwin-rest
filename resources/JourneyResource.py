from flask_restful import Resource, reqparse, marshal_with, fields

from common.util import api_bool, validate_tiploc

from bigdatadarwin.models import Schedule, CallingPoint

query_parser = reqparse.RequestParser()

query_parser.add_argument(
    'apiKey', dest='api_key',
    required=True,
    type=str, help='Your BigData Darwin API Key',
)

query_parser.add_argument(
    'service', dest='service',
    type=str, help='The TSDB ID (uid) of the service',
)

query_parser.add_argument(
    'station', dest='station',
    type=str, help='Either the TIPLOC or CRS code for the station.',
)


class JourneyResource(Resource):

    def get(self):

        args = query_parser.parse_args()

        service = args.service
        station = validate_tiploc(args.station)

        try:
            cancelled = self._get_cancellations(True, station, service)
            fulfilled = self._get_cancellations(False, station, service)

            response = {
                "cancelled": cancelled,
                "fulfilled": fulfilled
            }

        except Exception as e:
            response = {
                "error": str(e)
            }

        return response

    def _get_cancellations(self, cancelled=False, tiploc=None, service=None):

        if not tiploc and not service:
            raise Exception("Either service and/or tiploc must be provided.")

        query_params = CallingPoint.cancelled==cancelled

        if tiploc: query_params = query_params & (CallingPoint.tiploc==tiploc)
        if service: query_params = query_params & (Schedule.uid==service)

        # In this query, we query for the "unique" number
        # of schedules that contain a cancellation.
        schedules_found = Schedule.select(
                        Schedule,
                        CallingPoint
                    ).join(
                        CallingPoint
                    ).where(
                        query_params
                    ).distinct(
                        [Schedule.uid,
                        Schedule.rid]
                    ).order_by(
                        [Schedule.uid.desc(),
                        Schedule.rid.desc(),
                        Schedule.id.desc()]
                    )

        return schedules_found.count()
