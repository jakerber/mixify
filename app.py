"""Flask app runner."""
try:
    import config  # Safely initialize application config
except KeyError as error:
    raise RuntimeError(f'missing environment variable: {str(error)}') from error
import flask
import flask_cors
from api import endpoints
from db import connection as db_connection

# Initialize Flask app
app = flask.Flask(__name__)
app.secret_key = config.SECRET_KEY
flask_cors.CORS(app)

# Connect to database
db_connection.connect_to_db(app)

# Route endpoints
endpoints.route(app)

if __name__ == '__main__':
    app.run()
