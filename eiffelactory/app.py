import configparser
import logging
from kombu.utils import json

from eiffelactory.artifactory import find_artifact
from eiffelactory.eiffel import *
from eiffelactory.rabbitmq import RabbitMQConnection
from eiffelactory.utils import setup_logger

setup_logger('received', 'received.log', logging.INFO)
setup_logger('artifacts', 'artifacts.log', logging.INFO)
setup_logger('published', 'published.log', logging.INFO)

LOGGER_ARTIFACTS = logging.getLogger('artifacts')
LOGGER_PUBLISHED = logging.getLogger('published')
LOGGER_RECEIVED = logging.getLogger('received')

CONFIG = configparser.ConfigParser()
CONFIG.read('../rabbitmq.config')
AF_SECTION = CONFIG['artifactory']
RMQ_SECTION = CONFIG['rabbitmq']
EA_SECTION = CONFIG['eiffelactory']

ARTIFACT_URL = AF_SECTION.get('url')
EVENT_SOURCES = EA_SECTION.get('event_sources', '').replace(' ', '').split()


class App(object):

    def __init__(self):
        self.rmq_connection = RabbitMQConnection(self.on_message_received)

    def on_message_received(self, event_json):
        if not is_artifact_created_event(event_json):
            return

        if EVENT_SOURCES:
            if not is_event_sent_from_sources(event_json, EVENT_SOURCES):
                return

        LOGGER_RECEIVED.info(event_json)

        artc_event_id = event_json['meta']['id']
        artifact = find_artifact(event_json)

        if artifact:
            LOGGER_ARTIFACTS.info(artifact + '\n\n')

            location = '%s/%s/%s/%s' % (ARTIFACT_URL, artifact.repo, artifact.path, artifact.name)
            artifact_published_event = create_artifact_published_event(artc_event_id, [Location(location)])

            LOGGER_PUBLISHED.info(json.dumps(artifact_published_event))
            # commented out since we don't have publish permission yet
            # self.rmq_connection.publish_message(json.dumps(artifact_published_event))

    def run(self):
        self.rmq_connection.read_messages()


if __name__ == "__main__":
    app = App()
    app.run()
