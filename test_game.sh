#!/bin/bash

unset http_proxy
unset https_proxy

curl -X POST http://localhost:8000/api/players --header 'content-type: application/json' --data '{"name": "Nikhil", "suspect": "scarlet"}'
curl -X POST http://localhost:8000/api/players --header 'content-type: application/json' --data '{"name": "Dawn", "suspect": "white"}'
curl -X POST http://localhost:8000/api/players --header 'content-type: application/json' --data '{"name": "Madhu", "suspect": "mustard"}'
curl -X POST http://localhost:8000/api/players --header 'content-type: application/json' --data '{"name": "Deepu", "suspect": "green"}'
curl -X POST http://localhost:8000/api/players --header 'content-type: application/json' --data '{"name": "Catherine", "suspect": "peacock"}'
curl -X POST http://localhost:8000/api/players --header 'content-type: application/json' --data '{"name": "Tony", "suspect": "plum"}'

