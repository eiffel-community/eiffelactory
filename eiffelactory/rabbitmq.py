"""
Module for sending and receiving messages from RabbitMQ.
"""
import configparser
import signal
import sys

from kombu import Connection, Exchange, Queue
from kombu.utils import json

CONFIG = configparser.ConfigParser()
CONFIG.read('../rabbitmq.config')
RMQ_SECTION = CONFIG["rabbitmq"]

USERNAME = RMQ_SECTION.get('username')
PASSWORD = RMQ_SECTION.get('password')
HOST = RMQ_SECTION.get('host')
PORT = RMQ_SECTION.getint('port')
VHOST = RMQ_SECTION.get('vhost')
EXCHANGE = RMQ_SECTION.get('exchange')
EXCHANGE_TYPE = RMQ_SECTION.get('exchange_type')
ROUTING_KEY = RMQ_SECTION.get('routing_key')
QUEUE = RMQ_SECTION.get('queue')
PREFETCH_COUNT = RMQ_SECTION.getint("prefetch_count", 200)

EIFFEL_EXCHANGE = Exchange(EXCHANGE)
EIFFEL_QUEUE = Queue(QUEUE, routing_key=ROUTING_KEY)


class RabbitMQConnection:
    """
    Class handling receiving and publishing message on the RabbitMQ messages bus
    """
    def __init__(self, message_callback):
        self.message_callback = message_callback

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
            callbacks=[self.handle_message],
            prefetch_count=PREFETCH_COUNT)

        self.consuming = True
        signal.signal(signal.SIGINT, self.signal_handler)

    def handle_message(self, body, message):
        """
        Callback called by consumer.
        :param body:
        :param message:
        :return:
        """

        # body is sometimes dict and sometimes str
        # make sure it's a json dict before passing it on
        json_body = dict()
        if type(body) is dict:
            json_body = body
        elif type(body) is str:
            json_body = json.loads(body)

        self.message_callback(json_body)
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
        Method reading messages from the queue in a while-true loop.
        Callback is defined in __init__
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

