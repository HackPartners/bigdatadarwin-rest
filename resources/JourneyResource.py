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
    type=str, help='The TSDB ID (uid) of the service',
)

query_parser.add_argument(
    'station', dest='station',
    type=str, help='Either the TIPLOC or CRS code for the station.',
)

query_parser.add_argument(
    'granularity', dest='granularity',
    type=str, help='Either the TIPLOC or CRS code for the station.',
)

query_parser.add_argument(
    'granularity', dest='granularity',
    default=DEFAULT_GRANULARITY,
    type=str, help='Either the TIPLOC or CRS code for the station.',
)


class JourneyResource(Resource):

    def get(self):

        args = query_parser.parse_args()

        service = validate_service(args.service) if args.service else None
        granularity = validated_granularity(args.granularity)
        station = validate_tiploc(args.station)
        print granularity

        date_to = datetime.datetime.now().date()
        date_from = date_to - datetime.timedelta(days=DEFAULT_DAY_WINDOW)

        try:
            journeys = self._get_journeys(
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
                "to": str(date_to)
            }

        except Exception as e:
            response = {
                "error": str(e)
            }

        return response

    def _get_journeys(self, granularity, station, service, from_date, to_date):
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
            SELECT s.total, s.cancelled, s.fulfilled
            FROM (
                SELECT
                    s.start_date as start_date, s.uid as uid,
                    COUNT(c.id) as total,
                    COUNT(CASE WHEN c.cancelled THEN 1 ELSE null END) as cancelled,
                    COUNT(CASE WHEN c.cancelled THEN null ELSE 1 END) as fulfilled
                FROM callingpoint c
                JOIN (
                    SELECT * FROM schedule
                    %s
                ) s ON s.id = c.schedule_id
                %s
                GROUP BY s.start_date, s.uid
                ORDER BY cancelled DESC
            ) s 
            JOIN t ON 
            t.start_time <= s.start_date AND t.end_time > s.start_date
        """ % ( granularity,
                from_date, 
                to_date, 
                granularity,
                ("WHERE uid=%s" % service) if service else "",
                ("WHERE tiploc='%s'" % station) if station else ""))

        cursor = db.execute_sql(query)
        # TODO: Make a proper class for this.
        result = [
            { 
                "total": int(l[0]),
                "cancelled": int(l[1]),
                "fulfilled": int(l[2])
            } 
            for l in cursor.fetchall()]


        return result

