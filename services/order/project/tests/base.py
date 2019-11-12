from flask_testing import TestCase
from project import create_app, db
from project.api.models import *

app = create_app()


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        # Fill the DBs with tickets
        for ticketsLeftDB in ticketsLeftDBs:
            db.session.add(ticketsLeftDB(1))    # Just one ticket (= 350 tickets in total)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
