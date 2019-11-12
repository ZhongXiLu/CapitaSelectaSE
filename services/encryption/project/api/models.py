from project import db


class Key(db.Model):
    __tablename__ = 'keys'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    key = db.Column(db.String(32), nullable=False)
    IV = db.Column(db.String(32), nullable=False)

    def __init__(self, user_id, key, IV):
        self.user_id = user_id
        self.key = key
        self.IV = IV

    def to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'key': self.key,
            'IV': self.IV
        }
