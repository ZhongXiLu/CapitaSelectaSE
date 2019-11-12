import os
import unittest
import hashlib

from flask.cli import FlaskGroup

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
        user = User(f'User{i}', hashlib.sha256(f'User{i}'.encode('utf8')).hexdigest())
        user.gender = 'M'
        user.country = 'Belgium'
        user.city = 'Antwerp'
        user.zip_code = '2000'
        user.street = f'Keyserlei {i}'
        user.card_type = 'VISA'
        user.card_number = f'45000000000{str((10000 + i))}'
        user.expiration_date_month = 4
        user.expiration_date_year = 2023
        user.cvv = '203'
        token = str(hash(user))
        user.token = token
        db.session.add(user)
    db.session.commit()


if __name__ == '__main__':
    cli()
