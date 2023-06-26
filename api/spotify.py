import requests
import urllib.parse


def add_to_queue(access_token: str, track_id: str):
    _exec_request(
        f'https://api.spotify.com/v1/me/player/queue?uri=spotify%3Atrack%3A{track_id}',
        requests.post,
        access_token)


def search_tracks(access_token: str, search_query: str):
    resp = _exec_request(
        f'https://api.spotify.com/v1/search?q={urllib.parse.quote(search_query)}&type=track',
        requests.get,
        access_token)
    return resp.json()['tracks']['items']


def get_track(access_token: str, track_id: str):
    resp = _exec_request(
        f'https://api.spotify.com/v1/tracks/{track_id}', requests.get, access_token)
    return resp.json()


def _exec_request(url, method, access_token):
    resp = method(url, headers={'Authorization': 'Bearer ' + access_token}, timeout=30)
    if resp.status_code != 200 and resp.status_code != 204:
        raise Exception(f'request failed: {resp.text} ({resp.status_code})')
    return resp
