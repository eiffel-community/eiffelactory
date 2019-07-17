import configparser
import signal
import sys

from kombu import Connection, Exchange, Queue

cfg = configparser.ConfigParser()
cfg.read('../rabbitmq.config')

username = cfg.get('rabbitmq', 'username')
password = cfg.get('rabbitmq', 'password')
host = cfg.get('rabbitmq', 'host')
port = int(cfg.get('rabbitmq', 'port'))
vhost = cfg.get('rabbitmq', 'vhost')
exchange = cfg.get('rabbitmq', 'exchange')
exchange_type = cfg.get('rabbitmq', 'exchange_type')
routing_key = cfg.get('rabbitmq', 'routing_key')
queue = cfg.get('rabbitmq', 'queue')

eiffel_exchange = Exchange(exchange)
eiffel_queue = Queue(queue, routing_key=routing_key)


class RabbitMQConnection:
    """
    Class handling receiving and publishing message on the RabbitMQ messages bus
    """
    def __init__(self):
        self.connection = Connection(transport='amqp',
                                     hostname=host,
                                     port=port,
                                     userid=username,
                                     password=password,
                                     virtual_host=vhost,
                                     ssl=True)
        self.connection.connect()
        self.producer = self.connection.Producer(serializer='json')
        self.consumer = self.connection.Consumer(
            eiffel_queue,
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
        print(body)
        print(message)
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
                              exchange=eiffel_exchange,
                              routing_key=routing_key)

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
        # closes down everything when Ctrl-C is pressed
        self.close_connection()
        print("\nExiting")
        sys.exit(0)


if __name__ == "__main__":
    # this is for easy testing
    mq = RabbitMQConnection()
    mq.publish_message("Test Eiffelactory")
    mq.read_messages()
