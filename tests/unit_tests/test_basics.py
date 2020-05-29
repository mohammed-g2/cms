import unittest
from flask import current_app
from app import create_app, db, mail
from app.util import send_email


class TestBasics(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertTrue(current_app is not None)

    def test_app_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_send_email(self):
        with mail.record_messages() as outbox:
            send_email(['admin@email.com'],
                'test',
                'email/test-email',
                value='test value')
        
        self.assertTrue(len(outbox) == 1)
        self.assertTrue(current_app.config['MAIL_SUBJECT_PREFIX'] + 'test' == outbox[0].subject)
        self.assertTrue('this is a test email' in outbox[0].body.lower())
        self.assertTrue('this is a test email' in outbox[0].html.lower())

        self.assertTrue('test value' in outbox[0].html)
        self.assertTrue('test value' in outbox[0].html)
    