"""
Module for querying Artifactory to confirm the presence of the artifacts from
the received Eiffel ArtC events.
"""
import logging

import requests
from kombu.utils import json
from requests.auth import HTTPBasicAuth

from config import Config

LOGGER = logging.getLogger('artifacts')

CONFIG = Config().artifactory

ARTIFACTORY_SEARCH_URL = CONFIG.url + '/api/search/aql/'

AQL_DOMAIN_SEARCH_STRING = \
    'items.find({{"$or":[{{"artifact.name":"{}"}},{{"name":"{}"}}],' \
    '"artifact.module.build.url":{{"$match":"*{}*"}}}}).' \
    'include("name","repo","path")'


def find_artifact_on_artifactory(artifact_filename, build_path_substring):
    """
    Queries Artifactory for the artifact, using the filename and the path
    substring from the purl, where it tries to match it with the build url
    present on Artifactory
    :param artifact_filename: tuple: the artifact filename
    :param build_path_substring: the substring from the build path
    :return:
    """
    query_string = AQL_DOMAIN_SEARCH_STRING.format(artifact_filename,
                                                   artifact_filename,
                                                   build_path_substring)
    LOGGER.debug(query_string)

    response = requests.post(ARTIFACTORY_SEARCH_URL,
                             auth=HTTPBasicAuth(CONFIG.username,
                                                CONFIG.password),
                             data=query_string)

    if response.status_code == 200:
        content = response.content.decode('utf-8')
        json_content = json.loads(content)
        results = json_content['results']
        LOGGER.debug(results)
        return results
