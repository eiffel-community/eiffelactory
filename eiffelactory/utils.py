import logging
import time
import uuid


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

    return dict((k, remove_none_from_dict(v))
                for k, v in dictionary.items()
                if v is not None)


def parse_purl(purl):
    """
    Finds the purl in the body of the Eiffel event message and parses it
    :param purl: the purl from the Eiffel ArtC event
    :return: tuple: the artifact filename and the substring from the build path
    """
    artifact_filename_and_build = purl.split("/")[-1]
    artifact_filename = artifact_filename_and_build.split("@")[0]
    build_path_substring = purl.split("pkg:")[1].split("/artifacts")[0]
    return artifact_filename, build_path_substring
