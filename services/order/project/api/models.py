import os
from math import ceil

from project import db


class Ticket:

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(32))

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'token': self.token
        }


class TicketsLeft:

    count = db.Column(db.Integer, primary_key=True)

    def __init__(self, count):
        self.count = count

    def to_json(self):
        return {
            'count': self.count
        }


# Create all the database shards
shards = ceil(int(os.environ['NR_OF_TICKETS']) / int(os.environ['TICKETS_PER_SHARD']))
os.environ['NR_OF_SHARDS'] = str(shards)
ticketDBs = []
ticketsLeftDBs = []
for i in range(shards):
    ticketDBs.append(type(f'Ticket-{i}', (Ticket, db.Model), {'__tablename__': f'tickets-{i}'}))
    ticketsLeftDBs.append(type(f'TicketsLeft-{i}', (TicketsLeft, db.Model), {'__tablename__': f'count-{i}'}))
