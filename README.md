# Clueless

A reduced version of [Clue](http://www.hasbro.com/en-us/product/clue-game:940119D4-6D40-1014-8BF0-9EFBF894F9D4) by Hasbro. Made for a class project at [JHU](http://www.jhu.edu/). 

## Installation

    npm install
    bower install
    
    # Please use a virtualenv
    pip install -r requirements.txt

    # Build the SPA
    cd client
    gulp

## Running the app

You'll need to run both the Python server and the frontend SPA (in `client/dist`)

For the former,

    python server.py

For the latter, I use [`http-server`](https://github.com/indexzero/http-server)

    hs client/dist

Now navigate to `localhost:8080` to see the game.

## Author
	
Nikhil Anand <mail@nikhil.io>

## License

MIT
