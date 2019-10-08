"""
Module for sending and receiving messages from RabbitMQ.
"""
import logging

from kombu import Connection, Exchange, Queue
from kombu.utils import json


class RabbitMQConnection:
    """
    Class handling receiving and publishing message on the RabbitMQ messages bus
    """
    def __init__(self,  rabbitmq_config, message_callback):
        self.rabbitmq_config = rabbitmq_config
        self.app_logger = logging.getLogger('app')
        self.message_callback = message_callback

        self.exchange = Exchange(self.rabbitmq_config.exchange)
        self.connection = Connection(transport='amqp',
                                     hostname=self.rabbitmq_config.host,
                                     port=self.rabbitmq_config.port,
                                     userid=self.rabbitmq_config.username,
                                     password=self.rabbitmq_config.password,
                                     virtual_host=self.rabbitmq_config.vhost,
                                     ssl=True)

        self.connection.connect()
        self.producer = self.connection.Producer(serializer='json',
                                                 auto_declare=True)
        self.queue = Queue(channel=self.connection.channel(),
                           name=self.rabbitmq_config.queue,
                           routing_key=self.rabbitmq_config.routing_key)
        self.queue.declare()
        self.queue.bind_to(exchange=Exchange(self.rabbitmq_config.exchange),
                           routing_key=self.rabbitmq_config.routing_key)
        self.consumer = self.connection.\
            Consumer(
                    queues=self.queue,
                    callbacks=[self._handle_message],
                    prefetch_count=
                    self.rabbitmq_config.prefetch_count,
                    tag_prefix=self.rabbitmq_config.consumer_tag)
        self.consuming = True

    def _handle_message(self, body, message):
        """
        Callback called by consumer.
        :param body:
        :param message:
        :return:
        """
        # body is sometimes dict and sometimes str
        # make sure it's a json dict before passing it on
        json_body = dict()
        if isinstance(body, dict):
            json_body = body
        elif isinstance(body, str):
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
                              exchange=self.exchange,
                              routing_key=self.rabbitmq_config.routing_key)

    def read_messages(self):
        """
        Method reading messages from the queue in a while-true loop.
        Callback is defined in __init__
        :return:
        """
        with self.consumer:
            self.app_logger.info("Consumer is starting to consume"
                                 " RabbitMQ messages.")
            while self.consuming:
                self.connection.drain_events()
            self.app_logger.info("Consumer is stopping consuming"
                                 "RabbitMQ messages.")
        self.app_logger.info("Consumer stopped consuming RabbitMQ messages.")

    def close_connection(self):
        """
        Closes the channels/connections.
        :return:
        """
        # for now called when you press Ctrl-C
        self.consuming = False
        self.producer.release()
        self.connection.release()
        self.app_logger.info("SIGINT/SIGTERM received. "
                             "Closing RabbiMQ connection.")
