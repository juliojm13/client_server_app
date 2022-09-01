import sys
import log.configs.server_log_config
import logging
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, USER, \
    ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import get_message, send_message
import socket
import time
import select
import json
from decorators import log

LOGGER = logging.getLogger('server_logger')


@log
def process_clients_message(message, messages_list, client):
    """
    As param we get the message from the client as a dict Python object, validates the message and returns the response
    :param client: Client from whom we received the message.
    :param messages_list: List of the messages that where sent by clients
    :param message: Client's message as a dict python object
    :return: response as a dict python object
    """

    LOGGER.info(f'Message from the client {client}: {message}')
    LOGGER.info(f'Processing from the client message: "{message}" ')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message \
            and message[USER][ACCOUNT_NAME] == 'Guest':
        LOGGER.info('The message is correct. Response 200 OK.')
        send_message({RESPONSE: 200}, client)
        return
    elif ACTION in message and message[ACTION] == MESSAGE and TIME in message \
            and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        LOGGER.info(f'Message {message[MESSAGE_TEXT]} was added to the messages queue')
        return
    LOGGER.error('Message is not correct, returning Bad Request!')
    send_message({
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }, client)


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
    LOGGER.info(
        f'Running server on port: {listen_port}, '
        f'address to connect: {listen_address}. '
        f'if there is none address, connection can be from all the addresses.')
    transport.settimeout(0.5)

    clients = []
    messages = []

    # listening port
    transport.listen(MAX_CONNECTIONS)

    while True:

        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            LOGGER.info(f'Connected with the client {client_address}')
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    message_from_client = get_message(client_with_message)
                    process_clients_message(message_from_client, messages, client_with_message)
                except:
                    LOGGER.error(f'The connection with the client {client_with_message.getpeername()} was lost ')
                    clients.remove(client_with_message)

        if messages and send_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_message(message, waiting_client)
                except:
                    LOGGER.error(f'Was not possible to send the message to the client {waiting_client}\n'
                                 f'It seems the connection was lost')
                    clients.remove(waiting_client)


if __name__ == '__main__':
    main()
