from project import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    gender = db.Column(db.CHAR())

    token = db.Column(db.String(32), unique=True)

    country = db.Column(db.String(128))
    city = db.Column(db.String(128))
    zip_code = db.Column(db.String(16))
    street = db.Column(db.String(128))

    card_type = db.Column(db.String(128))
    card_number = db.Column(db.String(16))
    expiration_date_month = db.Column(db.Integer)
    expiration_date_year = db.Column(db.Integer)
    cvv = db.Column(db.String(3))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'gender': self.gender,
            'token': self.token,
            'card_type': self.card_type,
            'card_number': self.card_number,
            'expiration_date_month': self.expiration_date_month,
            'expiration_date_year': self.expiration_date_year,
            'cvv': self.cvv
        }
