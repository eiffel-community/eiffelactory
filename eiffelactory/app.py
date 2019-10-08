"""
Main module that starts RabbitMQ connection and publishes ArtifactPublished
events
"""
import logging
import signal
import sys
import os
import json

from eiffelactory import artifactory
from eiffelactory import config
from eiffelactory import eiffel
from eiffelactory import rabbitmq
from eiffelactory import utils

if not os.path.exists('logs'):
    os.makedirs('logs')


LOGGER_ARTIFACTS = utils.setup_event_logger('artifacts', 'artifacts.log',
                                            logging.DEBUG)
LOGGER_PUBLISHED = utils.setup_event_logger('published', 'published.log',
                                            logging.INFO)
LOGGER_RECEIVED = utils.setup_event_logger('received', 'received.log', logging.INFO)
LOGGER_APP = utils.setup_app_logger('app', 'eiffelactory.log', logging.DEBUG)

CFG = config.Config()


class App:
    """
    that starts RabbitMQ connection and publishes ArtifactPublished
    events
    """
    def __init__(self):
        self.rmq_connection = rabbitmq.RabbitMQConnection(CFG.rabbitmq,
                                                          self.on_event_received)
        self.artifactory_connection = artifactory.ArtifactoryConnection(
            CFG.artifactory)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def on_event_received(self, event):
        """
        Callback method passed to RabbitMQConnection and that processes
        received messages
        :param event: RabbitMQ message
        :return:
        """
        if not eiffel.is_artifact_created_event(event) or (
            CFG.eiffelactory.event_sources and
            not eiffel.is_sent_from_sources(event,
                                            CFG.eiffelactory.event_sources)):
            return

        LOGGER_RECEIVED.info(event)

        artc_meta_id = event['meta']['id']
        artc_data_identity = event['data']['identity']

        artifact = self.artifactory_connection.\
            find_artifact_on_artifactory(*utils.parse_purl(artc_data_identity))

        if artifact:
            if len(artifact) > 1:
                LOGGER_APP.error("AQL query returned '%d' artifacts",
                                 len(artifact))
                return
            else:
                self._publish_artp_event(artc_meta_id, artifact[0])

    def _publish_artp_event(self, artc_meta_id, artifact):
        """
        Creates and ArtifactPublished event and sends it to RabbitMQ exchange
        :param artc_meta_id: the id of ArtifactCreated event
        :param artifact: the results dictionary returned from Artifactory by the
        AQL query.
        """

        location = '{}/{}/{}/{}'.format(CFG.artifactory.url,
                                        artifact['repo'],
                                        artifact['path'],
                                        artifact['name'])

        artp_event = eiffel.create_artifact_published_event(
            artc_meta_id, [eiffel.Location(location)])

        artp_event_json = json.dumps(utils.remove_none_from_dict(artp_event))

        self.rmq_connection.publish_message(json.loads(artp_event_json))

        LOGGER_ARTIFACTS.info(artifact)
        LOGGER_PUBLISHED.info(artp_event_json)

    def run(self):
        """
        Starts the app by starting to listen to RabbitMQ messages.
        """
        self.rmq_connection.read_messages()

    def _signal_handler(self, signal_received, frame):
        """
        Method for handling Ctrl-C. The two unused arguments have to be there,
        otherwise it won't work
        :param signal_received:
        :param frame:
        :return:
        """
        self.rmq_connection.close_connection()
        sys.exit(0)
