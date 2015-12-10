import json

from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_socketio import SocketIO, emit
from game.service import BoardService

bs = BoardService(test_mode=True)

app = Flask(__name__)
app.debug = True
api = Api(app)
socketio = SocketIO(app, async_mode='eventlet')


# CORS Headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


class CluelessLog(Resource):
    def get(self):
        return bs.log


class CluelessPlayer(Resource):
    @classmethod
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
            player = bs.add_player(
                        name=request.json.get('name'),
                        suspect=request.json.get('suspect'),
                        )
        except Exception as e:
            return {'message': str(e)}, 400
        else:
            socketio.emit('board:state', bs.state)
            socketio.emit('board:log', bs.log)
            return player


class CluelessEndTurn(Resource):
    def put(self):
        try:
            bs.end_turn(player_token=request.json.get('token'))
        except Exception as e:
            return {'message': str(e)}, 400
        else:
            socketio.emit('board:state', bs.state)
            socketio.emit('board:log', bs.log)
            return {}


class CluelessMakeSuggestion(Resource):
    def put(self):
        try:
            suggestion = bs.make_suggestion(
                            player_token=request.json.get('token'),
                            suspect=request.json.get('suspect'),
                            weapon=request.json.get('weapon'),
                            )
        except Exception as e:
            return {'message': str(e)}, 400
        else:
            socketio.emit('board:state', bs.state)
            socketio.emit('board:log', bs.log)
            return suggestion


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
            # Doing this twice since the last player's wrong accusation
            # throws a "GameOver" exception. Need to push the board
            # state and logs before croaking...
            socketio.emit('board:state', bs.state)
            socketio.emit('board:log', bs.log)
            return {'message': str(e)}, 400
        else:
            socketio.emit('board:state', bs.state)
            socketio.emit('board:log', bs.log)
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
        else:
            socketio.emit('board:state', bs.state)
            socketio.emit('board:log', bs.log)
            return {}


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


@socketio.on('board:playerdata')
def playerdata(message):
    emit('board:playerdata', CluelessPlayer.get(player_token=message['token']))


@socketio.on('board:metadata')
def board_metadata():
    emit('board:metadata', bs.metadata)


@socketio.on('board:state')
def board_metadata():
    emit('board:state', bs.state)


@socketio.on('board:log')
def board_metadata():
    emit('board:log', bs.log)


@app.route('/new_game')
def new_game():
    global bs
    bs = BoardService(test_mode=True)
    socketio.emit('board:state', bs.state)
    socketio.emit('board:log', bs.log)
    socketio.emit('board:playerdata', None)
    return jsonify(bs.state)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)

