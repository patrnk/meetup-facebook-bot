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

    @patch('meetup_facebook_bot.messenger.message_handlers.messaging.send_main_menu')
    @patch('meetup_facebook_bot.messenger.message_handlers.messaging.send_schedule')
    def test_schedule_command_handling(self, send_schedule_mock, send_main_menu_mock):
        talks_mock = [MagicMock(talk_id=1), MagicMock(talk_id=2)]
        server.db_session.query().all = MagicMock(return_value=talks_mock)
        known_input = self.generate_quick_reply('schedule payload')
        self.app.post('/', data=json.dumps(known_input), content_type='application/json')
        send_schedule_mock.assert_called_once_with(
            self.access_token,
            self.sender_id,
            talks_mock,
            server.db_session
        )
        send_main_menu_mock.assert_called_once_with(
            self.access_token,
            self.sender_id
        )

    @patch('meetup_facebook_bot.messenger.message_handlers.messaging.send_main_menu')
    @patch('meetup_facebook_bot.messenger.message_handlers.messaging.send_talk_info')
    def test_more_talk_info_command_handling(self, send_talk_info_mock, send_main_menu_mock):
        talk_mock = MagicMock()
        server.db_session.query().get = MagicMock(return_value=talk_mock)
        known_input = self.generate_postback('info talk 1')
        self.app.post('/', data=json.dumps(known_input), content_type='application/json')
        send_talk_info_mock.assert_called_once_with(
            self.access_token,
            self.sender_id,
            talk_mock
        )
        send_main_menu_mock.assert_called_once_with(
            self.access_token,
            self.sender_id
        )

    @patch('meetup_facebook_bot.messenger.message_handlers.messaging.send_main_menu')
    @patch('meetup_facebook_bot.messenger.message_handlers.messaging.send_schedule')
    def test_talk_like_command_handling(self, send_schedule_mock, send_main_menu_mock):
        liked_talk_mock = MagicMock(talk_id=1)
        liked_talk_mock.revert_like = MagicMock()
        talks_mock = [liked_talk_mock, MagicMock(talk_id=2)]
        server.db_session.query().all = MagicMock(return_value=talks_mock)
        known_input = self.generate_postback('like talk 1')
        self.app.post('/', data=json.dumps(known_input), content_type='application/json')
        liked_talk_mock.revert_like.assert_called_once_with(
            self.sender_id,
            server.db_session
        )
        send_schedule_mock.assert_called_once_with(
            self.access_token,
            self.sender_id,
            talks_mock,
            server.db_session
        )
        send_main_menu_mock.assert_called_once_with(
            self.access_token,
            self.sender_id
        )
