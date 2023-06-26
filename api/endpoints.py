import flask
import datetime
from api import spotify
from api import utils
from db import models


def route(app: flask.Flask):
    app.route('/v1/queue/<code>', methods=['GET'])(fetch_queue)
    app.route('/v1/queue/<visitor_id>/<access_token>', methods=['GET'])(create_queue)
    app.route('/v1/queue/<visitor_id>/<code>/drake/forever', methods=['GET'])(queue_drake_forever)
    app.route('/v1/queue/upvote/<visitor_id>/<queue_track_id>', methods=['GET'])(upvote_track)
    app.route('/v1/search/<queue_id>/<search_query>', methods=['GET'])(search_tracks)
    app.route('/v1/queue/add/<queue_id>/<visitor_id>/<track_id>',
              methods=['GET'])(add_track_to_queue)


def fetch_queue(code):
    queue: models.Queues = models.Queues.query.filter_by(code=code).first()
    if queue is None:
        raise Exception('queue not found')
    return utils.populate_queue_with_tracks(queue)


def create_queue(visitor_id, access_token):
    new_queue = models.Queues(
        code=utils.generate_queue_code(),
        access_token=access_token,
        started_by_visitor_id=visitor_id,
        started_on_utc=datetime.datetime.utcnow()).save()
    return new_queue.as_dict()


def queue_drake_forever(visitor_id, code):
    forever_spotify_id = '6HSqyfGnsHYw9MmIpa9zlZ'
    queue: models.Queues = models.Queues.query.filter_by(code=code).first()
    if queue is None:
        raise Exception('queue not found')

    spotify.add_to_queue(queue.access_token, forever_spotify_id)
    models.QueueTracks(
        queue_id=queue.id,
        track_id=forever_spotify_id,
        track_name='forever',
        track_artist='drake',
        track_album_cover_url='tbd',
        track_length='tbd',
        added_by_visitor_id=visitor_id,
        added_on_utc=datetime.datetime.utcnow()).save()
    return utils.populate_queue_with_tracks(queue)


def upvote_track(visitor_id, queue_track_id):
    queue_track: models.QueueTracks = models.QueueTracks.query.filter_by(id=queue_track_id).first()
    if queue_track is None:
        raise Exception('queue track not found')

    models.QueueTrackUpvotes(
        queue_track_id=queue_track_id,
        upvoted_by_visitor_id=visitor_id,
        upvoted_on_utc=datetime.datetime.utcnow()).save()
    return utils.populate_queue_with_tracks(queue_track.queue)


def search_tracks(queue_id, search_query):
    queue: models.Queues = models.Queues.query.filter_by(id=queue_id).first()
    if queue is None:
        raise Exception('queue not found')

    search_results = []
    results = spotify.search_tracks(queue.access_token, search_query)
    for index, result in enumerate(results):
        if index == 5:
            break

        duration_mins = (result['duration_ms'] / (1000 * 60)) % 60
        duration_secs = (result['duration_ms'] / 1000) % 60
        search_results.append({
            'track_id': result['id'],
            'track_name': result['name'],
            'track_artist': ', '.join([artist['name'] for artist in result['artists']]),
            'track_album_cover_url': result['album']['images'][0]['url'],
            'track_length': f'{duration_mins}:{duration_secs}'})

    return search_results


def add_track_to_queue(queue_id, visitor_id, track_id):
    queue: models.Queues = models.Queues.query.filter_by(id=queue_id).first()
    if queue is None:
        raise Exception('queue not found')

    track_info = spotify.get_track(queue.access_token, track_id)
    duration_mins = (track_info['duration_ms'] / (1000 * 60)) % 60
    duration_secs = (track_info['duration_ms'] / 1000) % 60
    queue_track: models.QueueTracks = models.QueueTracks(
        queue_id=queue_id,
        track_id=track_id,
        track_name=track_info['name'],
        track_artist=', '.join([artist['name'] for artist in track_info['artists']]),
        track_album_cover_url=track_info['album']['images'][0]['url'],
        track_length=f'{duration_mins}:{duration_secs}',
        added_by_visitor_id=visitor_id,
        added_on_utc=datetime.datetime.utcnow()).save()
    spotify.add_to_queue(queue.access_token, track_id)

    return utils.populate_queue_with_tracks(queue_track.queue)
