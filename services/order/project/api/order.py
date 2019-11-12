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
        response_obj = send_request('post', 'user', 'users/verify', timeout=3, json={
            'user_id': user_id,
            'token': token
        })
        response = response_obj.json
        valid_token = response['data']['valid_token']

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

                    # TODO: contact PaymentService

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
