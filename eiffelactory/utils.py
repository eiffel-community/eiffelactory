import time
import uuid


def current_time_millis():
    """Returns UNIX Epoch time, in milliseconds."""
    return int(round(time.time() * 1000))


def generate_uuid():
    return str(uuid.uuid4())
