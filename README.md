# Clueless

A simplified version of [Clue](http://www.hasbro.com/en-us/product/clue-game:940119D4-6D40-1014-8BF0-9EFBF894F9D4) by Hasbro for a class project at [JHU](http://www.jhu.edu/). Here's what it looks like:

[<img src="http://i.imgur.com/u6srx2U.png" width="20%" />](http://i.imgur.com/u6srx2U.png)
[<img src="http://i.imgur.com/cpmVoJX.png" width="20%" />](http://i.imgur.com/cpmVoJX.png)
[<img src="http://i.imgur.com/D38LRkB.png" width="20%" />](http://i.imgur.com/D38LRkB.png)
[<img src="http://i.imgur.com/OOeIS3T.png" width="20%" />](http://i.imgur.com/OOeIS3T.png)
[<img src="http://i.imgur.com/cNkk9un.png" width="20%" />](http://i.imgur.com/cNkk9un.png)

Built using

* Python 3.5 and [Flask-SocketIO](https://flask-socketio.readthedocs.org/en/latest/)
* AngularJS 1.4.8 and [Socket.IO](http://socket.io/)

## Installation

```
# Install server requirements
pip install -r requirements.txt

# Build the SPA
cd client
npm install
bower install
gulp
```

## Running the app

You'll need to run both the Python server and the frontend SPA (in `client/dist`)

For the former,

    python server.py

For the latter, I use [`http-server`](https://github.com/indexzero/http-server)

    hs client/dist

Now navigate to `localhost:8080` to see the game.

## Notes

* Use REST calls to mutate game state.
* Use websockets to send state to connected players.
	* Board state is sent via `board:state`
	* Game log is sent via `board:logs`
	* Player data is sent via `board:playerdata`
* Adding a player will return a JSON object that contains the player's token. This is to be used for all interactions detailed in the API section.
* If `BoardService` is initialized with `test_mode=True`, player tokens are not UUIDs but simply "a" through "f", in order of player addition.

## API

The REST API is built using `game.service` which wraps `game.engine`. A valid

* `<suspect>` is one of `scarlet`, `mustard`, `white`, `green`, `peacock`, `plum`
* `<weapon>` is one of `rope`, `knife`, `lead_pipe`, `wrench`, `revolver`, `candlestick`
* `<space>` is either a
	* room: `study`, `hall`, `lounge`, `library`, `billiard_room`, `dining_room`, `conservatory`, `ballroom`, `kitchen`
	* or a hallway: `study_to_hall`, `hall_to_lounge`, `study_to_library`, `hall_to_billiard`, `lounge_to_dining`, `library_to_billiard`, `billiard_to_dining`, `library_to_conservatory`, `billiard_to_ballroom`, `dining_to_kitchen`, `conservatory_to_ballroom`, `ballroom_to_kitchen`

---

### Add a Player

```
POST /api/players
Content-Type: application/json

{
    "name": "<String>",
    "suspect": "<suspect>"
}
```

### See Board State

```
GET /api
```

### See Game Log

```
GET /api/logs
```

### See Confidential File

```
GET /api/confidential_file
```

### Move Player

```
PUT /api/move
Content-Type: application/json

{
    "token": "<player token>",
    "space": "<space>"
}
```

### Make Suggestion

```
PUT /api/suggest
Content-Type: application/json

{
    "token": "<player token>",
    "weapon": "<weapon>",
    "suspect": "<suspect>"
}
```

### Make Accusation

```
PUT /api/accuse
Content-Type: application/json

{
    "token": "<player token>",
    "weapon": "<weapon>",
    "suspect": "<suspect>",
    "space": "<space>"
}
```

### End Turn

```
PUT /api/end_turn
Content-Type: application/json

{
    "token": "<player token>"
}
```

## Author
	
Nikhil Anand <mail@nikhil.io>

## Image Sources

[1](http://craftypantscarol.com/2012/12/clue-board-game-1950-edition.html.), [2](https://www.pinterest.com/pin/113786328058659174/), [3](https://www.pinterest.com/pin/41095415327567834/), [4](https://www.pinterest.com/pin/537898749219226995/), [5](https://www.flickr.com/photos/rosered/sets/805113)

## License

MIT
