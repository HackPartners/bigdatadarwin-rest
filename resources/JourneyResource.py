from flask_restful import Resource, reqparse, marshal_with, fields

from common.darwinutil import get_service_details
from common.util import api_bool

from nredarwin.webservice import DarwinLdbSession, WebServiceError

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
    type=api_bool, help='Either the TIPLOC or CRS code for the station.',
)

class JourneyResource(Resource):

    def get(self):

        args = query_parser.parse_args()

        service = args.service
        station = args.station

        try:
            # In this query, we query for the "unique" number 
            # of schedules that contain a cancellation.
            cancelled = Schedule.select(
                    Schedule,
                    CallingPoint
                ).join(
                    CallingPoint
                ).where(
                    CallingPoint.tiploc=="ELPHNAC", 
                    CallingPoint.cancelled==True
                ).distinct(
                    [CallingPoint.working_departure,
                    CallingPoint.working_arrival]
                ).count()

            fulfilled = Schedule.select(
                    Schedule,
                    CallingPoint
                ).join(
                    CallingPoint
                ).where(
                    CallingPoint.tiploc=="ELPHNAC", 
                    CallingPoint.cancelled==False
                ).distinct(
                    [CallingPoint.working_departure,
                    CallingPoint.working_arrival]
                ).count()

            response = {
                "cancelled": cancelled,
                "fulfilled": fulfilled
            }
            
        except WebServiceError as e:
            response = {
                "error": "Darwin web service error - probably service id does not exist."
            }
        except Exception as e:
            response = {
                "error": str(e)
            }

        return response


        