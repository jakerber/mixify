"""Queue API controller module."""
import config
import datetime
from api import payments
from api import spotify
from api import utils
from db import models


def fetch_queue(queue_name: str, fpjs_visitor_id: str) -> dict:
    """Fetch a Mixify queue.

    :param queue_name: queue name
    :return: queue object
    :raises RuntimeError: if queue ID is invalid or queue has been ended
    """
    queue: models.Queues = models.Queues.query.filter_by(name=queue_name.lower()).first()
    if queue is None:
        raise RuntimeError('queue not found')
    if queue.ended_on_utc is not None:
        raise RuntimeError('queue is ended')

    return utils.get_queue_with_tracks(queue, fpjs_visitor_id)


def create_queue(spotify_access_token: str, fpjs_visitor_id: str) -> dict:
    """Create a Mixify queue.

    :param spotify_access_token: Spotify access token for queue host account
    :param fpjs_visitor_id: FingerprintJS ID of user who created the queue
    :raises RuntimeError: if access token is invalid
    :return: new queue object
    """
    user = spotify.get_user(spotify_access_token)
    if 'id' not in user or user['id'] is None:
        raise RuntimeError('unable to fetch spotify user')  # invalid access token

    # Return Spotify user's active queue if one exists
    active_queue: models.Queues = models.Queues.query.filter_by(
        spotify_user_id=user['id'], ended_on_utc=None).first()
    if active_queue is not None:
        active_queue.spotify_access_token = spotify_access_token  # refresh access token
        active_queue.started_by_fpjs_visitor_id = fpjs_visitor_id  # refresh ownership
        active_queue.save()
        return active_queue.as_dict()

    # Generate unique queue name
    queue_name = ''
    while not queue_name or models.Queues.query.filter_by(name=queue_name).first() is not None:
        queue_name = utils.generate_random_queue_name()

    new_queue = models.Queues(
        name=queue_name,
        spotify_user_id=user['id'],
        spotify_access_token=spotify_access_token,
        started_by_fpjs_visitor_id=fpjs_visitor_id,
        started_on_utc=datetime.datetime.utcnow()).save()
    return new_queue.as_dict()


def search_tracks(queue_id: str, search_query: str) -> dict:
    """Search Spotify for a track.

    :param queue_id: ID of queue to search for
    :param search_query: query to use for search
    :raises RuntimeError: if queue ID is invalid
    :return: list of tracks (search results)
    """
    queue: models.Queues = models.Queues.query.filter_by(id=queue_id).first()
    if queue is None:
        raise RuntimeError('queue not found')

    search_results_info: list[dict] = []
    for index, result in enumerate(spotify.search(queue.spotify_access_token, search_query)):
        if index == config.MAX_SEARCH_RESULTS:
            break
        search_results_info.append({
            'track_id': result['id'],
            'track_name': result['name'],
            'track_artist': ', '.join([artist['name'] for artist in result['artists']]),
            'track_album_cover_url': result['album']['images'][0]['url'],
            'track_length': result['duration_ms'],
            'track_explicit': result['explicit']})

    return search_results_info


def add_song_to_queue(queue_id: str, spotify_track_id: str, fpjs_visitor_id: str) -> dict:
    """Add a song from Spotify to a Mixify queue.

    :param queue_id: ID of Mixify queue
    :param spotify_track_id: Track ID of song on Spotify
    :param fpjs_visitor_id: FingerprintJS ID of user who added track
    :raises RuntimeError: if queue ID or track ID is invalid, or queue has been ended
    :return: updated queue object with track added
    """
    queue: models.Queues = models.Queues.query.filter_by(id=queue_id).first()
    if queue is None:
        raise RuntimeError('queue not found')
    if queue.ended_on_utc is not None:
        raise RuntimeError('queue is ended')
    if models.QueueSongs.query.filter_by(
            queue_id=queue_id, spotify_track_id=spotify_track_id,
            added_to_spotify_queue_on_utc=None).first() is not None:
        raise RuntimeError('song already in queue')
    track_info = spotify.get_track(queue.spotify_access_token, spotify_track_id)
    if 'id' not in track_info or track_info['id'] is None:
        raise RuntimeError('Spotify track not found')

    queue_track: models.QueueSongs = models.QueueSongs(
        queue_id=queue_id,
        name=track_info['name'],
        artist=', '.join([artist['name'] for artist in track_info['artists']]),
        album_cover_url=track_info['album']['images'][0]['url'],
        duration_ms=track_info['duration_ms'],
        spotify_track_id=spotify_track_id,
        spotify_track_uri=track_info['uri'],
        added_by_fpjs_visitor_id=fpjs_visitor_id,
        added_on_utc=datetime.datetime.utcnow()).save()

    return utils.get_queue_with_tracks(queue_track.queue, fpjs_visitor_id)


def upvote_song(queue_song_id: str, fpjs_visitor_id: str) -> dict:
    """Upvote an unplayed song in a Mixify queue.

    :param queue_song_id: queue song ID
    :param fpjs_visitor_id: FingerprintJS visitor ID
    :raises RuntimeError: if queue song ID is invalid or already queued on Spotify
    :return: updated queue with new upvote
    """
    queue_song: models.QueueSongs = models.QueueSongs.query.filter_by(id=queue_song_id).first()
    if queue_song is None:
        raise RuntimeError('queue song not found')
    if queue_song.added_to_spotify_queue_on_utc is not None:
        raise RuntimeError('song already queued on Spotify')

    models.QueueSongUpvotes(
        queue_song_id=queue_song_id,
        upvoted_by_fpjs_visitor_id=fpjs_visitor_id,
        upvoted_on_utc=datetime.datetime.utcnow()).save()

    return utils.get_queue_with_tracks(queue_song.queue, fpjs_visitor_id)


def remove_song_upvote(queue_song_id: str, fpjs_visitor_id: str) -> dict:
    """Remove an upvote on an unplayed song in a Mixify queue.

    :param queue_song_id: queue song ID
    :param fpjs_visitor_id: FingerprintJS visitor ID
    :raises RuntimeError: if queue song ID is invalid or already queued on Spotify
    :return: updated queue with upvote removed
    """
    queue_song: models.QueueSongs = models.QueueSongs.query.filter_by(id=queue_song_id).first()
    if queue_song is None:
        raise RuntimeError('queue song not found')
    if queue_song.added_to_spotify_queue_on_utc is not None:
        raise RuntimeError('song already queued on Spotify')

    queue_song_upvote: models.QueueSongUpvotes = models.QueueSongUpvotes.query.filter_by(
        queue_song_id=queue_song.id, upvoted_by_fpjs_visitor_id=fpjs_visitor_id).first()
    if queue_song_upvote is None:
        raise RuntimeError('queue song upvote not found')
    queue_song_upvote.delete()

    return utils.get_queue_with_tracks(queue_song.queue, fpjs_visitor_id)


def end_queue(queue_id: str, fpjs_visitor_id: str) -> dict:
    """End a Mixify queue.

    :param queue_id: queue ID
    :param fpjs_visitor_id: FingerprintJS visitor ID
    :raises RuntimeError: if queue ID is invalid
    :return: empty object
    """
    queue: models.Queues = models.Queues.query.filter_by(id=queue_id).first()
    if queue is None:
        raise RuntimeError('queue not found')
    if queue.started_by_fpjs_visitor_id != fpjs_visitor_id:
        raise RuntimeError('user is not starter of queue')

    queue.ended_on_utc = datetime.datetime.utcnow()
    queue.save()
    return {}


def pause_queue(queue_id: str, fpjs_visitor_id: str) -> dict:
    """Pause a Mixify queue.

    :param queue_id: queue ID
    :param fpjs_visitor_id: FingerprintJS visitor ID
    :raises RuntimeError: if queue ID is invalid
    :return: paused queue object
    """
    queue: models.Queues = models.Queues.query.filter_by(id=queue_id).first()
    if queue is None:
        raise RuntimeError('queue not found')

    queue.paused_on_utc = datetime.datetime.utcnow()
    queue.save()
    return utils.get_queue_with_tracks(queue, fpjs_visitor_id)


def unpause_queue(queue_id: str, fpjs_visitor_id: str) -> dict:
    """Unpause a Mixify queue.

    :param queue_id: queue ID
    :param fpjs_visitor_id: FingerprintJS visitor ID
    :raises RuntimeError: if queue ID is invalid
    :return: unpaused queue object
    """
    queue: models.Queues = models.Queues.query.filter_by(id=queue_id).first()
    if queue is None:
        raise RuntimeError('queue not found')

    queue.paused_on_utc = None
    queue.save()
    return utils.get_queue_with_tracks(queue, fpjs_visitor_id)


def subscribe_to_queue(queue_id: str, spotify_access_token: str, fpjs_visitor_id: str) -> dict:
    """Subscribe to a Mixify queue.

    :param queue_id: queue ID
    :param spotify_access_token: Spotify access token of subscriber
    :param fpjs_visitor_id: FingerprintJS visitor ID of subscriber
    :return: queue object
    """
    queue: models.Queues = models.Queues.query.filter_by(id=queue_id).first()
    if queue is None:
        raise RuntimeError('queue not found')
    existing_subscriber: models.QueueSubscribers = models.QueueSubscribers.query.filter_by(
        queue_id=queue.id, spotify_access_token=spotify_access_token).first()
    if existing_subscriber is not None:
        existing_subscriber.fpjs_visitor_id = fpjs_visitor_id
        existing_subscriber.save()
        return queue.as_dict()

    models.QueueSubscribers(
        queue_id=queue_id,
        spotify_access_token=spotify_access_token,
        fpjs_visitor_id=fpjs_visitor_id,
        subscribed_on_utc=datetime.datetime.utcnow()).save()
    return queue.as_dict()


def unsubscribe_from_queue(queue_id: str, fpjs_visitor_id: str) -> dict:
    """Unsubscribe from a Mixify queue.

    :param queue_id: queue ID
    :param spotify_access_token: Spotify access token of subscriber
    :param fpjs_visitor_id: FingerprintJS visitor ID of subscriber
    :return: empty object
    """
    queue: models.Queues = models.Queues.query.filter_by(id=queue_id).first()
    if queue is None:
        raise RuntimeError('queue not found')
    subscriber: models.QueueSubscribers = models.QueueSubscribers.query.filter_by(
        queue_id=queue.id, fpjs_visitor_id=fpjs_visitor_id).first()
    if subscriber is None:
        raise RuntimeError('subscriber not found')

    subscriber.delete()
    return utils.get_queue_with_tracks(queue, fpjs_visitor_id)


def create_boost_payment(queue_song_id: str, fpjs_visitor_id: str) -> dict:
    """Create the Stripe payment intent to boost a song in a Mixify queue.

    :param queue_song_id: queue song ID
    :param fpjs_visitor_id: FingerprintJS visitor ID
    :raises RuntimeError: if queue song ID is invalid or already queued on Spotify
    :return: dict with payment intent client secret
    """
    queue_song: models.QueueSongs = models.QueueSongs.query.filter_by(id=queue_song_id).first()
    if queue_song is None:
        raise RuntimeError('queue song not found')
    if queue_song.added_to_spotify_queue_on_utc is not None:
        raise RuntimeError('song already queued on Spotify')
    if queue_song.queue.paused_on_utc is not None:
        raise RuntimeError('queue is paused')
    if queue_song.queue.ended_on_utc is not None:
        raise RuntimeError('queue is ended')

    # Create Stripe payment intent for the boost
    try:
        stripe_client_secret = payments.create_boost_payment(
            config.BOOST_COST_USD, queue_song_id, fpjs_visitor_id)
    except Exception as error:  # pylint: disable=broad-except
        raise RuntimeError(f'unable to create stripe payment: {str(error)}') from error

    return {'stripe_client_secret': stripe_client_secret}


def boost_song(queue_song_id: str, fpjs_visitor_id: str) -> dict:
    """Immedately queue an unplayed song in a Mixify queue.

    :param queue_song_id: queue song ID
    :param fpjs_visitor_id: FingerprintJS visitor ID
    :raises RuntimeError: if queue song ID is invalid or already queued on Spotify
    :return: updated queue with boosted song
    """
    queue_song: models.QueueSongs = models.QueueSongs.query.filter_by(id=queue_song_id).first()
    if queue_song is None:
        raise RuntimeError('queue song not found')
    if queue_song.added_to_spotify_queue_on_utc is not None:
        raise RuntimeError('song already queued on Spotify')
    if queue_song.queue.paused_on_utc is not None:
        raise RuntimeError('queue is paused')
    if queue_song.queue.ended_on_utc is not None:
        raise RuntimeError('queue is ended')

    # Queue the song on the host's Spotify
    try:
        spotify.add_to_queue(queue_song.queue.spotify_access_token, queue_song.spotify_track_uri)
    except Exception as error:  # pylint: disable=broad-except
        raise RuntimeError(f'unable to queue song: {str(error)}') from error
    else:
        queue_song.added_to_spotify_queue_on_utc = datetime.datetime.utcnow()
        queue_song.save()

        # Record new boost for host payout
        models.QueueSongBoosts(
            queue_id=queue_song.queue.id,
            queue_song_id=queue_song.id,
            boosted_by_fpjs_visitor_id=fpjs_visitor_id,
            cost_usd=config.BOOST_COST_USD).save()

    return utils.get_queue_with_tracks(queue_song.queue, fpjs_visitor_id)
