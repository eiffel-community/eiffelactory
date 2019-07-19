"""
Module for querying Artifactory to confirm the presence of the artifacts from
the received Eiffel ArtC events.
"""
import configparser
import logging

import requests
from requests.auth import HTTPBasicAuth
from kombu.utils import json

from utils import setup_logger

CONFIG = configparser.ConfigParser()
CONFIG.read('../rabbitmq.config')
AF_SECTION = CONFIG['artifactory']

AQL_DOMAIN_SEARCH_STRING = \
    'items.find({{"$or":[{{"artifact.name":"{}"}},{{"name":"{}"}}],' \
    '"artifact.module.build.url":{{"$match":"*{}*"}}}}).' \
    'include("name","repo","path")'
ARTIFACTORY_URL = AF_SECTION.get('url')
ARTIFACTORY_SEARCH_URL = ARTIFACTORY_URL + '/api/search/aql/'
ARTIFACTORY_USER = AF_SECTION.get('username')
ARTIFACTORY_PASSWORD = AF_SECTION.get('password')

setup_logger('received', 'received.log', logging.INFO)
setup_logger('artifacts', 'artifacts.log', logging.INFO)
setup_logger('published', 'published.log', logging.INFO)

LOGGER_RECEIVED = logging.getLogger("received")


def find_artifact(body):
    """
    Identifies if the received message is an ArtC and proceeds with parsing it
    and sending an AQL query to Artifactory
    :param body: the body of the received RabbitMQ messages
    """
    purl = body['data']['identity']
    results = find_artifact_on_artifactory(*parse_purl(purl))
    if results:
        return results


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

    print(query_string)
    response = requests.post(ARTIFACTORY_SEARCH_URL,
                             auth=HTTPBasicAuth(ARTIFACTORY_USER,
                                                ARTIFACTORY_PASSWORD),
                             data=query_string)

    if response.status_code == 200:
        content = response.content.decode('utf-8')
        json_content = json.loads(content)
        results = json_content['results']
        return results
