import time
import uuid
import logging


def current_time_millis():
    """Returns UNIX Epoch time, in milliseconds."""
    return int(round(time.time() * 1000))


def generate_uuid():
    return str(uuid.uuid4())


def setup_logger(logname, filename, level=logging.WARNING):
    handler = logging.FileHandler("../logs/%s" % filename)
    logger = logging.getLogger(logname)
    logger.setLevel(level)
    logger.addHandler(handler)


def remove_none_from_dict(dictionary):
    if not isinstance(dictionary, dict):
        return dictionary

    return dict((k, remove_none_from_dict(v)) for k, v in dictionary.items() if v is not None)

