"""
Module for querying Artifactory to confirm the presence of the artifacts from
the received Eiffel ArtC events.
"""
import logging

import requests
from requests.auth import HTTPBasicAuth
from kombu.utils import json

from eiffelactory import config

LOGGER = logging.getLogger('artifacts')
CONFIG = config.Config().artifactory
ARTIFACTORY_SEARCH_URL = CONFIG.url + '/api/search/aql/'
AQL_DOMAIN_SEARCH_STRING = CONFIG.aql_search_string


def _format_aql_query(artifact_filename, build_path_substring):
    return AQL_DOMAIN_SEARCH_STRING.format(
        artifact_name=artifact_filename,
        build_path_substring=build_path_substring).replace('\n', '')


def _execute_aql_query(query_string):
    response = requests.post(ARTIFACTORY_SEARCH_URL,
                             auth=HTTPBasicAuth(CONFIG.username,
                                                CONFIG.password),
                             data=query_string)
    content = response.content.decode('utf-8')
    if response.status_code == 200:
        return content
    LOGGER.error("Artifactory error: %d, %s",
                 response.status_code, content)
    return None


def find_artifact_on_artifactory(artifact_filename, build_path_substring):
    """
    Queries Artifactory for the artifact, using the filename and the path
    substring from the purl, where it tries to match it with the build url
    present on Artifactory
    :param artifact_filename: tuple: the artifact filename
    :param build_path_substring: the substring from the build path
    :return:
    """
    query_string = _format_aql_query(artifact_filename, build_path_substring)
    LOGGER.debug(query_string)

    content = _execute_aql_query(query_string)

    if content:
        json_content = json.loads(content)
        results = json_content['results']
        LOGGER.debug(results)
        return results
    return None
