from flask import Blueprint, request, jsonify
from ..models import User, VerificationCode, DataRestoration
from ..utils import helper as h
from .. import db, jwt, limiter
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
import random
import time

auth_bp = Blueprint('auth', __name__)

jwt_blocklist = set()


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    return jti in jwt_blocklist


@auth_bp.route('register', methods=['POST'])
def register_user():
    data = request.get_json(force=True)
    email = data.get('email').lower()
    username = data.get('username')
    password = data.get('password')
    exists = []
    email_exists = User.query.filter_by(email=email).first()
    username_exists = User.query.filter_by(username=username).first()
    if email_exists: exists.append('email')
    if username_exists: exists.append('username')
    if len(exists) > 0: return jsonify({'message': f'{exists} already exists!'}), 409
    hashed_password = h.hash_password(password)
    user = User(email=email, username=username, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'You have been registered successfully'}), 201


@auth_bp.route('send-code', methods=['POST'])
def send_codes():
    data = request.get_json()
    username = data.get('username')
    user = User.query.filter_by(username=username).first()

    if not user: return jsonify({'message': 'Bad request, no such user!'}), 400

    if user.verified:
        return jsonify({'message': 'User is verified.'}), 401

    if user.verification_process:
        if h.time_difference(user.verification_process.time_stamp) < 120:
            return jsonify({'message': 'Codes have been already sent'}), 400
        else:
            db.session.delete(user.verification_process)
            db.session.commit()

    email_code = random.randint(100000, 999999)

    h.send_email_verification_code(user.email, email_code, user.username)

    email_code = h.hash_password(str(email_code))
    verification_codes = VerificationCode(user_id=user.id, username=user.username, email_code=email_code)
    db.session.add(verification_codes)
    db.session.commit()
    return jsonify({'message': 'Codes have been sent successfully'}), 200


@auth_bp.route('verify-email', methods=['POST'])
def verify():
    data = request.get_json()
    username = data.get('username')
    email_code = data.get('email_code')
    user = User.query.filter_by(username=username).first()
    if not user: return jsonify({'message': 'Bad request, no such user!'}), 400
    if user.verification_process:
        print(h.time_difference(user.verification_process.time_stamp))
        # Codes are still valid
        if h.time_difference(user.verification_process.time_stamp) < 600:
            db_email_code = user.verification_process.email_code
            if h.check_password(db_email_code, str(email_code)):
                access_token = create_access_token(identity={
                    'username': user.username,
                    'user_id': user.id
                })
                user.verified = True
                db.session.delete(user.verification_process)
                db.session.commit()
                return jsonify({'message': access_token}), 200
            else:
                return jsonify({'message': 'Invalid credentials'}), 401
        # Codes are invalid, 10 minutes passed
        else:
            db.session.delete(user.verification_process)
            db.session.commit()
            return jsonify({'message': 'Your code have expired, please request new!'}), 400
    else:
        if user.verified:
            return jsonify({'message': 'User is verified'}), 400
        else:
            return jsonify({'message': 'Your codes have expired, please request new!'}), 400


@auth_bp.route('authenticate', methods=['GET'])
@jwt_required()
def authenticate():
    return jsonify({'message': get_jwt_identity()}), 200


@auth_bp.route('logout', methods=['GET'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_blocklist.add(jti)
    return jsonify({'message': 'You have been logged out successfully'}), 200


@auth_bp.route('login', methods=["POST"])
@limiter.limit("5 per minute")
def login():
    time.sleep(3)
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if not user: return jsonify({'message': 'Invalid credentials'}), 401
    if h.check_password(user.password, password):
        if not user.verified:
            return jsonify({'message': 'not verified'}), 401
        user.last_login = time.time()
        db.session.commit()
        return jsonify({'message': create_access_token(
            {
                'username': username,
                'user_id': user.id
            }
        )}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


@auth_bp.route('forgot-cred', methods=['POST'])
def forgot_cred():
    data = request.get_json()
    cred = data.get('email')


    user = User.query.filter_by(email=cred).first()

    if not user:
        return jsonify({'message': 'No users matched this data'}), 400
    elif not user.verified:
        return jsonify({'message': 'User is not verified, please verify first!'}), 401
    data_to_restore = 0
    if data.get('username') and data.get('password'):
      data_to_restore = 3
    elif data.get('password'):
      data_to_restore = 2

    if user.data_restoration:
        if h.time_difference(user.data_restoration.time_stamp) > 120 \
                or user.data_restoration.data_to_restore != data_to_restore:
            db.session.delete(user.data_restoration)
            db.session.commit()
        else:
            return jsonify({'message': 'Code already been sent, try again in two minutes!'}), 400

    link = str(random.randint(0, 100000000000))
    link = f'{link}b' if data_to_restore == 3 else f'{link}p' if data_to_restore == 2 else link
    code = random.randint(100000, 999999)

    h.send_email_verification_code(cred, code, link, 1)

    code = h.hash_password(str(code))
    restoration = DataRestoration(restoration_link=link, user_id=user.id,
                                  username=user.username, code=code, data_to_restore=data_to_restore)
    db.session.add(restoration)
    db.session.commit()
    return jsonify({'message': link}), 200


@auth_bp.route('restore-cred', methods=['POST'])
def restore_cred():
    data = request.get_json()
    code = data.get('code')
    new_password = data.get('password')
    restoration_link = data.get('id')
    restoration = DataRestoration.query.filter_by(restoration_link=restoration_link).first()

    if not restoration:
        return jsonify({'message': 'Bad request!'}), 400
    if h.time_difference(restoration.time_stamp) > 600:
        db.session.delete(restoration)
        db.session.commit()
        return jsonify({'message': 'Your codes have expired, please request new!'}), 400
    if h.check_password(restoration.code, str(code)):
        user = restoration.requester
        db.session.delete(restoration)
        db.session.commit()
        if restoration.data_to_restore == 3:
            user.password = h.hash_password(new_password)
            db.session.commit()
            return jsonify({'message': f'Your username is: <strong>{user.username}</strong><br>You have successfully restored your '
                                       f'password!'}), 200
        elif restoration.data_to_restore == 2:
            user.password = h.hash_password(new_password)
            db.session.commit()
            return jsonify({'message': f'You have successfully restored your password!'}), 200
        else:
            return jsonify({'message': f'Your username is: <strong>{user.username}</strong>'}), 200
    else:
        return jsonify({'message': 'You have entered wrong code!'}), 400
