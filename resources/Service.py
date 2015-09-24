from flask_restful import Resource, reqparse, marshal_with, fields
from peewee import prefetch
from common import util
from playhouse.shortcuts import model_to_dict

from bigdatadarwin.models import Schedule, CallingPoint

query_parser = reqparse.RequestParser()

query_parser.add_argument(
    'apiKey', dest='api_key',
    required=True,
    type=str, help='Your BigData Darwin API Key',
)

class Service(Resource):
    """The service returns schedules and all the calling points."""

    def get(self, service):
        where = self.get_where(service)
        if where is None:
            return {
                "err": "We don't understand that ID. Try an UID or a RID.",
            }

        # TODO pagination
        schedules = Schedule.select().where(where)
        callingpoints = CallingPoint.select().order_by(CallingPoint.id.asc())
        results = prefetch(schedules, callingpoints)



        res = []
        for s in results:

            res.append({
                "uid": s.uid,
                "rid": s.rid,
                "date": str(s.start_date),
                "toc": s.toc_code,
                "status": s.status,
                "category": s.category,
                "headcode": s.headcode,
                "active": s.active,
                "delete": s.deleted,
                "callingpoints": [
                    {
                        "id": c.id,
                        "station": c.tiploc,
                        "type": c.type,
                        "working_arrival": str(c.working_arrival),
                        "working_pass": str(c.working_pass),
                        "working_departure": str(c.working_departure),
                        "public_arrival": str(c.public_arrival),
                        "public_departure": str(c.public_departure),
                        "cancelled": c.cancelled,
                    } for c in s.callingpoint_set_prefetch
                ]
            })

        return res

    def get_where(self, service):
        stype = util.service(service)

        if stype == util.UID:
            return Schedule.uid == service
        if stype == util.RID:
            return Schedule.rid == service

        return None
