from flask_restful import Resource, reqparse, marshal_with, fields
from peewee import prefetch
from common import util
from playhouse.shortcuts import model_to_dict
import json

from bigdatadarwin.models import Schedule, CallingPoint

query_parser = reqparse.RequestParser()

query_parser.add_argument(
    'apiKey', dest='api_key',
    required=True,
    type=str, help='Your BigData Darwin API Key',
)


def date_handler(obj):
    # Fix for date not being serializable in python for json objects
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

class ServiceResource(Resource):
    """The service returns schedules and all the calling points."""

    def get(self, service):

        s = Schedule.get(Schedule.rid == service)

        schedule = model_to_dict(s, recurse=True, backrefs=True)

        # Reverse the list of calling points
        schedule["callingpoint_set"] = schedule["callingpoint_set"][::-1]

        return json.loads(json.dumps(schedule, default=date_handler))