"""
Utils module used by other classes in the app for parsing purl, creating
timestamps, etc.
"""
import logging
import time


def current_time_millis():
    """
    Convenience method for getting the current time in milliseconds.
    :return: UNIX Epoch time, in milliseconds.
    """
    return int(round(time.time() * 1000))


def setup_logger(logname, filename, level=logging.WARNING):
    """
    Creates a logger with a file handler.

    :param logname: the name of the logger
    :param filename: the filename to log to
    :param level: the minimum log level
    """
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
    handler = logging.FileHandler("logs/%s" % filename)
    handler.setFormatter(formatter)
    logger = logging.getLogger(logname)
    logger.setLevel(level)
    logger.addHandler(handler)


def remove_none_from_dict(dictionary):
    """
    Recursively removes None values from a dictionary
    :param dictionary: the dictionary to clean
    :return: a copy of the dictionary with None values removed
    """
    if not isinstance(dictionary, dict):
        return dictionary

    return {k: remove_none_from_dict(v)
            for k, v in dictionary.items()
            if v is not None}


def parse_purl(purl):
    """
    Finds the purl in the body of the Eiffel event message and parses it
    :param purl: the purl from the Eiffel ArtC event
    :return: tuple: the artifact filename and the substring from the build path
    """
    # pkg:<build_path>/<intermediate_directories>/
    # <artifact_filename>@< build_number >
    # artifact_filename_and_build = purl.split('/')[-1]
    # artifact_filename = artifact_filename_and_build.split('@')[0]
    # build_path = purl.split('pkg:')[1].split('/artifacts')[0]

    # pkg:<intermediate_directories>/<artifact_filename>@<build_number>?
    # build_path=< build_path >
    # for when Eiffel Broadcaster is updated
    artifact_filename = purl.split('@')[0].split('/')[-1]
    build_path = purl.split('?build_path=')[-1]
    return artifact_filename, build_path
