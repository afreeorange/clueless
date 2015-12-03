import logging
import sys
import importlib
from uuid import uuid4

import arrow
from flask import Flask, render_template, request, send_from_directory, jsonify
from flask_restful import Api, Resource

from game.service import BoardService

bs = BoardService(test_mode=True)

# -------

app = Flask(__name__)
app.debug = True
api = Api(app)


# CORS Headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response



# handler = logging.StreamHandler(sys.stdout)
# handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z'))
# handler.setLevel(logging.INFO)

# log = logging.getLogger('CluelessService')
# log.setLevel(logging.INFO)
# log.addHandler(handler)

class CluelessLog(Resource):
    def get(self):
        return bs.log


class CluelessPlayer(Resource):
    def get(self, player_token):
        try:
            return bs.get_player(player_token)
        except Exception as e:
            return {'message': str(e)}, 404


class CluelessPlayers(Resource):
    def get(self):
        return bs.players

    def post(self):
        try:
            return bs.add_player(
                        name=request.json.get('name'),
                        suspect=request.json.get('suspect'),
                        )
        except Exception as e:
            return {'message': str(e)}, 400


class CluelessEndTurn(Resource):
    def put(self):
        try:
            bs.end_turn(player_token=request.json.get('token'))
        except Exception as e:
            return {'message': str(e)}, 400


class CluelessMakeSuggestion(Resource):
    def put(self):
        try:
            return bs.make_suggestion(
                        player_token=request.json.get('token'),
                        suspect=request.json.get('suspect'),
                        weapon=request.json.get('weapon'),
                        )
        except Exception as e:
            return {'message': str(e)}, 400


class CluelessMakeAccusation(Resource):
    def put(self):
        try:
            bs.make_accusation(
                player_token=request.json.get('token'),
                suspect=request.json.get('suspect'),
                weapon=request.json.get('weapon'),
                room=request.json.get('room'),
                )
        except Exception as e:
            return {'message': str(e)}, 400
        else:
            return {}


class CluelessMove(Resource):
    def put(self):
        try:
            bs.move_player(
                player_token=request.json.get('token'),
                space=request.json.get('space'),
                )
        except Exception as e:
            return {'message': str(e)}, 400


class CluelessMetadata(Resource):
    def get(self):
        return bs.metadata


class CluelessConfidentialFile(Resource):
    def get(self):
        return bs.confidential_file


class Clueless(Resource):
    def get(self):
        return bs.state


api.add_resource(CluelessPlayer, '/api/players/<string:player_token>')
api.add_resource(CluelessPlayers, '/api/players')
api.add_resource(CluelessMove, '/api/move')
api.add_resource(CluelessMakeSuggestion, '/api/suggest')
api.add_resource(CluelessMakeAccusation, '/api/accuse')
api.add_resource(CluelessEndTurn, '/api/end_turn')
api.add_resource(CluelessLog, '/api/logs')
api.add_resource(CluelessMetadata, '/api/meta')
api.add_resource(CluelessConfidentialFile, '/api/confidential_file')
api.add_resource(Clueless, '/api')


@app.route('/new')
def new_game():
    global bs
    bs = BoardService(Board(), test_mode=True)
    return jsonify(bs.state)


@app.route('/')
def client_interface():
    return render_template('index.html')



# if __name__ == '__main__':
#     socketio.run(app)
