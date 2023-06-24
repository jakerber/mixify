import random

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
