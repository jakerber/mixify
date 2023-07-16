"""Queue Manager API controller module."""
import datetime
import config
from api import spotify
from db import models


def manage_active_queues(token: str) -> dict:
    """Manages active Mixify queues and Spotify playback.

    Runs once per minute globally.

    :return: dict with songs added to Spotify queues, if any
    :raises RuntimeError: if manager token is invalid
    """
    if token != config.QUEUE_MANAGER_TOKEN:
        raise RuntimeError('invalid manager token')
    songs_queued_on_spotify = {}
    for active_queue in models.Queues.query.filter_by(ended_on_utc=None, paused_on_utc=None).all():
        active_queue_songs = models.QueueSongs.query.filter_by(queue_id=active_queue.id).all()
        unplayed_queue_songs = [
            queue_song for queue_song in active_queue_songs
            if queue_song.added_to_spotify_queue_on_utc is None]
        if len(unplayed_queue_songs) == 0:
            continue  # no songs to queue, skip

        # Fetch current queue and song playing
        track_ids_in_spotify_queue = []
        try:
            track_ids_in_spotify_queue = spotify.get_playback_info(
                active_queue.spotify_access_token)['queue']
        except Exception:  # pylint: disable=broad-except
            continue  # access token expired

        # Determine the song last added to the Spotify queue by Mixify
        last_queued_track_id: str | None = None
        last_queued_on: datetime.datetime | None = None
        for queue_song in active_queue_songs:
            if queue_song.added_to_spotify_queue_on_utc is None:
                continue  # not played yet, skip
            if last_queued_on is None or queue_song.added_to_spotify_queue_on_utc > last_queued_on:
                last_queued_track_id = queue_song.spotify_track_id
                last_queued_on = queue_song.added_to_spotify_queue_on_utc

        # Skip if Mixify song is in the Spotify queue
        if last_queued_track_id in track_ids_in_spotify_queue:
            continue

        # Determine the song at the top of the Mixify queue
        top_song: models.QueueSongs | None = None
        top_song_upvotes = -1
        for song in unplayed_queue_songs:
            song_upvotes = len(models.QueueSongUpvotes.query.filter_by(queue_song_id=song.id).all())
            if song_upvotes > top_song_upvotes or (
                    song_upvotes == top_song_upvotes
                    and song.added_on_utc < top_song.added_on_utc):
                top_song = song
                top_song_upvotes = song_upvotes

        # Add the next song to Spotify queue
        try:
            spotify.add_to_queue(active_queue.spotify_access_token, top_song.spotify_track_uri)
        except Exception:  # pylint: disable=broad-except
            pass  # Host has no devices active.
        else:
            top_song.added_to_spotify_queue_on_utc = datetime.datetime.utcnow()
            top_song.save()
            songs_queued_on_spotify[active_queue.name] = top_song.name

    print({'queued_songs': songs_queued_on_spotify})  # easy debugging :)

    return songs_queued_on_spotify
