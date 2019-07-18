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

