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
        print "params:", service, station

        try:
            cancelled = self._get_cancellations(True, station)
            fulfilled = self._get_cancellations(False, station)

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
            raise Exception("Either service and/or service must be provided.")

        query_params = []
        query_params.append(CallingPoint.cancelled==cancelled)

        if tiploc: query_params.append(CallingPoint.tiploc==tiploc)
        if service: query_params.append(Schedule.uid==service)

        # In this query, we query for the "unique" number 
        # of schedules that contain a cancellation.
        print tiploc
        schedules_found = Schedule.select(
                        Schedule,
                        CallingPoint
                    ).join(
                        CallingPoint
                    ).where(
                        CallingPoint.tiploc==tiploc
                    ).distinct(
                        [CallingPoint.working_departure,
                        CallingPoint.working_arrival]
                    )
        print schedules_found
        print schedules_found.count()

        return schedules_found.count()


