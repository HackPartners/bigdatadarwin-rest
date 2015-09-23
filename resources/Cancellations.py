from flask_restful import Resource, reqparse, marshal_with, fields

from common import util

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
    'service', dest='service',
    type=str, help='The train RID or UID.',
)

query_parser.add_argument(
    'station', dest='station',
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
                    "err": "Day must be of format yyyy-mm-dd.",
                }

        if args.station:
            args.station = util.validate_tiploc(args.station)

        if args.service:
            args.stype = util.service(args.service)
            if args.stype == util.TRAINID:
                return {
                    "err": "Only rid and uid supported at the moment,"\
                        " trainId was given.",
                }

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

        if args.station:
            query_params = query_params & (CallingPoint.tiploc==args.station)

        if args.service:
            if args.stype == util.UID:
                query_params = query_params & (Schedule.uid==args.service)
            else:
                query_params = query_params & (Schedule.rid==args.service)

        res =  CallingPoint.select(
            CallingPoint.id
        ).join(
            Schedule
        ).where(
            query_params
        )

        return res.count()
