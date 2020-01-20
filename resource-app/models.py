from main import db
from datetime import datetime
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True)
    birthday = db.Column(db.String(64))
    image = db.Column(db.String(500))
    campus = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean, default=False)
    tokenn = db.Column(db.String(500), index=True, unique=True)
    secret_key = db.Column(db.String(100))

    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('role'))

    def is_admin(self):
        if self.userRoles_set.filter(user_id=self.id, role_id=1).exists():
            #UserRoles.query.filter_by(user_id=self.id, role_id=1).exists()
            #self.query.filter(User.roles.any(name="Admin")).all()
            return True
        return False

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


# Setup Flask-User
#db_adapter = SQLAlchemyAdapter(db, User)
#user_manager = UserManager(db_adapter, app)