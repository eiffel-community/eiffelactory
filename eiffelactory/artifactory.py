"""
Module for querying Artifactory to confirm the presence of the artifacts from
the received Eiffel ArtC events.
"""
import configparser
import requests
from requests.auth import HTTPBasicAuth
from kombu.utils import json

CONFIG = configparser.ConfigParser()
CONFIG.read('../rabbitmq.config')

EIFFEL_ARTIFACT_CREATED_EVENT = "EiffelArtifactCreatedEvent"
AQL_DOMAIN_SEARCH_STRING = \
    'items.find({{"$or":[{{"artifact.name":"{}"}},{{"name":"{}"}}],' \
    '"artifact.module.build.url":{{"$match":"*{}*"}}}}).' \
    'include("name","repo","path")'
ARTIFACTORY_SEARCH_URL = CONFIG.get('artifactory', 'search_url')
ARTIFACTORY_USER = CONFIG.get('artifactory', 'username')
ARTIFACTORY_PASSWORD = CONFIG.get('artifactory', 'password')


def find_artifact(body):
    """
    Identifies if the received message is an ArtC and proceeds with parsing it
    and sending an AQL query to Artifactory
    :param body: the body of the received RabbitMQ messages
    """
    if body['meta']['type'] == EIFFEL_ARTIFACT_CREATED_EVENT:
        purl = body['data']['identity']
        find_artifact_on_artifactory(*parse_purl(purl))
        # print(str(body))


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

    # print(query_string)
    response = requests.post(ARTIFACTORY_SEARCH_URL,
                             auth=HTTPBasicAuth(ARTIFACTORY_USER,
                                                ARTIFACTORY_PASSWORD),
                             data=query_string)

    if response.status_code == 200:
        content = response.content.decode('utf-8')
        json_content = json.loads(content)
        results = json_content['results']
        return results
