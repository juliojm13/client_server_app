import sys
import log.configs.server_log_config
import logging
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, USER, \
    ACCOUNT_NAME, RESPONSE, ERROR
from common.utils import get_message, send_message
import socket
import json

LOGGER = logging.getLogger('server_logger')


def process_clients_message(message):
    """
    As param we get the message from the client as a dict Python object, validates the message and returns the response
    :param message: Client's message as a dict python object
    :return: response as a dict python object
    """
    LOGGER.info(f'Processing from the client message: "{message}" ')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message \
            and message[USER][ACCOUNT_NAME] == 'Guest':
        LOGGER.info('The message is correct. Response 200 OK.')
        return {RESPONSE: 200}
    LOGGER.error('Message is not correct, returning Bad Request!')
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


def main():
    """
    Function to run the server socket, getting the params from the command line, if there are not params, we give
    default variables
    Example for the command line:
    server.py -p 6565 -a 192.168.0.104
    """
    # Block for getting the port number from the command line
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        LOGGER.error('After the parameter -\'p\' must be the port number! ')
        sys.exit(1)
    except ValueError:
        LOGGER.error('The number of the port must be in the diapason from 1024 to 65535! ')
        sys.exit(1)

    # Block for getting the host number from the command line
    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        LOGGER.error('After the parameter -\'a\' must be the host number, that will listen the server! ')
        sys.exit(1)

    # Getting the socket ready
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))

    # listening port
    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        try:
            message_from_client = get_message(client)
            LOGGER.info(f'Message from the client {client}: {message_from_client}')
            response = process_clients_message(message_from_client)
            send_message(response, client)
            client.close()
        except (ValueError, json.JSONDecodeError):
            LOGGER.error('Was received a not correct message from the client! ')
            client.close()


if __name__ == '__main__':
    main()
