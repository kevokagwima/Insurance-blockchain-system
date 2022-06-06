from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

app = Flask(__name__)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model, UserMixin):
  __tablename__ = 'members'
  id = db.Column(db.Integer(), primary_key=True)
  unique_id = db.Column(db.Integer(), nullable=False, unique=True)
  first_name = db.Column(db.String(30), nullable=False)
  last_name = db.Column(db.String(30), nullable=False)
  age = db.Column(db.Integer(), nullable=False)
  phone_number = db.Column(db.String(10), nullable=False)
  email = db.Column(db.String(50), nullable=False)
  password = db.Column(db.String(100), nullable=False)
  session = db.relationship("Session", backref="session", lazy=True)
  questions = db.relationship("Questions", backref="user-questions", lazy=True)

  @property
  def passwords(self):
    return self.passwords

  @passwords.setter
  def passwords(self, plain_text_password):
    self.password = bcrypt.generate_password_hash(plain_text_password).decode("utf-8")

  def check_password_correction(self, attempted_password):
    return bcrypt.check_password_hash(self.password, attempted_password)

class Major_Insurance(db.Model):
  __tablename__ = 'Major_insurance'
  id = db.Column(db.Integer(), primary_key=True)
  unique_id = db.Column(db.Integer(), nullable=False, unique=True)
  name = db.Column(db.String(30), nullable=False, unique=True)
  insurance_cover = db.relationship("Insurance_covers", backref="sub-category", lazy=True)
  session = db.relationship("Session", backref="major_session", lazy=True)

class Insurance_covers(db.Model):
  __tablename__ = 'Insurance_cover'
  id = db.Column(db.Integer(), primary_key=True)
  unique_id = db.Column(db.Integer(), nullable=False, unique=True)
  name = db.Column(db.String(30), nullable=False, unique=True)
  category = db.Column(db.String(10), nullable=False)
  cost = db.Column(db.Integer(), nullable=False)
  avg_score = db.Column(db.Integer(), nullable=False)
  major_category = db.Column(db.Integer(), db.ForeignKey('Major_insurance.id'))
  session = db.relationship("Session", backref="session_cover", lazy=True)

class Session(db.Model):
  __tablename__ = 'Session'
  id = db.Column(db.Integer(), primary_key=True)
  session_id = db.Column(db.Integer(), nullable=False, unique=True)
  start_date = db.Column(db.DateTime(), nullable=False)
  end_date = db.Column(db.DateTime())
  status = db.Column(db.String(10), nullable=False)
  user = db.Column(db.Integer(), db.ForeignKey('members.id'))
  major_insurance = db.Column(db.Integer(), db.ForeignKey('Major_insurance.id'))
  insurance_cover = db.Column(db.Integer(), db.ForeignKey('Insurance_cover.id'))
  questions = db.relationship("Questions", backref="session-questions", lazy=True)

class Questions(db.Model):
  __tablename__ = 'questions'
  id = db.Column(db.Integer(), primary_key=True)
  unique_id = db.Column(db.Integer(), nullable=False, unique=True)
  name = db.Column(db.String(3), nullable=False, unique=True)
  point = db.Column(db.Integer(), nullable=False, default=0)
  Hash = db.Column(db.String(), nullable=False)
  user = db.Column(db.Integer(), db.ForeignKey('members.id'))
  session = db.Column(db.Integer(), db.ForeignKey('Session.id'))