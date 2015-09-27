
from bigdatadarwin.models import db

def get_cancellations(
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


