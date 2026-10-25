"""
Shared extension instances. Import these from here everywhere (models.py,
auth.py, teammates' future blueprints) rather than instantiating a second
SQLAlchemy() — a second instance would not see these models.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()
