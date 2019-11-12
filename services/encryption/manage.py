import os
import unittest
from Crypto import Random
from flask.cli import FlaskGroup

from project import create_app, db
from project.api.models import *

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
    """Seed the database with keys"""
    for i in range(10000):
        db.session.add(Key(user_id=i + 1, key=f'100000000000000000000000000{10000 + i}',
                           IV=f'a00000000000000000000000000{10000 + i}'))
    db.session.commit()


if __name__ == '__main__':
    cli()
