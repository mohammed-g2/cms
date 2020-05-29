import unittest
from flask import current_app
from app import create_app, db
from app.models import User, Role, Permission
from app.models.user import AnonymousUser


class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        current_app.config['ADMIN'] = 'admin@email.com'

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter_and_getter(self):
        u = User()
        u.password = 'pass'
        with self.assertRaises(AttributeError):
            u.password
        self.assertTrue(u.password_hash is not None)

    def test_password_verification(self):
        u = User(password='pass')
        self.assertTrue(u.check_password('pass'))
        self.assertFalse(u.check_password('pass2'))

    def test_password_salts(self):
        u1 = User(password='pass1')
        u2 = User(password='pass1')

        self.assertTrue(u1.password_hash != 'pass1')
        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_constructor_sets_roles(self):
        # create admin account
        admin = User(username='admin', email='admin@email.com')
        # create user account (default)
        user = User(username='user', email='user@email.com')

        admin_role = Role.query.filter_by(name='Admin').first()
        user_role = Role.query.filter_by(name='User').first()

        self.assertTrue(admin.role == admin_role)
        self.assertTrue(user.role == user_role)

    def test_user_roles(self):
        user = User(username='user', email='user@email.com')
        admin = User(username='admin', email='admin@email.com')
        mod = User(username='mod', email='mod@email.com')
        mod.role = Role.query.filter_by(name='Moderator').first()

        #user role
        self.assertTrue(user.can(Permission.WRITE))
        self.assertTrue(user.can(Permission.FOLLOW))
        self.assertTrue(user.can(Permission.COMMENT))
        self.assertFalse(user.can(Permission.ADMIN))
        self.assertFalse(user.can(Permission.MODERATE))
        # mod
        self.assertTrue(mod.can(Permission.WRITE))
        self.assertTrue(mod.can(Permission.FOLLOW))
        self.assertTrue(mod.can(Permission.COMMENT))
        self.assertTrue(mod.can(Permission.MODERATE))
        self.assertFalse(mod.can(Permission.ADMIN))
        # admin
        self.assertTrue(admin.can(Permission.WRITE))
        self.assertTrue(admin.can(Permission.FOLLOW))
        self.assertTrue(admin.can(Permission.COMMENT))
        self.assertTrue(admin.can(Permission.MODERATE))
        self.assertTrue(admin.can(Permission.ADMIN))

    def test_generate_token(self):
        u = User(username='user', email='email@example.com')
        db.session.add(u)
        db.session.commit()

        token1 = u.generate_token()
        token2 = u.generate_token()
        token3 = u.generate_token(name='random')

        self.assertTrue(token1 == token2)
        self.assertTrue(token1 != token3)
        self.assertTrue(token1 != {'user_id': 1})

    def test_decode_token(self):
        u = User(username='user', email='email@example.com')
        db.session.add(u)
        db.session.commit()

        token1 = u.generate_token()
        token2 = u.generate_token(name='random')

        self.assertTrue(User.decode_token(token1) == {'user_id': 1})
        self.assertTrue(User.decode_token(token2) == {'user_id': 1, 'name': 'random'})
        token2 += '.'
        self.assertIsNone(User.decode_token(token2))

    def test_token_expiration(self):
        u = User(username='user', email='email@example.com')
        db.session.add(u)
        db.session.commit()

        token = u.generate_token(expiration=-10)
        self.assertIsNone(User.decode_token(token))

    def test_confirm(self):
        u1 = User(username='name1')
        u2 = User(username='name2')
        db.session.add_all([u1, u2])
        db.session.commit()

        token1 = u1.generate_token()
        token2 = u2.generate_token()

        self.assertTrue(u1.confirm(token1))
        self.assertFalse(u2.confirm(token1))

    def test_can_and_is_admin(self):
        u1 = User(username='name1', email='admin@email.com')
        u2 = User(username='name2', email='user@email.com')
        db.session.add_all([u1, u2])
        db.session.commit()
        # test can
        self.assertTrue(u1.can(Permission.ADMIN))
        self.assertTrue(u1.can(Permission.MODERATE))
        self.assertFalse(u2.can(Permission.ADMIN))
        # test is_admin
        self.assertTrue(u1.is_admin())
        self.assertFalse(u2.is_admin())

    def test_anonymous_user(self):
        user = AnonymousUser()
        self.assertFalse(user.can(Permission.WRITE))
        self.assertFalse(user.can(Permission.FOLLOW))
        self.assertFalse(user.can(Permission.COMMENT))
        self.assertFalse(user.can(Permission.ADMIN))
        self.assertFalse(user.can(Permission.MODERATE))
