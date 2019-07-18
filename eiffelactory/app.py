import logging
import configparser
from kombu.utils import json

from eiffelactory.rabbitmq import RabbitMQConnection
from eiffelactory.artifactory import find_artifact
from eiffelactory.utils import setup_logger
from eiffelactory.eiffel import *

setup_logger('received', 'received.log', logging.INFO)
setup_logger('artifacts', 'artifacts.log', logging.INFO)
setup_logger('published', 'published.log', logging.INFO)

LOGGER_ARTIFACTS = logging.getLogger("artifacts")

CONFIG = configparser.ConfigParser()
CONFIG.read('../rabbitmq.config')
AF_SECTION = CONFIG['artifactory']
RMQ_SECTION = CONFIG['rabbitmq']

ARTIFACT_URL = AF_SECTION.get('url')


class App(object):

    def __init__(self):
        self.rmq_connection = RabbitMQConnection(self.on_message_received)

    def create_artifact_published_event(self, artc_id, artifact):
        location = '/%s/%s/%s/%s' % (ARTIFACT_URL, artifact.repo, artifact.path, artifact.name)
        data = ArtifactPublishedData([Location(location)])
        links = [Link[Link.ARTIFACT, artc_id]]
        meta = create_artifact_published_meta()
        event = Event(data, links, meta)

        return event

    def on_message_received(self, body):
        if not is_artifact_created_event(body):
            return

        artc_id = body['meta']['id']
        artifact = find_artifact(body)

        if artifact:
            LOGGER_ARTIFACTS.info(artifact + '\n\n')

            # commented out since we don't have publish permission yet
            # self.rmq_connection.publish_message(json.dumps(self.create_artifact_published_event(artc_id, artifact)))

    def run(self):
        self.rmq_connection.read_messages()


if __name__ == "__main__":
    app = App()
    app.run()
