import json
import time

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Vault, VaultSubscription, Exams, ExamResults
from .. import db


vaults_bp = Blueprint('vaults', __name__)


@vaults_bp.route('new', methods=['POST'])
@jwt_required()
def new_vault():
    data = request.get_json()
    vault_name = data.get('vaultName')
    exams = data.get('exams')
    user_id = get_jwt_identity()['user_id']
    username = get_jwt_identity()['username']


    if not vault_name or not exams or len(exams) == 0:
        return jsonify({'message': 'Bad request, missing vaultName or exams!'}), 400

    vault = Vault(vault_name=vault_name, creator_id=user_id, creator_name=username)

    try:
        db.session.add(vault)
        db.session.flush()

        for exam in exams:
            exam_name = exam.get('examName')
            exam_date = exam.get('examDate')
            if not exam_name or not exam_date:
                raise ValueError('Bad request, missing examName or examDate')

            new_exam = Exams(exam_name=exam_name, exam_date=exam_date,
                             exam_notes=exam.get('examNotes'), exam_links=json.dumps(exam.get('examLinks')), vault_id=vault.id)
            db.session.add(new_exam)
        db.session.commit()
        return jsonify({'message': 'Vault and exams added successfully'}), 201
    except ValueError as ve:
        db.session.rollback()
        print("MISSING VALUES")
        return jsonify({'message': str(ve)}), 400

    except Exception as e:
        db.session.rollback()
        print("EXCEPTION!", e)

        return jsonify({'message': 'An error occurred while adding the vault and exams', 'error': str(e)}), 500

@vaults_bp.route('/<int:vault_id>', methods=['GET'])
@jwt_required()
def get_vault(vault_id):
    # Retrieve the vault by ID
    vault = Vault.query.filter_by(id=vault_id).first()

    # Handle case where vault does not exist
    if not vault:
        return jsonify({'message': 'Vault not found'}), 404

    user_id = get_jwt_identity()['user_id']
    is_subscribed = VaultSubscription.query.filter_by(user_id=user_id, vault_id=vault_id).first()
    # Serialize vault data into a dictionary
    vault_data = {
        'vaultId': vault.id,
        'vaultName': vault.vault_name,
        'creatorId': vault.creator_id,
        'creatorName': vault.creator_name,
        'creator': vault.creator_id == user_id,
        'subscribed': bool(is_subscribed),
        'exams': [
            {
                'examId': exam.id,
                'examVaultId': vault.id,
                'examName': exam.exam_name,
                'examDate': exam.exam_date,
                'examNotes': exam.exam_notes,
                'examLinks': json.loads(exam.exam_links)
            } for exam in vault.exams
        ]
    }

    return jsonify({'vault': vault_data}), 200


@vaults_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_vaults():
  user_id = get_jwt_identity().get('user_id')
  username = get_jwt_identity().get('username')

  created_vaults = Vault.query.filter_by(creator_id=user_id).all()
  subscribed_vaults = Vault.query.join(VaultSubscription, Vault.id == VaultSubscription.vault_id) \
                                        .filter(VaultSubscription.user_id == user_id).all()

  response_data = {
    'created_vaults': [{'vaultId': vault.id,
        'vaultName': vault.vault_name,
        'creatorId': user_id,
        'creatorName': username,
        'creator': True,
        'subscribed': False,
        'exams': [
            {
                'examId': exam.id,
                'examVaultId': vault.id,
                'examName': exam.exam_name,
                'examDate': exam.exam_date,
                'examNotes': exam.exam_notes,
                'examLinks': json.loads(exam.exam_links)
            } for exam in vault.exams
        ]} for vault in created_vaults],

    'subscribed_vaults': [{'vaultId': vault.id,
        'vaultName': vault.vault_name,
        'creatorId': vault.creator_id,
        'creatorName': vault.creator_name,
        'creator': False,
        'subscribed': True,
        'exams': [
            {
                'examId': exam.id,
                'examVaultId': vault.id,
                'examName': exam.exam_name,
                'examDate': exam.exam_date,
                'examNotes': exam.exam_notes,
                'examLinks': json.loads(exam.exam_links)
            } for exam in vault.exams
        ]} for vault in subscribed_vaults]
  }

  return jsonify({'message': response_data}), 200



@vaults_bp.route('/search', methods=['POST'])
@jwt_required()
def search_vaults():
  data = request.get_json()
  vault_name = data.get('searchInput', '')
  if vault_name == '':
    return jsonify({'message': 'Bad request, no search input provided!'}), 400
  page = int(data.get('page', 1))
  user_id = get_jwt_identity()['user_id']
  offset = (page - 1) * 20

  vaults = Vault.query.filter(Vault.vault_name.ilike(f"%{vault_name}%"), Vault.creator_id != user_id).limit(20).offset(offset).all()

  vaults = [{'vaultId': vault.id,
        'vaultName': vault.vault_name,
        'creatorId': vault.creator_id,
        'creatorName': vault.creator_name,
        'creator': False,
        'subscribed': any(sub.id == user_id for sub in vault.subscribers),
        'exams': [
            {
                'examId': exam.id,
                'examVaultId': vault.id,
                'examName': exam.exam_name,
                'examDate': exam.exam_date,
                'examNotes': exam.exam_notes,
                'examLinks': json.loads(exam.exam_links)
            } for exam in vault.exams
        ]} for vault in vaults]

  return jsonify({'message': vaults}), 200


@vaults_bp.route('/<int:vault_id>', methods=['DELETE'])
@jwt_required()
def delete_vault(vault_id):
  user_id = get_jwt_identity()['user_id']

  if not vault_id:
    return jsonify({'message': 'Vault ID is required!'}), 400

  vault = Vault.query.filter_by(id=vault_id, creator_id=user_id).first()

  if not vault:
    return jsonify({'message': 'No such vault!'}), 400

  db.session.delete(vault)
  db.session.commit()

  return jsonify({'message': 'Success', 'vault_name': vault.vault_name}), 200

@vaults_bp.route('/<int:vault_id>/<int:exam_id>', methods=['DELETE'])
@jwt_required()
def delete_exam(vault_id, exam_id):
  user_id = get_jwt_identity()['user_id']

  if not vault_id or not exam_id:
    return jsonify({'message': "Missing ID's is required!"}), 400


  exam = Exams.query.filter_by(id=exam_id, vault_id=vault_id).first()

  if not exam:
    return jsonify({'message': "No such exam!"}), 400

  if not exam.vault.creator_id == user_id:
    return jsonify({'message': 'Unauthorized'}), 401

  db.session.delete(exam)
  db.session.commit()

  return jsonify({'message': 'Success', 'exam_name': exam.exam_name}), 200


@vaults_bp.route('/edit-vault', methods=['POST'])
@jwt_required()
def edit_vault():
  data = request.get_json()
  vault_id = data.get('vault_id')
  new_vault_data = data.get('vault')
  print(vault_id, new_vault_data)
  # print('VAULT:', new_vault_data , 'EXAMS:',new_vault_data.get('exams'), 'FIRST EXAM ID:', new_vault_data.get('exams')[0].get('examId'))
  # return jsonify({'message': 'Vault edited successfully'}), 200
  user_id = get_jwt_identity()['user_id']
  if not vault_id or not new_vault_data:
    return jsonify({'message': 'Missing data!'}), 400

  vault = Vault.query.filter_by(id=vault_id).first()

  if not vault:
    return jsonify({'message': 'No such vault!'}), 400

  if vault.creator_id != user_id:
    return jsonify({'message': 'Unauthorized'}), 401

  vault.vault_name = new_vault_data.get('vaultName', vault.vault_name)
  existing_exam_ids = {}
  try:
    # Adding the new exams
    for index, exam in enumerate(new_vault_data.get('exams')):
      exam_id = exam.get('examId')
      if not exam_id:
        new_exam = Exams(exam_name=exam.get('examName'), exam_date=exam.get('examDate'),
                         exam_notes=exam.get('examNotes'), exam_links=json.dumps(exam.get('examLinks')),
                         vault_id=vault_id)
        db.session.add(new_exam)
        db.session.flush()
        existing_exam_ids[new_exam.id] = 'new'
        continue
      existing_exam_ids[exam_id] = index

    for exam in vault.exams:
      exam_index_in_new_data = existing_exam_ids.get(exam.id)
      if exam_index_in_new_data is None:
        db.session.delete(exam)
        continue
      elif exam_index_in_new_data == 'new':
          continue
      exam.exam_name = new_vault_data.get('exams')[exam_index_in_new_data].get('examName', exam.exam_name)
      exam.exam_date = new_vault_data.get('exams')[exam_index_in_new_data].get('examDate', exam.exam_date)
      exam.exam_notes = new_vault_data.get('exams')[exam_index_in_new_data].get('examNotes', exam.exam_notes)
      exam.exam_links = json.dumps(new_vault_data.get('exams')[exam_index_in_new_data].get('examLinks', exam.exam_links))

    db.session.commit()
  except Exception as e:
    db.session.rollback()
    return jsonify({'message': 'An error occurred while editing the vault.', 'error': str(e)}), 500

  return jsonify({'message': 'Vault edited successfully'}), 200




@vaults_bp.route('/subscribe/<int:vault_id>', methods=['POST'])
@jwt_required()
def subscribe_to_vault(vault_id):
    user_id = get_jwt_identity()['user_id']
    vault = Vault.query.filter_by(id=vault_id).first()

    if not vault:
        return jsonify({'message': 'No such vault!'}), 400

    if vault.creator_id == user_id:
        return jsonify({'message': 'Cannot subscribe to your own vault!'}), 400

    is_already_subscribed = VaultSubscription.query.filter_by(vault_id=vault_id, user_id=user_id).first()

    if is_already_subscribed:
        return jsonify({'message': 'Already subscribed!'}), 400

    subscription = VaultSubscription(vault_id=vault_id, user_id=user_id)
    vault.subscribers_count += 1
    db.session.add(subscription)
    db.session.commit()

    return jsonify({'message': 'Subscribed successfully'}), 200


@vaults_bp.route('/subscribe/<int:vault_id>', methods=['DELETE'])
@jwt_required()
def unsubscribe_from_vault(vault_id):
    user_id = get_jwt_identity()['user_id']
    vault = Vault.query.filter_by(id=vault_id).first()

    if not vault:
        return jsonify({'message': 'No such vault!'}), 400

    subscription = VaultSubscription.query.filter_by(vault_id=vault_id, user_id=user_id).first()

    if not subscription:
        return jsonify({'message': 'Not subscribed!'}), 400

    db.session.delete(subscription)
    vault.subscribers_count -= 1
    db.session.commit()

    return jsonify({'message': 'Unsubscribed successfully'}), 200




