import unittest
import re
from app import create_app, db
from app.models import User, Role


class TestAuthBlueprint(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        db.create_all()
        Role.insert_roles()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search('home page', response.get_data(as_text=True), re.IGNORECASE))

    def test_register_and_login(self):
        # register a new account
        response = self.client.post('/auth/register', data={
            'email': 'email@example.com',
            'username': 'my_username',
            'password': 123456,
            'repeat_password': 123456
        })
        self.assertEqual(response.status_code, 302)
        # login using the new account
        response = self.client.post('/auth/login', data={
            'email': 'email@example.com',
            'password': 123456
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search('my_username', response.get_data(as_text=True)))
        self.assertTrue(re.search('you have not confirmed your account yet',
            response.get_data(as_text=True), re.IGNORECASE))

        # send confirmation token
        user = User.query.filter_by(email='email@example.com').first()
        token = user.generate_token()
        response = self.client.get(f'/auth/confirm/{ token }', follow_redirects=True)
        user.confirm(token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('you have confirmed your account' in \
            response.get_data(as_text=True))
        
        # logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('you have logged out' in response.get_data(as_text=True))
        