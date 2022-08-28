import unittest
from common.variables import RESPONSE, ERROR, ACTION, TIME, USER, ACCOUNT_NAME
from client import create_presence, process_response


class TestClientFunctions(unittest.TestCase):
    no_error_dict_response = {RESPONSE: 200}
    error_dict_response = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }
    good_processed_response = '200 : OK'
    processed_response_bad_request = f'400: {error_dict_response[ERROR]}'

    def test_process_response_good_request(self):
        self.assertEqual(process_response(self.no_error_dict_response),
                         self.good_processed_response)

    def test_process_response_bad_request(self):
        self.assertEqual(process_response(self.error_dict_response),
                         self.processed_response_bad_request)

    def test_create_presence_object(self):
        self.assertIsInstance(create_presence(), dict)

    def test_create_presence_name(self):
        self.assertEqual(create_presence('Admin')['user']['account_name'], 'Admin')

    def test_create_presence_action(self):
        self.assertEqual(create_presence()['action'], 'presence')

    def test_create_presence_action_in_message(self):
        self.assertIn(ACTION, create_presence())

    def test_create_presence_time_in_message(self):
        self.assertIn(TIME, create_presence())

    def test_create_presence_user_in_message(self):
        self.assertIn(USER, create_presence())

    def test_create_presence_name_in_message(self):
        self.assertIn(ACCOUNT_NAME, create_presence()[USER])
