from unittest import TestCase
from unittest.mock import MagicMock

import vcr

from meetup_facebook_bot.messenger import messaging


class MessagingTestCase(TestCase):
    def create_mockup_talk(self):
        talk_mock = MagicMock(id=1, title=1, speaker_facebook_id=1)
        talk_mock.is_liked_by = MagicMock(return_value=False)
        return talk_mock

    def generate_mockup_talks(self):
        talk_mocks = []
        for talk_id in range(1, 6):
            mock_talk_title = str(talk_id - 1)
            talk_mock = MagicMock(id=talk_id, title=mock_talk_title, speaker_facebook_id=1)
            talk_mock.count_likes = MagicMock(return_value=0)
            talk_mock.is_liked_by = MagicMock(return_value=False)
            talk_mock.ask_question_url = None
            talk_mocks.append(talk_mock)
        return talk_mocks

    def create_mockup_talk_with_speaker(self):
        speaker_mock = MagicMock()
        speaker_mock.name = '1'
        talk_mock = MagicMock(title='1', speaker=speaker_mock, description=None)
        return talk_mock

    def setUp(self):
        self.access_token = '1'
        self.user_id = '474276666029691'

    def test_send_schedule(self):
        talks = self.generate_mockup_talks()
        talk_like_numbers = {talk.id: 0 for talk in talks}
        liked_talk_ids = []
        with vcr.use_cassette('vcr_cassettes/send_schedule.yaml'):
            response = messaging.send_schedule(
                self.access_token,
                self.user_id,
                talks,
                talk_like_numbers,
                liked_talk_ids
            )
        self.assertTrue('recipient_id' in response)
        self.assertTrue('message_id' in response)
        self.assertEqual(response['recipient_id'], self.user_id)

    def test_send_talk_info(self):
        talk = self.create_mockup_talk_with_speaker()
        with vcr.use_cassette('vcr_cassettes/send_more_talk_info.yaml'):
            response = messaging.send_talk_info(self.access_token, self.user_id, talk)
        self.assertTrue('recipient_id' in response)
        self.assertTrue('message_id' in response)
        self.assertEqual(response['recipient_id'], self.user_id)

    def test_send_rate_menu(self):
        talk = self.create_mockup_talk()
        talk_liked = False
        with vcr.use_cassette('vcr_cassettes/send_rate_menu.yaml'):
            response = messaging.send_rate_menu(self.access_token, self.user_id, talk, talk_liked)
        self.assertTrue('recipient_id' in response)
        self.assertTrue('message_id' in response)
        self.assertEqual(response['recipient_id'], self.user_id)

