import os
import unittest
import threading
from selenium import webdriver
from app import create_app, db
from app import fake
from app.models import User, Role


class SeleniumTestCase(unittest.TestCase):
    client = None
    error = None

    @classmethod
    def setUpClass(cls):
        # make it possible to call app.run() from command line
        os.environ['FLASK_RUN_FROM_CLI'] = 'false'

        options = webdriver.ChromeOptions()
        # headless will notopen browser window
        options.add_argument('headless')
        # try to start chrome
        try:
            cls.client = webdriver.Chrome(chrome_options=options)
        except Exception as e:
            cls.error = str(e)

        # tests in this class will be skipped if browser could not be started
        if cls.client:
            # create the application
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # suppress logging for cleaner output
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel('ERROR')

            # create the database
            db.create_all()
            Role.insert_roles()
            fake.users(9) # admin with email: admin@email.com and username: admin
            fake.posts(10)

            # start flask server in a thread
            cls.server_thread = threading.Thread(target=cls.app.run,
                kwargs={
                    'debug': False
                })
            cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # stop flask server and the browser
            # because flask is running in diffrent thread, the only way
            # to shut it down is by sending http request
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.quit()
            cls.server_thread.join()

            db.drop_all()
            db.session.remove()
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest(f'web browser not available, Error { self.error }')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        # navigate to home page
        self.client.get('http://localhost:5000/')
        self.assertTrue('Home page' in self.client.page_source)

        # navigate to login page
        self.client.find_element_by_link_text('Login').click()
        self.assertTrue('<h1>Login</h1>' in self.client.page_source)

        # login
        self.client.find_element_by_name('email').send_keys('admin@email.com')
        self.client.find_element_by_name('password').send_keys('123456')
        self.client.find_element_by_name('submit').click()
        self.assertTrue('admin' in self.client.page_source)

        # navigate to user profile page
        self.client.find_element_by_link_text('Profile').click()
        self.assertTrue('<h1>admin</h1>' in self.client.page_source)