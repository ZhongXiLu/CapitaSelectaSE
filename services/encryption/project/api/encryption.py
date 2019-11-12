import os
from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from requests.exceptions import RequestException

from project.api.models import Key
from project import db

encryption_blueprint = Blueprint('encryption', __name__, url_prefix='/keys')


@encryption_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@encryption_blueprint.route('', methods=['POST'])
def generate_key():
    """Generate a new key of a user"""
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload'
    }

    parameters = request.get_json()
    if not parameters:
        return jsonify(response_object), 400

    try:
        user_id = int(parameters.get('user_id'))

        new_key = os.urandom(16).hex()
        new_IV = os.urandom(16).hex()
        key = Key.query.filter_by(user_id=user_id).first()
        if not key:
            key = Key(user_id=user_id, key=new_key, IV=new_IV)
        else:
            key.key = new_key
            key.IV = new_IV

        db.session.add(key)
        db.session.commit()
        response_object['status'] = 'success'
        response_object['message'] = f'Successfully generated a new key'
        return jsonify(response_object), 201

    except (exc.IntegrityError, RequestException) as e:
        response_object['message'] = str(e)
        db.session.rollback()
        return jsonify(response_object), 400


@encryption_blueprint.route('/<user_id>', methods=['GET'])
def get_key(user_id):
    """Get the key of a user"""
    response_object = {
        'status': 'fail',
        'message': 'User does not exist'
    }
    try:
        key = Key.query.filter_by(id=int(user_id)).first()
        if not key:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'key': key.to_json()
            }
            return jsonify(response_object), 200

    except ValueError:
        return jsonify(response_object), 404
