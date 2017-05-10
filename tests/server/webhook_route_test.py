import json
from unittest import TestCase
from unittest.mock import patch, MagicMock

from meetup_facebook_bot import server


class WebhookRouteTestCase(TestCase):
    def setUp(self):
        self.access_token = 1
        self.sender_id = 'USER_ID'

        server.app.config['ACCESS_TOKEN'] = self.access_token
        self.app = server.app.test_client()
        server.engine = MagicMock()
        server.Session = MagicMock()
        server.db_session = MagicMock()

    def generate_facebook_request(self, message_kind, message):
        facebook_request = {
            'object': 'page',
            'entry': [
                {
                    'messaging': [
                        {
                            'sender': {
                                'id': self.sender_id
                            },
                            message_kind: message
                        }
                    ]
                }
            ]
        }
        return facebook_request

    def generate_quick_reply(self, payload):
        message = {
            'text': 'Doesn\'t matter',
            'quick_reply': {
                'payload': payload
            }
        }
        return self.generate_facebook_request('message', message)

    def generate_postback(self, payload):
        message = {
            'payload': payload
        }
        return self.generate_facebook_request('postback', message)

    def generate_simple_text_message(self):
        message = {
            'text': 'Doesn\'t matter'
        }
        return self.generate_facebook_request('message', message)

    @patch('meetup_facebook_bot.server.message_handlers')
    def test_schedule_command_handling(self, message_handlers_mock):
        message_handlers_mock.handle_speaker_auth = MagicMock()
        talks_mock = [MagicMock(talk_id=1), MagicMock(talk_id=2)]
        server.db_session.query().all = MagicMock(return_value=talks_mock)
        known_input = self.generate_quick_reply('schedule payload')
        self.app.post('/', data=json.dumps(known_input), content_type='application/json')
        number_of_calls = message_handlers_mock.handle_speaker_auth.call_count
        self.assertEqual(number_of_calls, 1)


    @patch('meetup_facebook_bot.messenger.message_handlers.messaging.send_talk_info')
    def test_more_talk_info_command_handling(self, send_talk_info_mock):
        talk_mock = MagicMock()
        server.db_session.query().get = MagicMock(return_value=talk_mock)
        known_input = self.generate_postback('info talk 1')
        self.app.post('/', data=json.dumps(known_input), content_type='application/json')
        send_talk_info_mock.assert_called_once_with(
            self.access_token,
            self.sender_id,
            talk_mock
        )

    @patch('meetup_facebook_bot.messenger.message_handlers.Talk')
    def test_talk_like_command_handling(self, talk_class_mock):
        talk_mock = MagicMock(talk_id=1)
        talk_mock.revert_like = MagicMock()
        server.db_session.query(talk_class_mock).get = MagicMock(return_value=talk_mock)
        known_input = self.generate_quick_reply('like talk 1')
        self.app.post('/', data=json.dumps(known_input), content_type='application/json')
        talk_mock.revert_like.assert_called_once_with(
            self.sender_id,
            server.db_session
        )

    @patch('meetup_facebook_bot.server.message_handlers')
    def test_speaker_auth_gets_called(self, message_handlers_mock):
        message_handlers_mock.handle_speaker_auth = MagicMock()
        message_handlers_mock.handle_speaker_auth = MagicMock()
        known_input = self.generate_simple_text_message()
        self.app.post('/', data=json.dumps(known_input), content_type='application/json')
        number_of_calls = message_handlers_mock.handle_speaker_auth.call_count
        self.assertEqual(number_of_calls, 1)
