from . import db
import time

# TODO implement private accounts
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    date_registered = db.Column(db.Integer, default=time.time())
    last_login = db.Column(db.Integer, default=time.time())
    verified = db.Column(db.Boolean, default=False)
    notifications = db.Column(db.String(), default="[]")
    verification_process = db.relationship('VerificationCode', backref='requester'
                                           , lazy=True, uselist=False, cascade="all, delete-orphan")
    data_restoration = db.relationship('DataRestoration', backref='requester'
                                       , lazy=True, uselist=False, cascade="all, delete-orphan")
    subscribed_vaults = db.relationship('Vault', secondary='vault_subscription', backref='subscribed_vaults', viewonly=True)

    # exams_results = db.relationship('ExamResults', backref='subscribed_exams'
    #                                    , lazy=True, uselist=True, cascade="all, delete-orphan")



# class Notification(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=False)
#     from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=False)
#     type = db.Column(db.String(40), default="", nullable=False)
#     message = db.Column(db.String(120), default="", nullable=False)
#     post_id = db.Column(db.Integer)


class VerificationCode(db.Model):
    verification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email_code = db.Column(db.String(128), nullable=False)
    time_stamp = db.Column(db.Integer, default=time.time())


class DataRestoration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restoration_link = db.Column(db.String(), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    code = db.Column(db.String(128), nullable=False)
    data_to_restore = db.Column(db.Integer, nullable=False)
    time_stamp = db.Column(db.Integer, default=time.time())


class Vault(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  vault_name = db.Column(db.String(50), nullable=False)
  creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  creator_name = db.Column(db.String(80), nullable=False)
  exams = db.relationship('Exams', backref='vault', lazy=True, uselist=True, cascade="all, delete-orphan")
  subscribers = db.relationship('User', secondary='vault_subscription', backref='subscribers', viewonly=True)
  subscribers_count = db.Column(db.Integer, default=0)



class VaultSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vault_id = db.Column(db.Integer, db.ForeignKey('vault.id'), nullable=False)
    subscribed_on = db.Column(db.DateTime, default=db.func.current_timestamp())


class Exams(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  exam_name = db.Column(db.String(50), nullable=False)
  exam_date = db.Column(db.String(12), nullable=False)
  exam_notes = db.Column(db.String(2000), nullable=True)
  exam_links = db.Column(db.String(1000), nullable=True)
  vault_id = db.Column(db.Integer, db.ForeignKey('vault.id'), nullable=False)

class ExamResults(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
  owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  grade_goal = db.Column(db.Integer, nullable=True)
  exam_passed = db.Column(db.Boolean, default=False)
