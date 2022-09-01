from common.variables import MAX_PACKAGE_LENGTH, ENCODING
import json
from decorators import log


@log
def get_message(socket):
    """
    The function gets the message sent by the socket and decodes it from bytes to dict. If got something else instead
    of json,raise ValueError.
    :param socket: socket object from who we got the message
    :return: message: returns the message as a python dict object
    """
    encoded_message = socket.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_message, bytes):
        json_message = encoded_message.decode(encoding=ENCODING)
        message = json.loads(json_message)
        if isinstance(message, dict):
            return message
        raise ValueError
    raise ValueError


@log
def send_message(message, socket):
    """
    The function gets as param the message that we want to send as a python dict object and the socket that will receive
    the message, encodes it and sends it to the socket as bytes.
    :param message: Python dict object, message that we want to send.
    :param socket: Socket object, who will receive the message
    """
    if isinstance(message, dict):
        json_message = json.dumps(message)
        encoded_message = json_message.encode(encoding=ENCODING)
        socket.send(encoded_message)
    else:
        raise ValueError
