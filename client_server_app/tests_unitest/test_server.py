import unittest
from common.variables import RESPONSE, ERROR
from server import process_clients_message


class TestServerFunctions(unittest.TestCase):
    no_error_dict_response = {RESPONSE: 200}
    error_dict_response = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    def test_process_clients_message_no_action(self):
        self.assertEqual(process_clients_message(
            {'time': 1660370943.0685773, 'user': {'account_name': 'Guest'}}),
            self.error_dict_response)

    def test_process_clients_message_action_is_not_presence(self):
        self.assertEqual(process_clients_message(
            {'action': 'quit', 'time': 1660371373.3088787, 'user': {'account_name': 'Guest'}}),
            self.error_dict_response)

    def test_process_clients_message_no_time(self):
        self.assertEqual(process_clients_message(
            {'action': 'presence', 'user': {'account_name': 'Guest'}}), self.error_dict_response)

    def test_process_clients_message_no_user(self):
        self.assertEqual(process_clients_message(
            {'action': 'presence', 'time': 1660371373.3088787}), self.error_dict_response)

    def test_process_clients_message_user_is_not_guest(self):
        self.assertEqual(process_clients_message(
            {'action': 'presence', 'time': 1660371373.3088787, 'user': {'account_name': 'Admin'}}),
            self.error_dict_response)

    def test_process_clients_message_good_request(self):
        self.assertEqual(process_clients_message(
            {'action': 'presence', 'time': 1660371373.3088787, 'user': {'account_name': 'Guest'}}
        ), self.no_error_dict_response)
