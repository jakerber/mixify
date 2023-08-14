"""Spotify API wrapper module."""
import urllib.parse
import requests


def add_to_queue(access_token: str, track_uri) -> None:
    """Add a track to the Spotify queue.

    :param access_token: Spotify API access token
    :param track_uri: URI of track
    """
    _exec_request(
        f'https://api.spotify.com/v1/me/player/queue?uri={track_uri}',
        requests.post,
        access_token)


def search(access_token: str, search_query: str) -> list[dict]:
    """Search Spotify for a track.

    :param access_token: Spotify API access token
    :param search_query: query to use for search
    :return: list of tracks (search results)
    """
    resp = _exec_request(
        f'https://api.spotify.com/v1/search?q={urllib.parse.quote(search_query)}&type=track',
        requests.get,
        access_token)
    return resp.json()['tracks']['items']


def get_playback_info(access_token: str) -> dict:
    """Fetch current playback info, including Spotify queue state and current track.

    :param access_token: Spotify API access token
    :return: dict with playback info
    """
    resp = _exec_request('https://api.spotify.com/v1/me/player/queue', requests.get, access_token)
    current_playback = resp.json()
    current_track_id = (None if current_playback['currently_playing'] is None
                        else current_playback['currently_playing']['id'])
    return {
        'current_track': current_track_id,
        'currently_playing': current_playback['currently_playing'],
        'queue': [track['id'] for track in current_playback['queue']]}


def get_track(access_token: str, track_id: str) -> dict:
    """Fetch a track.

    :param access_token: Spotify API access token
    :param track_id: ID of track
    :return: dict with track info
    """
    resp = _exec_request(
        f'https://api.spotify.com/v1/tracks/{track_id}', requests.get, access_token)
    return resp.json()


def get_user(access_token: str) -> dict:
    """Fetch a Spotify user.

    :param access_token: Spotify API access token
    :return: dict with user info
    """
    resp = _exec_request(
        'https://api.spotify.com/v1/me', requests.get, access_token)
    return resp.json()


def _exec_request(
        url, method, access_token, body: str | None = None, headers: dict | None = None) -> dict:
    """Execute a Spotify API request.

    :param url: request URL
    :param method: request HTTP method
    :param access_token: Spotify API access token
    :param body: request body, defaults to None
    :param headers: request headers, defaults to None
    :raises RuntimeError: _description_
    :return: _description_
    """
    headers = headers if headers else {}
    headers['Authorization'] = 'Bearer ' + access_token  # append Spotify access token to headers
    resp = method(url, headers=headers, data=(body if body else {}), timeout=30)  # execute request
    if str(resp.status_code)[0] != '2':
        resp_error = None
        try:
            resp_error = resp.json()
        except Exception:  # pylint: disable=broad-except
            resp_error = resp.text
        raise RuntimeError(resp_error)
    return resp
