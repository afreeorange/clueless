from engine import Board
from engine.constants import *

from flask import Flask, request, render_template
from flask_restful import Resource, Api

app = Flask(__name__, template_folder='./')
app.debug = True
api = Api(app)
# board = Board()


def abort(message=None, code=500):
    api.make_response({'error': message}, code)


class SuspectList(Resource):
    def get(self):
        
        return {}


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


api.add_resource(HelloWorld, '/api')
api.add_resource(SuspectList, '/api/suspect_list')


@app.route('/')
def index():
    return render_template('socket_client.html')


if __name__ == '__main__':
    socketio.run(app)
