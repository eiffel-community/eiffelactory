"""
Config module for handling the eiffelactory.config file.
Wraps the different sections in the config file in their own classes
and exposes options as object properties in order to take advantage of
dot.notation and auto-completion.

This allows for safer and easier access of config options.

Parses option strings into collections or other formats if needed.
"""
import configparser

CONFIG = configparser.ConfigParser()
CONFIG.read('eiffelactory.config')

CONFIG_RABBITMQ = CONFIG['rabbitmq']
CONFIG_ARTIFACTORY = CONFIG['artifactory']
CONFIG_EIFFELACTORY = CONFIG['eiffelactory']


class Config:
    """
    Holds all the different config sections.
    """

    def __init__(self):
        self.rabbitmq = RabbitMQConfig()
        self.artifactory = ArtifactoryConfig()
        self.eiffelactory = EiffelactoryConfig()


class ConfigSection:
    """
    Wrapper parent class for easier and safer extraction of configs from
    the config file. Wraps a single config section.

    Strings always fallback to empty strings
    while int and booleans always fallback to None.

    :param section: the config section
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
    Wraps the rabbitmq section of the config file for easier and safer
    extraction of RabbitMQ related options.
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
    Wraps the artifactory section of the config file for easier and safer
    extraction of artifactory related options.
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
    Wraps the eiffelactory section of the config file for easier and safer
    extraction of app related options.
    """

    def __init__(self):
        super().__init__(CONFIG_EIFFELACTORY)

    @property
    def event_sources(self):
        return self.get('event_sources').replace(' ', '').split(',')
