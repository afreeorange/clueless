import logging

class SocketIOLoggingHandler(logging.Handler):

    def __init__(self, socket_io_object, channel):
        super(SocketIOLoggingHandler, self).__init__()
        self.socket_io_object = socket_io_object
        self.channel = channel

    def emit(self, record):
        self.socket_io_object.emit(self.channel, {
                'data': {
                    'timestamp': str(arrow.now()),
                    'level': record.levelname,
                    'message': record.msg,
                }
            })


class JSONHandler(logging.Handler):

    def __init__(self, json_object=[]):
        super(JSONHandler, self).__init__()
        self.json_object = json_object

    def emit(self, record):
        self.json_object.append({
                'timestamp': str(arrow.now()),
                'level': record.levelname,
                'message': record.msg,
            })
