import socketio
import requests
from text_to_speech import tts


def get_token():
    with open('token', 'r') as f:
        return f.read()


def get_jwt(token):
    return requests.post('https://wasd.tv/api/auth/chat-token', headers={
        'Authorization': 'Token ' + token
    }).json()["result"]


def get_streamer_meta(alias):
    url = "https://wasd.tv/api/v2/broadcasts/public?channel_name=%s" % alias
    info = requests.get(url).json()
    return info


def get_channel_id(info):
    return info['result']['channel']['channel_id']


def stream_is_live(info):
    return info['result']['channel']['channel_is_live']


def get_stream_id(info):
    return info['result']['media_container']['media_container_streams'][0]['stream_id'] if stream_is_live(info) else 0


class WASD:

    token = get_token()
    jwt = get_jwt(token)

    def __init__(self, alias):

        self.sio = socketio.Client()

        @self.sio.event
        def connect():
            print('Yes. Connected.')

        @self.sio.event
        def connect_error(data):
            print('Connection failed')
            print(data)

        @self.sio.event
        def joined(data):
            print(data)

        @self.sio.event
        def disconnect():
            print('Disconnected')

        @self.sio.event
        def error(data):
            print(data)

        @self.sio.event
        def message(data):
            print("|{}| {} : {}".format(data['date_time'], data['user_login'], data['message']))
            tts("{} сказал: {}".format(data['user_login'], data['message']))

        @self.sio.event
        def event(data):
            print(data)

        self.alias = alias
        self.meta = get_streamer_meta(self.alias)
        self.channel_id = get_channel_id(self.meta)
        self.stream_id = get_stream_id(self.meta)
        self.live = stream_is_live(self.meta)

    def run(self):

        self.sio.connect('wss://chat.wasd.tv')

        self.sio.emit('join',
                      {
                          "streamId": self.stream_id,
                          "channelId": self.channel_id,
                          "jwt": self.jwt,
                          "excludeStickers": False
                      }
                      )

    def kill(self):
        self.sio.disconnect()
