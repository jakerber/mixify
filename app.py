"""Flask app runner."""
import datetime
import utils
import requests
try:
    import config  # Safely initialize application config
except KeyError as error:
    raise RuntimeError(f'missing environment variable: {str(error)}')
import flask
import flask_cors
from db import connection as db_connection
from db import models

# Initialize Flask app
app = flask.Flask(__name__)
flask_cors.CORS(app)

# Connect to database
db_connection.connect_to_db(app)


@app.route('/v1/queue/<code>', methods=['GET'])
def fetch_queue(code):
    queue: models.Queues = models.Queues.query.filter_by(code=code).first()
    if queue is None:
        raise Exception('queue not found')
    return _populate_queue_with_tracks(queue)


@app.route('/v1/queue/<visitor_id>/<access_token>', methods=['GET'])
def create_queue(visitor_id, access_token):
    new_queue = models.Queues(
        code=utils.generate_queue_code(),
        access_token=access_token,
        started_by_visitor_id=visitor_id,
        started_on_utc=datetime.datetime.utcnow()).save()
    return new_queue.as_dict()


@app.route('/v1/queue/<visitor_id>/<code>/drake/forever', methods=['GET'])
def queue_drake_forever(visitor_id, code):
    forever_spotify_id = '6HSqyfGnsHYw9MmIpa9zlZ'
    queue: models.Queues = models.Queues.query.filter_by(code=code).first()
    if queue is None:
        raise Exception('queue not found')

    requests.post(
        'https://api.spotify.com/v1/me/player/queue?uri=spotify%3Atrack%3A' + forever_spotify_id,
        headers={'Authorization': 'Bearer ' + queue.access_token},
        timeout=30)
    models.QueueTracks(
        queue_id=queue.id,
        track_id=forever_spotify_id,
        track_name='forever',
        track_artist='drake',
        track_album_cover_url='tbd',
        track_length='tbd',
        added_by_visitor_id=visitor_id,
        added_on_utc=datetime.datetime.utcnow()).save()
    return _populate_queue_with_tracks(queue)


@app.route('/v1/queue/upvote/<visitor_id>/<queue_track_id>', methods=['GET'])
def upvote_track(visitor_id, queue_track_id):
    queue_track: models.QueueTracks = models.QueueTracks.query.filter_by(id=queue_track_id).first()
    if queue_track is None:
        raise Exception('queue track not found')

    models.QueueTrackUpvotes(
        queue_track_id=queue_track_id,
        upvoted_by_visitor_id=visitor_id,
        upvoted_on_utc=datetime.datetime.utcnow()).save()
    return _populate_queue_with_tracks(queue_track.queue)


def _populate_queue_with_tracks(queue: models.Queues) -> list:
    queue_info = queue.as_dict()
    queue_info['tracks'] = []
    for queue_track in models.QueueTracks.query.filter_by(
            queue_id=queue.id, played_on_utc=None).all():
        queue_track_info = queue_track.as_dict()
        queue_track_info['upvotes'] = [
            queue_track_upvote.upvoted_by_visitor_id
            for queue_track_upvote in models.QueueTrackUpvotes.query.filter_by(
                queue_track_id=queue_track.id).all()]
        queue_info['tracks'].append(queue_track_info)

    queue_info['tracks'].sort(key=lambda t: len(t['upvotes']), reverse=True)
    return queue_info


if __name__ == '__main__':
    app.run()
