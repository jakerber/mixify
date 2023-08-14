"""Mixify API utility function module."""
import datetime
import random
from db import models
from api import spotify

QUEUE_NAME_CHAR_OPTIONS = 'abcdefghjklmnopqrstuvwxyz123456789'
QUEUE_NAME_LENGTH = 6


def generate_random_queue_name():
    """Generate a random name for a Mixify queue.

    :return: queue name
    """
    queue_name = ''
    for _ in range(QUEUE_NAME_LENGTH):
        queue_name += QUEUE_NAME_CHAR_OPTIONS[random.randint(0, len(QUEUE_NAME_CHAR_OPTIONS) - 1)]
    return queue_name


def get_queue_with_tracks(queue: models.Queues) -> list:
    """Fetches the current Mixify queue with playback info.

    :param queue: Mixify queue object
    :return: queue object with playback info
    """
    queue_info = queue.as_dict()
    queued_songs: list[dict] = []
    played_songs: list[dict] = []
    current_song = {}

    # Fetch Spotify playback info of host
    playback_info = spotify.get_playback_info(queue.spotify_access_token)
    current_spotify_track_playing: str | None = playback_info['current_track']
    current_spotify_queue_track_ids = set(playback_info['queue'])

    # Fetch all songs in the Mixify queue
    # Handle newest song first to accurately identify currently playing entry
    queue_songs: list[models.QueueSongs] = models.QueueSongs.query.filter_by(
        queue_id=queue.id).all()
    queue_songs.sort(key=lambda t: t.added_on_utc, reverse=True)

    # Break songs in the Mixify queue into playback state buckets
    for queue_song in queue_songs:
        queue_song_info = queue_song.as_dict()
        queue_song_info['upvotes']: list[str] = [
            queue_song_upvote.upvoted_by_fpjs_visitor_id
            for queue_song_upvote in models.QueueSongUpvotes.query.filter_by(
                queue_song_id=queue_song.id).all()]
        if (not current_song and queue_song.spotify_track_id == current_spotify_track_playing
                and queue_song.added_to_spotify_queue_on_utc is not None):
            current_song = queue_song_info
            queue_song.played_on_utc = datetime.datetime.utcnow()
            queue_song.save()
        elif (queue_song.added_to_spotify_queue_on_utc is not None
              and queue_song.spotify_track_id not in current_spotify_queue_track_ids):
            played_songs.append(queue_song_info)
        else:

            # TODO: Handle case of already played song appearing as in the queue because Spotify
            # added it under the "Next from" section.

            if queue_song.played_on_utc is None:
                queued_songs.append(queue_song_info)

    # Append queue subscribers
    queue_info['subscribers'] = [
        subscriber.as_dict() for subscriber in models.QueueSubscribers.query.filter_by(
            queue_id=queue.id).all()]

    # Sort buckets for frontend queue display
    queued_songs.sort(key=lambda t: (
        t['added_to_spotify_queue_on_utc'] is None, 1 - len(t['upvotes']), t['added_on_utc']))
    played_songs.sort(key=lambda t: t['added_to_spotify_queue_on_utc'], reverse=True)
    queue_info['queued_songs'] = queued_songs
    queue_info['played_songs'] = played_songs
    queue_info['current_song'] = current_song
    queue_info['currently_playing'] = None
    if playback_info['currently_playing'] is not None:
        queue_info['currently_playing'] = {
            'name': playback_info['currently_playing']['name'],
            'artist': ', '.join(
                [artist['name'] for artist in playback_info['currently_playing']['artists']]),
            'album_cover_url': playback_info[
                'currently_playing']['album']['images'][0]['url']}

    return queue_info
