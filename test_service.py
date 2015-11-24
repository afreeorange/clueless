import requests
import os

os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

endpoint = 'http://localhost:8000/api'

p1 = requests.post('{}/players'.format(endpoint), json={"name": "Nikhil", "suspect": "scarlet"}).json().get('data').get('player_token')
p2 = requests.post('{}/players'.format(endpoint), json={"name": "Dawn", "suspect": "white"}).json().get('data').get('player_token')
p3 = requests.post('{}/players'.format(endpoint), json={"name": "Madhu", "suspect": "mustard"}).json().get('data').get('player_token')
p4 = requests.post('{}/players'.format(endpoint), json={"name": "Deepu", "suspect": "green"}).json().get('data').get('player_token')
p5 = requests.post('{}/players'.format(endpoint), json={"name": "Catherine", "suspect": "peacock"}).json().get('data').get('player_token')
p6 = requests.post('{}/players'.format(endpoint), json={"name": "Tony", "suspect": "plum"}).json().get('data').get('player_token')

players = [
    p1,
    p2,
    p3,
    p4,
    p5,
    p6,
    ]

print('\n'.join(players))

