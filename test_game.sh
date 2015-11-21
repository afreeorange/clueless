#!/bin/bash

unset http_proxy
unset https_proxy

curl -X GET 'http://localhost:8000'
echo -e ''
curl -X POST -H "Content-Type: multipart/form-data" -F "name=Nikhil" -F "suspect=scarlet" 'http://localhost:8000/players'
echo -e ''
curl -X POST -H "Content-Type: multipart/form-data" -F "name=Dawn" -F "suspect=white" 'http://localhost:8000/players'
echo -e ''
curl -X POST -H "Content-Type: multipart/form-data" -F "name=Madhu" -F "suspect=mustard" 'http://localhost:8000/players'
echo -e ''
curl -X POST -H "Content-Type: multipart/form-data" -F "name=Deepu" -F "suspect=green" 'http://localhost:8000/players'
echo -e ''
curl -X POST -H "Content-Type: multipart/form-data" -F "name=Catherine" -F "suspect=peacock" 'http://localhost:8000/players'
echo -e ''
curl -X POST -H "Content-Type: multipart/form-data" -F "name=Tony" -F "suspect=plum" 'http://localhost:8000/players'
echo -e ''
curl -X GET 'http://localhost:8000/current_player'