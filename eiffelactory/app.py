import logging

from kombu.utils import json

from artifactory import find_artifact_on_artifactory
from config import Config
from eiffel import *
from rabbitmq import RabbitMQConnection
from utils import setup_logger, parse_purl

setup_logger('received', 'received.log', logging.INFO)
setup_logger('artifacts', 'artifacts.log', logging.DEBUG)
setup_logger('published', 'published.log', logging.INFO)

LOGGER_ARTIFACTS = logging.getLogger('artifacts')
LOGGER_PUBLISHED = logging.getLogger('published')
LOGGER_RECEIVED = logging.getLogger('received')

CFG = Config()


class App(object):

    def __init__(self):
        self.rmq_connection = RabbitMQConnection(self.on_event_received)

    def on_event_received(self, event):
        if not is_artifact_created_event(event):
            return

        LOGGER_RECEIVED.info(event)

        if CFG.eiffelactory.event_sources:
            if not is_event_sent_from_sources(
                    event, CFG.eiffelactory.event_sources):
                return

        artc_meta_id = event['meta']['id']
        artc_data_identity = event['data']['identity']

        artifact = find_artifact_on_artifactory(*parse_purl(artc_data_identity))

        if artifact:
            LOGGER_ARTIFACTS.info(artifact + '\n\n')

            location = '%s/%s/%s/%s' % (CFG.artifactory.url,
                                        artifact.repo,
                                        artifact.path,
                                        artifact.name)

            artifact_published_event = create_artifact_published_event(
                artc_meta_id, [Location(location)])

            LOGGER_PUBLISHED.info(json.dumps(artifact_published_event))
            # commented out since we don't have publish permission yet
            # self.rmq_connection.publish_message(json.dumps(artifact_published_event))

    def run(self):
        self.rmq_connection.read_messages()


if __name__ == "__main__":
    app = App()
    app.run()
