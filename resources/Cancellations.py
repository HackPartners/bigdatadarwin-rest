from flask_restful import Resource, reqparse, marshal_with, fields

from common.util import api_bool, validate_tiploc

from bigdatadarwin.models import Schedule, CallingPoint

import datetime

query_parser = reqparse.RequestParser()

query_parser.add_argument(
    'apiKey', dest='api_key',
    required=True,
    type=str, help='Your BigData Darwin API Key',
)

query_parser.add_argument(
    'day', dest='day',
    type=str, help='The day, as yyyy-mm-dd',
)

query_parser.add_argument(
    'uid', dest='uid',
    type=str, help='The TSDB ID (uid) of the service',
)

query_parser.add_argument(
    'rid', dest='rid',
    type=str, help='The RID of the service.',
)

query_parser.add_argument(
    'tiploc', dest='tiploc',
    type=str, help='Either the TIPLOC or CRS code for the station.',
)


class Cancellations(Resource):

    def get(self):

        args = query_parser.parse_args()

        if args.day:
            try:
                args.day = datetime.datetime.strptime(args.day, "%Y-%m-%d")
                args.day = args.day.date()
            except ValueError:
                return {
                    "Error": "Day must be of format yyyy-mm-dd.",
                }

        if args.tiploc:
            args.tiploc = validate_tiploc(args.tiploc)

        try:
            count_cancelled = self._get_cancellations(True, args)
            count_fulfilled = self._get_cancellations(False, args)

            return {
                "cancelled": count_cancelled,
                "fulfilled": count_fulfilled,
            }

        except Exception as e:
            return {
                "err": "Something went wrong, please try again.",
            }

    def _get_cancellations(self, cancelled, args):

        query_params = CallingPoint.cancelled==cancelled

        if args.day:
            query_params = query_params & (Schedule.start_date==args.day)

        if args.tiploc:
            query_params = query_params & (CallingPoint.tiploc==args.tiploc)

        if args.uid:
            query_params = query_params & (CallingPoint.uid==args.uid)

        if args.rid:
            query_params = query_params & (CallingPoint.rid==args.rid)

        res =  CallingPoint.select(
            CallingPoint.id
        ).join(
            Schedule
        ).where(
            query_params
        )

        return res.count()
