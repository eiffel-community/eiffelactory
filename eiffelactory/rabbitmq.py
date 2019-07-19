"""
Module for sending and receiving messages from RabbitMQ.
"""
from kombu import Connection, Exchange, Queue
from kombu.utils import json

from config import Config

# we can't declare new Exchanges yet so comment it out for now
CFG = Config().rabbitmq

EIFFEL_EXCHANGE = Exchange(CFG.exchange,
                           # durable=True,
                           # delivery_mode="persistent"
                           )


class RabbitMQConnection:
    """
    Class handling receiving and publishing message on the RabbitMQ messages bus
    """
    def __init__(self, message_callback):
        self.message_callback = message_callback

        self.exchange = Exchange(CFG.exchange)
        self.connection = Connection(transport='amqp',
                                     hostname=CFG.host,
                                     port=CFG.port,
                                     userid=CFG.username,
                                     password=CFG.password,
                                     virtual_host=CFG.vhost,
                                     ssl=True)

        self.connection.connect()
        self.producer = self.connection.Producer(serializer='json',
                                                 auto_declare=True)
        self.queue = Queue(channel=self.connection.channel(),
                           name=CFG.queue,
                           routing_key=CFG.routing_key)
        self.queue.declare()
        self.queue.bind_to(exchange=EIFFEL_EXCHANGE,
                           routing_key=CFG.routing_key)
        self.consumer = self.connection.\
            Consumer(
                    queues=self.queue,
                    callbacks=[self.handle_message],
                    prefetch_count=
                    CFG.prefetch_count)
        self.consuming = True

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
                              exchange=self.exchange,
                              routing_key=CFG.routing_key,
                              declare=[EIFFEL_EXCHANGE])

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

