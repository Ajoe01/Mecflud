# utils/auth.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, LoginManager

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    lock_Q = db.Column(db.Integer, default=0, nullable=False)  # 0 = puede responder, 1 = bloqueado

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
