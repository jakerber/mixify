import random
from db import models

QUEUE_CODE_DIGIT_OPTIONS = 'abcdefghjkmnpqrstuvwxyz123456789'


def generate_queue_code():
    queue_code = ''
    queue_code += QUEUE_CODE_DIGIT_OPTIONS[random.randint(0, len(QUEUE_CODE_DIGIT_OPTIONS) - 1)]
    queue_code += QUEUE_CODE_DIGIT_OPTIONS[random.randint(0, len(QUEUE_CODE_DIGIT_OPTIONS) - 1)]
    queue_code += QUEUE_CODE_DIGIT_OPTIONS[random.randint(0, len(QUEUE_CODE_DIGIT_OPTIONS) - 1)]
    queue_code += '-'
    queue_code += QUEUE_CODE_DIGIT_OPTIONS[random.randint(0, len(QUEUE_CODE_DIGIT_OPTIONS) - 1)]
    queue_code += QUEUE_CODE_DIGIT_OPTIONS[random.randint(0, len(QUEUE_CODE_DIGIT_OPTIONS) - 1)]
    queue_code += QUEUE_CODE_DIGIT_OPTIONS[random.randint(0, len(QUEUE_CODE_DIGIT_OPTIONS) - 1)]
    return queue_code


def populate_queue_with_tracks(queue: models.Queues) -> list:
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
