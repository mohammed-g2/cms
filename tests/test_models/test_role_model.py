import unittest
from app import create_app, db
from app.models import User, Role, Permission


class TestRoleModel(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_insert_roles(self):
        Role.insert_roles()
        admin_role = Role.query.filter_by(name='Admin').first()
        mod_role = Role.query.filter_by(name='Moderator').first()
        user_role = Role.query.filter_by(name='User').first()

        self.assertIsNotNone(admin_role)
        self.assertIsNotNone(mod_role)
        self.assertIsNotNone(user_role)
        # default role
        self.assertTrue(user_role.default)
        self.assertFalse(admin_role.default)
        self.assertFalse(mod_role.default)

    def test_has_permission(self):
        Role.insert_roles()
        admin_role = Role.query.filter_by(name='Admin').first()
        mod_role = Role.query.filter_by(name='Moderator').first()
        user_role = Role.query.filter_by(name='User').first()

        self.assertTrue(admin_role.has_permission(Permission.ADMIN))
        self.assertTrue(mod_role.has_permission(Permission.MODERATE))
        self.assertTrue(user_role.has_permission(Permission.WRITE))

        self.assertFalse(user_role.has_permission(Permission.ADMIN))
        self.assertFalse(user_role.has_permission(Permission.MODERATE))

    def test_add_permission(self):
        Role.insert_roles()
        user_role = Role.query.filter_by(name='User').first()
        self.assertFalse(user_role.has_permission(Permission.MODERATE))
        user_role.add_permission(Permission.MODERATE)
        self.assertTrue(user_role.has_permission(Permission.MODERATE))


    def test_remove_permission(self):
        Role.insert_roles()
        user_role = Role.query.filter_by(name='User').first()
        self.assertTrue(user_role.has_permission(Permission.WRITE))
        user_role.remove_permission(Permission.WRITE)
        self.assertFalse(user_role.has_permission(Permission.WRITE))

    def test_reset_permission(self):
        Role.insert_roles()
        user_role = Role.query.filter_by(name='User').first()
        self.assertTrue(user_role.has_permission(Permission.WRITE))
        self.assertTrue(user_role.has_permission(Permission.FOLLOW))
        self.assertTrue(user_role.has_permission(Permission.COMMENT))

        user_role.reset_permissions()

        self.assertFalse(user_role.has_permission(Permission.WRITE))
        self.assertFalse(user_role.has_permission(Permission.FOLLOW))
        self.assertFalse(user_role.has_permission(Permission.COMMENT))
