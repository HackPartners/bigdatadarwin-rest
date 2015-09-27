#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#Adding to pythonpath
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask
from flask_restful import Api
from resources.JourneyResource import JourneyResource
from resources.ServiceResource import ServiceResource
from resources.ServiceJourneyResource import ServiceJourneyResource
from resources.StationJourneyResource import StationJourneyResource

app = Flask(__name__)
api = Api(app)

DEBUG = os.getenv("BIGDATADARWIN_DEBUG", False)

@app.after_request
def after_request(response):
  # This function enables CORS in all requests
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET')
  return response

api.add_resource(JourneyResource, 
                '/hist/1.0/journey/service/<string:service>',
                '/hist/1.0/journey/station/<string:station>')


###################################################
##################### Station #####################
###################################################

api.add_resource(StationJourneyResource, 
                "/hist/1.0/station/<string:station>/journey")


###################################################
##################### Service #####################
###################################################

api.add_resource(ServiceResource, 
                "/hist/1.0/service/<string:service>")

api.add_resource(ServiceJourneyResource, 
                '/hist/1.0/service/<string:service>/journey')

if __name__ == '__main__':

    if DEBUG:
        app.run(host='127.0.0.1', port=3001, debug=True)
    else:
        app.run(host='0.0.0.0', port=80, debug=False)

