from app import db

"""
    user roles:
    User -       permissions: FOLLOW, COMMENT, WRITE
    Moderator -  permissions: FOLLOW, COMMENT, WRITE, MODERATE
    Admin -      permissions: FOLLOW, COMMENT, WRITE, MODERATE, ADMIN
"""

class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


roles = {
    'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
    'Moderator': [Permission.FOLLOW, Permission.COMMENT, 
        Permission.WRITE, Permission.MODERATE],
    'Admin': [Permission.FOLLOW, Permission.COMMENT, 
        Permission.WRITE, Permission.MODERATE, Permission.ADMIN]
}


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, permission: int):
        if not self.has_permission(permission):
            self.permissions += permission

    def remove_permission(self, permission: int):
        if self.has_permission(permission):
            self.permissions -= permission
    
    def has_permission(self, permission: int) -> bool:
        return self.permissions & permission == permission

    def reset_permissions(self):
        self.permissions = 0

    @staticmethod
    def insert_roles():
        """existing roles are updated with new permissions"""
        default_role = 'User'

        for role_name, permissions in roles.items():
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
            
            role.default = (role.name == default_role)
            role.reset_permissions()

            for permission in permissions:
                role.add_permission(permission)
            
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return f'<Role {self.name}>'
