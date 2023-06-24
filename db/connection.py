"""SQLAlchemy database connection module."""
import flask
import flask_sqlalchemy

import config

# Database connection instance
SQL = flask_sqlalchemy.SQLAlchemy(session_options={'expire_on_commit': False})


def connect_to_db(app: flask.Flask) -> None:
    """Establishes a SQLAlchemy database connection for the Flask app instance.

    :param app: current Flask app instance
    """
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
    SQL.init_app(app)

    # Create new tables if necessary
    with app.app_context():
        SQL.create_all()
