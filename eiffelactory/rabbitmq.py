"""
Module for sending and receiving messages from RabbitMQ.
"""
import configparser
import signal
import sys

from kombu import Connection, Exchange, Queue

from artifactory import find_artifact

CONFIG = configparser.ConfigParser()
CONFIG.read('../rabbitmq.config')

USERNAME = CONFIG.get('rabbitmq', 'username')
PASSWORD = CONFIG.get('rabbitmq', 'password')
HOST = CONFIG.get('rabbitmq', 'host')
PORT = int(CONFIG.get('rabbitmq', 'port'))
VHOST = CONFIG.get('rabbitmq', 'vhost')
EXCHANGE = CONFIG.get('rabbitmq', 'exchange')
EXCHANGE_TYPE = CONFIG.get('rabbitmq', 'exchange_type')
ROUTING_KEY = CONFIG.get('rabbitmq', 'routing_key')
QUEUE = CONFIG.get('rabbitmq', 'queue')

EIFFEL_EXCHANGE = Exchange(EXCHANGE)
EIFFEL_QUEUE = Queue(QUEUE, routing_key=ROUTING_KEY)


class RabbitMQConnection:
    """
    Class handling receiving and publishing message on the RabbitMQ messages bus
    """
    def __init__(self):
        self.connection = Connection(transport='amqp',
                                     hostname=HOST,
                                     port=PORT,
                                     userid=USERNAME,
                                     password=PASSWORD,
                                     virtual_host=VHOST,
                                     ssl=True)
        self.connection.connect()
        self.producer = self.connection.Producer(serializer='json')
        self.consumer = self.connection.Consumer(
            EIFFEL_QUEUE,
            callbacks=[self.process_message])
        self.consuming = True
        signal.signal(signal.SIGINT, self.signal_handler)

    def process_message(self, body, message):
        """
        Callback called by consumer.
        :param body:
        :param message:
        :return:
        """
        find_artifact(body)
        message.ack()

    def publish_message(self, message):
        """
        Publishes passed message on the RabbitMQ message bus
        :param message:
        :return:
        """
        self.producer.publish(message,
                              retry=True,
                              retry_policy={
                                  'interval_start': 0,
                                  'interval_step': 2,
                                  'interval_max': 30,
                                  'max_retries': 30,
                              },
                              exchange=EIFFEL_EXCHANGE,
                              routing_key=ROUTING_KEY)

    def read_messages(self):
        """
        Method reading messages from the queue in a whilte-true loop. Callabck
        is defined in __init__
        :return:
        """
        with self.consumer:
            while self.consuming:
                self.connection.drain_events()

    def close_connection(self):
        """
        Closes the channels/connections.
        :return:
        """
        # for now called when you press Ctrl-C
        self.consuming = False
        self.producer.release()
        self.connection.release()

    def signal_handler(self, signal_received, frame):
        """
        Method for handling Ctrl-C. The two unused arguments have to be there,
        otherwise it won't work
        :param signal_received:
        :param frame:
        :return:
        """
        # closes down everything when Ctrl-C is pressed
        self.close_connection()
        print("\nExiting")
        sys.exit(0)


if __name__ == "__main__":
    # this is for easy testing
    mq = RabbitMQConnection()
    mq.read_messages()
