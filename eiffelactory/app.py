import logging

from eiffelactory.rabbitmq import RabbitMQConnection
from eiffelactory.artifactory import find_artifact
from eiffelactory.utils import setup_logger

setup_logger('received', 'received.log', logging.INFO)
setup_logger('artifacts', 'artifacts.log', logging.INFO)
setup_logger('published', 'published.log', logging.INFO)

LOGGER_ARTIFACTS = logging.getLogger("artifacts")


class App(object):

    def __init__(self):
        self.rmq_connection = RabbitMQConnection(self.on_message_received)

    def on_message_received(self, body):
        artifact = find_artifact(body)

        if artifact:
            LOGGER_ARTIFACTS.info(artifact + '\n\n')

    def run(self):
        self.rmq_connection.read_messages()


if __name__ == "__main__":
    app = App()
    app.run()
