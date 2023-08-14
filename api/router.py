"""Mixify API router module."""
import sys
import typing
import flask
from api.controllers import queue_controller
from api.controllers import manager_controller


def route(app: flask.Flask):
    """Route API URLs to endpoint functions.

    :param app: Flask app instance
    """
    app.route(
        '/v1/queue/<queue_name>', methods=['GET'],
        defaults={'endpoint_func': queue_controller.fetch_queue})(_exec_request)
    app.route(
        '/v1/queue/new/<spotify_access_token>/<fpjs_visitor_id>', methods=['GET'],
        defaults={'endpoint_func': queue_controller.create_queue})(_exec_request)
    app.route(
        '/v1/queue/upvote/<queue_song_id>/<fpjs_visitor_id>', methods=['GET'],
        defaults={'endpoint_func': queue_controller.upvote_song})(_exec_request)
    app.route(
        '/v1/queue/upvote/remove/<queue_song_id>/<fpjs_visitor_id>', methods=['GET'],
        defaults={'endpoint_func': queue_controller.remove_song_upvote})(_exec_request)
    app.route(
        '/v1/queue/boost/<queue_song_id>/<fpjs_visitor_id>', methods=['GET'],
        defaults={'endpoint_func': queue_controller.boost_song})(_exec_request)
    app.route(
        '/v1/search/<queue_id>/<search_query>', methods=['GET'],
        defaults={'endpoint_func': queue_controller.search_tracks})(_exec_request)
    app.route(
        '/v1/queue/add/<queue_id>/<spotify_track_id>/<fpjs_visitor_id>', methods=['GET'],
        defaults={'endpoint_func': queue_controller.add_song_to_queue})(_exec_request)
    app.route(
        '/v1/queue/end/<queue_id>', methods=['GET'],
        defaults={'endpoint_func': queue_controller.end_queue})(_exec_request)
    app.route(
        '/v1/queue/pause/<queue_id>', methods=['GET'],
        defaults={'endpoint_func': queue_controller.pause_queue})(_exec_request)
    app.route(
        '/v1/queue/unpause/<queue_id>', methods=['GET'],
        defaults={'endpoint_func': queue_controller.unpause_queue})(_exec_request)
    app.route(
        '/v1/queue/subscribe/<queue_id>/<spotify_access_token>/<fpjs_visitor_id>', methods=['GET'],
        defaults={'endpoint_func': queue_controller.subscribe_to_queue})(_exec_request)
    app.route(
        '/v1/queue/unsubscribe/<queue_id>/<fpjs_visitor_id>', methods=['GET'],
        defaults={'endpoint_func': queue_controller.unsubscribe_from_queue})(_exec_request)

    app.route(
        '/v1/manager/<token>', methods=['GET'],
        defaults={'endpoint_func': manager_controller.manage_active_queues})(_exec_request)


def _exec_request(endpoint_func: typing.Callable,
                  *args, **kwargs) -> tuple[dict[str, typing.Any], int]:
    """Safely execute an API request.

    :param endpoint_func: function to call for the request
    :return: request response
    """
    try:
        # Status 200 OK
        return endpoint_func(*args, **kwargs), 200
    except Exception as error:  # pylint: disable=broad-except
        response: dict[str, str] = {}
        response['error_type'] = type(error).__name__
        response['error_message'] = str(error)

        status_code = 500  # default Internal Server Error
        sys.stderr.write(f'{str(response)}\n')
        return response, status_code
