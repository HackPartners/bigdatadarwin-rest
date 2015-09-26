from flask_restful import Resource, reqparse, marshal_with, fields

from common.util import api_bool, validate_tiploc, validated_granularity, validate_service

from bigdatadarwin.models import db

import datetime

DEFAULT_GRANULARITY="day"
DEFAULT_DAY_WINDOW=7

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
    'station', dest='station',
    type=str, help='Either the TIPLOC or CRS code for the station.',
)

query_parser.add_argument(
    'granularity', dest='granularity',
    default=DEFAULT_GRANULARITY,
    type=str, help='Granularity desired. Can be day, week or month.',
)


class JourneyResource(Resource):

    def get(self, service=None, station=None):

        # We check the grouping that will be used in the SQL query
        if service:
            grouping = "s.uid"
        elif station:
            grouping = "c.tiploc"
        else:
            raise Exception("No service or station given")

        args = query_parser.parse_args()

        granularity = validated_granularity(args.granularity)
        service = validate_service(args.service) if (not service and args.service) else service
        station = validate_tiploc(args.station) if (not station and args.station) else station

        date_to = datetime.datetime.now().date()
        date_from = date_to - datetime.timedelta(days=DEFAULT_DAY_WINDOW)

        try:
            journeys = self._get_journeys(
                    grouping,
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

    def _get_journeys(
            self, 
            grouping,
            granularity, 
            station, 
            service, 
            from_date, 
            to_date):
        """Function that queries the database for number of cancelled and fulfilled journeys.

        Args:
            granularity (string): The type of granularity desired. It can be day, month, week.
            station (string): The tiploc or crs station code.
            service (string): The uid service id.
            from_date (Date): The date to use as FROM.
            to_date (Date): The date to use as TO.

        Returns:
            JourneyResponse: A JourneyResponse object containing an array of cancelled/fulfilled journeys.
        """

        query = ("""
            WITH t AS (
                -- generate start_time and end_time interval of 1 day 
                SELECT
                n AS start_time, 
                n + interval '1' %s AS end_time
                from GENERATE_SERIES('%s', '%s', 
                   '1 %s'::interval) n
                   )
            SELECT t.start_time, t.end_time, s.total, s.cancelled, s.fulfilled
            FROM (
                SELECT
                    s.start_date as start_date,
                    COUNT(c.id) as total,
                    COUNT(CASE WHEN c.cancelled THEN 1 ELSE null END) as cancelled,
                    COUNT(CASE WHEN c.cancelled THEN null ELSE 1 END) as fulfilled
                FROM callingpoint c
                JOIN (
                    SELECT * FROM schedule
                    %s
                ) s ON s.id = c.schedule_id
                %s
                GROUP BY s.start_date, %s
                ORDER BY cancelled DESC
            ) s 
            RIGHT OUTER JOIN t ON 
            t.start_time <= s.start_date AND t.end_time > s.start_date
        """ % ( granularity,
                from_date, 
                to_date, 
                granularity,
                ("WHERE uid='%s'" % service) if service else "",
                ("WHERE tiploc='%s'" % station) if station else "",
                grouping ))

        print ( granularity,
                from_date, 
                to_date, 
                granularity,
                ("WHERE uid='%s'" % service) if service else "",
                ("WHERE tiploc='%s'" % station) if station else "",
                grouping )
        cursor = db.execute_sql(query)
        # TODO: Make a proper class for this.
        result = [
            { 
                "from": str(l[0]),
                "to": str(l[1]),
                "total": int(l[2]) if l[2] else 0,
                "cancelled": int(l[3]) if l[3] else 0,
                "fulfilled": int(l[4]) if l[4] else 0
            } 
            for l in cursor.fetchall()]


        return result

