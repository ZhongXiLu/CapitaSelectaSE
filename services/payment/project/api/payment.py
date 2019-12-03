import base64
import time
import os

from util.send_request import send_request
from requests.exceptions import RequestException

from flask import Blueprint, jsonify, request
from Crypto.Cipher import AES

payment_blueprint = Blueprint('encryption', __name__, url_prefix='/payment')


@payment_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@payment_blueprint.route('', methods=['POST'])
def create_payment():
    """Generate a new key of a user"""
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload'
    }

    parameters = request.get_json()
    if not parameters:
        return jsonify(response_object), 400

    try:
        payment_successful = False
        user_id = int(parameters.get('user_id'))
        card_type = str(parameters.get('card_type'))
        amount = int(parameters.get('amount'))

        # Get key (and IV) to encrypt the sensitive information
        response_obj = send_request('get', 'encryption', f'keys/{user_id}')
        if response_obj.status_code != 200:
            raise RequestException('Failed retrieving key for user')

        # Initialize some AES parameters
        response_json = response_obj.json
        key = bytes.fromhex(response_json['key']['key'])
        IV = bytes.fromhex(response_json['key']['IV'])
        unpad = lambda s: s[:-ord(s[len(s) - 1:])]

        # Get encrypted data
        _card_holder_name = base64.b64decode(parameters.get('card_holder_name'))
        _card_number = base64.b64decode(parameters.get('card_number'))
        _expiration_date_month = base64.b64decode(parameters.get('expiration_date_month'))
        _expiration_date_year = base64.b64decode(parameters.get('expiration_date_year'))
        _cvv = base64.b64decode(parameters.get('cvv'))

        # Set up AES's
        aes_card_holder_name = AES.new(key, AES.MODE_CBC, _card_holder_name[:16])
        aes_card_number = AES.new(key, AES.MODE_CBC, _card_number[:16])
        aes_expiration_date_month = AES.new(key, AES.MODE_CBC, _expiration_date_month[:16])
        aes_expiration_date_year = AES.new(key, AES.MODE_CBC, _expiration_date_year[:16])
        aes_cvv = AES.new(key, AES.MODE_CBC, _cvv[:16])

        # Decrypt the credit card information
        card_holder_name = unpad(aes_card_holder_name.decrypt(_card_holder_name[16:]).decode("utf-8"))
        card_number = unpad(aes_card_number.decrypt(_card_number[16:]).decode("utf-8"))
        expiration_date_month = unpad(aes_expiration_date_month.decrypt(_expiration_date_month[16:]).decode("utf-8"))
        expiration_date_year = unpad(aes_expiration_date_year.decrypt(_expiration_date_year[16:]).decode("utf-8"))
        cvv = unpad(aes_cvv.decrypt(_cvv[16:]).decode("utf-8"))

        # Actual call to payment API
        if card_type == 'VISA':
            time.sleep(float(os.environ.get('API_RESPONSE_TIME')))  # Just "mock" for now
            payment_successful = True
        elif card_type == 'MasterCard':
            time.sleep(float(os.environ.get('API_RESPONSE_TIME')))  # Just "mock" for now
            payment_successful = True
        elif card_type == 'American Express':
            time.sleep(float(os.environ.get('API_RESPONSE_TIME')))  # Just "mock" for now
            payment_successful = True
        else:
            raise RequestException('Unsupported credit card type')

        response_object['status'] = 'success'
        response_object['message'] = f'Successfully processed transaction'
        response_object['payment_successful'] = payment_successful
        return jsonify(response_object), 201

    except Exception as e:
        response_object['message'] = str(e)
        return jsonify(response_object), 400
