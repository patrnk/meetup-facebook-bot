import os
import tempfile
import unittest

import sqlalchemy

from app import app
from app import models
from app import database


class SpeakerTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_name = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % self.db_name
        database.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_name)
        database.session.remove()
        database.drop_all()

    def test_valid_speaker_without_talks(self):
        speaker = models.Speaker(facebook_id=1, name='John Doe (Qweqwe, inc.)')
        database.session.add(speaker)
        database.session.commit()

        returned_speaker = models.Speaker.query.get(1)
        self.assertEqual(len(returned_speaker.talks.all()), 0)
        self.assertEqual(returned_speaker.facebook_id, speaker.facebook_id)
        self.assertEqual(returned_speaker.name, speaker.name)

    def test_invalid_speaker_without_name(self):
        speaker = models.Speaker(facebook_id=1)
        database.session.add(speaker)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            database.session.commit()

    def test_invalid_speaker_without_facebook_id(self):
        speaker = models.Speaker(name='John Doe (Qweqwe, inc.)')
        database.session.add(speaker)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            database.session.commit()

    

if __name__ == '__main__':
    unittest.main()