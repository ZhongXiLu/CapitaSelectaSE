from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from util.send_request import send_request
from requests.exceptions import RequestException
import hashlib

from project.api.models import User
from project import db

user_blueprint = Blueprint('user', __name__, url_prefix='/users')


@user_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@user_blueprint.route('', methods=['POST'])
def add_user():
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload'
    }

    parameters = request.get_json()
    if not parameters:
        return jsonify(response_object), 400

    try:
        username = str(parameters.get('username'))
        password = str(parameters.get('password'))

        user = User.query.filter_by(username=username).first()
        if not user:
            # SHA256 is used to hash passwords now, in the real world it's better to use salt and whatnot
            password_hash = hashlib.sha256(password.encode('utf8')).hexdigest()
            user = User(username=username, password=password_hash)
            db.session.add(user)
            db.session.commit()

            response_object['status'] = 'success'
            response_object['message'] = f'{username} was successfully added'
            response_object['user_id'] = user.id
            return jsonify(response_object), 201
        else:
            response_object['message'] = f'Username {username} already exists'
            return jsonify(response_object), 400

    except (exc.IntegrityError, RequestException) as e:
        response_object['message'] = str(e)
        db.session.rollback()
        return jsonify(response_object), 400


@user_blueprint.route('', methods=['PUT'])
def update_user():
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload'
    }

    parameters = request.get_json()
    if not parameters:
        return jsonify(response_object), 400
    user_id = str(parameters.get('user_id'))

    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            response_object['message'] = 'User does not exist'
            return jsonify(response_object), 404
        else:
            # TODO: encrypt this information
            user.gender = str(parameters.get('gender'))
            user.country = str(parameters.get('country'))
            user.city = str(parameters.get('city'))
            user.zip_code = str(parameters.get('zip_code'))
            user.street = str(parameters.get('street'))
            user.card_type = str(parameters.get('card_type'))
            user.card_number = str(parameters.get('card_number'))
            user.expiration_date_month = str(parameters.get('expiration_date_month'))
            user.expiration_date_year = str(parameters.get('expiration_date_year'))
            user.cvv = str(parameters.get('cvv'))

            token = str(hash(user))
            user.token = token

            db.session.commit()

            response_object['status'] = 'success'
            response_object['message'] = f'{user.username} was successfully updated'
            response_object['token'] = token
            return jsonify(response_object), 200

    except (exc.IntegrityError, RequestException) as e:
        response_object['message'] = str(e)
        db.session.rollback()
        return jsonify(response_object), 400


@user_blueprint.route('/<user_id>', methods=['GET'])
def get_single_user(user_id):
    """Get single user details"""
    response_object = {
        'status': 'fail',
        'message': 'User does not exist'
    }
    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'user': user.to_json()
            }
            return jsonify(response_object), 200

    except ValueError:
        return jsonify(response_object), 404


@user_blueprint.route('', methods=['GET'])
def get_all_users():
    """Get all users"""
    response_object = {
        'status': 'success',
        'data': {
            'users': [user.to_json() for user in User.query.all()]
        }
    }
    return jsonify(response_object), 200


@user_blueprint.route('/verify', methods=['POST'])
def verify_user():
    """Verify a user with their token"""
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload'
    }

    parameters = request.get_json()
    if not parameters:
        return jsonify(response_object), 400
    user_id = parameters.get('user_id')
    token = parameters.get('token')

    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            return jsonify(response_object), 404
        else:
            valid_token = user.token == token

            response_object['status'] = 'success'
            response_object['message'] = f'{user.username} has been verified'
            response_object['valid_token'] = valid_token
            return jsonify(response_object), 200

    except (ValueError, RequestException) as e:
        db.session.rollback()
        return jsonify(response_object), 400
