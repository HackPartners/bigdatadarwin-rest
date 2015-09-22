#Adding to pythonpath
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask
from flask_restful import Api
from resources.JourneyResource import JourneyResource
from resources.OnTimeResource import OnTimeResource
from resources.Cancellations import Cancellations


app = Flask(__name__)
api = Api(app)

@app.after_request
def after_request(response):
  # This function enables CORS in all requests
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET')
  return response

api.add_resource(JourneyResource, '/hist/1.0/journey')

api.add_resource(OnTimeResource, '/hist/1.0/ontime')

api.add_resource(Cancellations, "/hist/1.0/cancellations")
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3001, debug=True)
