import unittest
from eiffelactory import rabbitmq


def on_event_received(event):
    print(str(event))


class TestRabbitMQ(unittest.TestCase):
    def setUp(self):
        self.rabbitmq_connection = rabbitmq.RabbitMQConnection(
            on_event_received)

    def test_close_connection(self):
        # not really a unit test :/
        self.rabbitmq_connection.close_connection()
        self.assertFalse(self.rabbitmq_connection.connection.connected)

    def tearDown(self):
        self.rabbitmq_connection = None
