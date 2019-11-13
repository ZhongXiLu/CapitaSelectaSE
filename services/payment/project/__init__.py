import os

from flask import Flask
from flask_cors import CORS


def create_app(script_info=None):
    # instantiate the app
    app = Flask(__name__)
    CORS(app, supports_credentials=True)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # register blueprints
    from project.api.payment import payment_blueprint
    app.register_blueprint(payment_blueprint)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app}

    return app
