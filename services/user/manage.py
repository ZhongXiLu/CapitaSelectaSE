import base64
import os
import unittest
import hashlib
from flask.cli import FlaskGroup
from Crypto.Cipher import AES

from project import create_app, db
from project.api.models import User

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command('recreate_db')
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command()
def test():
    """Runs the tests without code coverage"""
    os.environ['TESTING'] = "True"
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    os.environ['TESTING'] = "False"
    if result.wasSuccessful():
        return 0
    return 1


@cli.command('seed_db')
def seed_db():
    """Seed the database with some default users"""
    for i in range(10000):
        # Initialize AES
        key = bytes.fromhex(f'100000000000000000000000000{str(10000 + i)}')
        IV = bytes.fromhex(f'a00000000000000000000000000{str(10000 + i)}')
        pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

        user = User(f'User{i}', hashlib.sha256(f'User{i}'.encode('utf8')).hexdigest())
        user.gender = 'M'
        user.country = 'Belgium'
        user.city = 'Antwerp'
        user.zip_code = '2000'
        user.street = f'Keyserlei {i}'
        user.card_type = 'VISA'
        aes = AES.new(key, AES.MODE_CBC, IV)
        user.card_holder_name = base64.b64encode(IV + aes.encrypt(pad(f'User {i}'))).decode('utf-8')
        aes = AES.new(key, AES.MODE_CBC, IV)
        user.card_number = base64.b64encode(IV + aes.encrypt(pad(f'45000000000{str((10000 + i))}'))).decode('utf-8')
        aes = AES.new(key, AES.MODE_CBC, IV)
        user.expiration_date_month = base64.b64encode(IV + aes.encrypt(pad('4'))).decode('utf-8')
        aes = AES.new(key, AES.MODE_CBC, IV)
        user.expiration_date_year = base64.b64encode(IV + aes.encrypt(pad('2023'))).decode('utf-8')
        aes = AES.new(key, AES.MODE_CBC, IV)
        user.cvv = base64.b64encode(IV + aes.encrypt(pad('203'))).decode('utf-8')
        token = str(hash(user))
        user.token = token
        db.session.add(user)

    db.session.commit()


if __name__ == '__main__':
    cli()
