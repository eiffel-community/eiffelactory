"""
Config module for prettier logging across the classes in the app
"""
import configparser

CONFIG = configparser.ConfigParser()
CONFIG.read('eiffelactory.config')

CONFIG_RABBITMQ = CONFIG['rabbitmq']
CONFIG_ARTIFACTORY = CONFIG['artifactory']
CONFIG_EIFFELACTORY = CONFIG['eiffelactory']


class Config:
    """
    for prettier logging across the classes in the app
    """
    def __init__(self):
        self.config = CONFIG
        self.rabbitmq = RabbitMQConfig()
        self.artifactory = ArtifactoryConfig()
        self.eiffelactory = EiffelactoryConfig()


class ConfigSection:
    """
    Wrapper parent class for easier and safer extraction of configs from
    the config file
    """
    def __init__(self, section):
        self.section = section

    def get(self, key, default=''):
        return self.section.get(key, fallback=default)

    def getint(self, key, default=None):
        return self.section.getint(key, fallback=default)

    def getbool(self, key, default=None):
        return self.section.getboolean(key, fallback=default)


class RabbitMQConfig(ConfigSection):
    """
    Child of ConfigSection for easier and safer extraction of RabbitMQ-related
    configs from the config file
    """
    DEFAULT_ROUTING_KEY = '#'
    DEFAULT_VHOST = '/'
    DEFAULT_PREFETCH_COUNT = '50'

    def __init__(self):
        super().__init__(CONFIG_RABBITMQ)

    @property
    def username(self):
        return self.get('username')

    @property
    def password(self):
        return self.get('password')

    @property
    def host(self):
        return self.get('host')

    @property
    def port(self):
        return self.get('port')

    @property
    def exchange(self):
        return self.get('exchange')

    @property
    def exchange_type(self):
        return self.get('exchange_type')

    @property
    def queue(self):
        return self.get('queue')

    @property
    def routing_key(self):
        return self.get('routing_key', self.DEFAULT_ROUTING_KEY)

    @property
    def vhost(self):
        return self.get('vhost', self.DEFAULT_VHOST)

    @property
    def prefetch_count(self):
        return self.getint('prefetch_count', self.DEFAULT_PREFETCH_COUNT)


class ArtifactoryConfig(ConfigSection):
    """
    Child of ConfigSection for easier and safer extraction of Artifactory-
    related configs from the config file
    """
    def __init__(self):
        super().__init__(CONFIG_ARTIFACTORY)

    @property
    def username(self):
        return self.get('username')

    @property
    def password(self):
        return self.get('password')

    @property
    def url(self):
        return self.get('url')


class EiffelactoryConfig(ConfigSection):
    """
    Child of ConfigSection for easier and safer extraction of related
    configs specifically for this plugin from the config file
    """
    def __init__(self):
        super().__init__(CONFIG_EIFFELACTORY)

    @property
    def event_sources(self):
        return self.get('event_sources').replace(' ', '').split()
