import os
from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from util.send_request import send_request
from requests.exceptions import RequestException

from project.api.models import *
from project import db

order_blueprint = Blueprint('order', __name__, url_prefix='/orders')


@order_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@order_blueprint.route('', methods=['POST'])
def order_ticket():
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload'
    }

    parameters = request.get_json()
    if not parameters:
        return jsonify(response_object), 400

    try:
        user_id = int(parameters.get('user_id'))
        token = str(parameters.get('token'))

        # Verify user
        response_obj = send_request('post', 'user', 'users/verify', json={
            'user_id': user_id,
            'token': token
        })
        valid_token = False
        user = None
        if response_obj.status_code == 200:
            response = response_obj.json
            valid_token = response['valid_token']
            user = response['user']
        else:
            response_object = response_obj
            return jsonify(response_object), 400

        if valid_token:
            stop = False
            # Choose the database shard
            shards = int(os.environ['NR_OF_SHARDS'])
            initial_shard = hash(token) % shards
            shard_nr = initial_shard
            while not stop:

                # Check if there are any tickets left in this shard
                ticketsLeft = ticketsLeftDBs[shard_nr].query.first()
                if ticketsLeft.count > 0:

                    # Try the actual payment
                    response_obj = send_request('post', 'payment', 'payment', json={
                        'user_id': user['id'],
                        'card_type': user['card_type'],
                        'card_holder_name': user['card_holder_name'],
                        'card_number': user['card_number'],
                        'expiration_date_month': user['expiration_date_month'],
                        'expiration_date_year': user['expiration_date_year'],
                        'cvv': user['cvv'],
                        'amount': 100
                    })
                    if response_obj.status_code != 201 or not response_obj.json['payment_successful']:
                        raise RequestException(f'Failed processing the payment with {user["card_type"]}')

                    # Everything went successful => create new ticket
                    ticket = ticketDBs[shard_nr](user_id, token)
                    db.session.add(ticket)
                    ticketsLeft.count -= 1

                    db.session.commit()
                    response_object['ticket_id'] = ticket.id
                    response_object['message'] = 'Successfully ordered a new ticket'
                    stop = True

                else:
                    # Go to the next shard
                    shard_nr = (shard_nr + 1) % shards
                    if shard_nr == initial_shard:
                        # No more tickets in all DB's
                        response_object['message'] = 'No more tickets left'
                        stop = True
        else:
            response_object['message'] = 'User verification failed'

        response_object['status'] = 'success'
        return jsonify(response_object), 200

    except (exc.IntegrityError, RequestException) as e:
        response_object['message'] = str(e)
        db.session.rollback()
        return jsonify(response_object), 400
