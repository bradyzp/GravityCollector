# -*- coding: utf-8 -*-
import os
import sys
import logging
from urllib.parse import quote

from flask import Flask
from flask_cors import CORS


_root_log = logging.getLogger()
_hdlr = logging.StreamHandler(sys.stderr)
_hdlr.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
_root_log.addHandler(_hdlr)
_root_log.setLevel(logging.DEBUG)

# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class DefaultConfig:
    DEBUG = False
    DB_USER = os.getenv('PGDB_USER', 'postgresql')
    DB_USER_PW = quote(os.getenv('PGDB_PASS', ''))
    DB_HOST = os.getenv('PGDB_HOST', 'localhost')
    DB_PORT = 5432
    DATABASE = os.getenv('PGDB_DATABASE', 'postgresql')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_USER_PW}@{DB_HOST}:{DB_PORT}/{DATABASE}'


def make_app(config_file=None) -> Flask:
    app = Flask('gravrepo', instance_relative_config=True)
    app.config.from_object('gravrepo.DefaultConfig')
    # app.config.from_pyfile(config_file, silent=False)
    print(f'Flask root is: {app.instance_path}')

    @app.before_request
    def before():
        _root_log.info("Received Request")

    CORS(app)

    from .models import db
    db.init_app(app)

    from .collector import sensor_blueprint, collector_blueprint
    app.register_blueprint(sensor_blueprint)
    app.register_blueprint(collector_blueprint)

    from .management import registration_blueprint
    app.register_blueprint(registration_blueprint)

    from .responder import responder_blueprint
    app.register_blueprint(responder_blueprint)

    print("App created")
    return app
