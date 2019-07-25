"""
Config module for handling the eiffelactory.config file.
Wraps the different sections in the config file in their own classes
and exposes options as object properties in order to take advantage of
dot.notation.

This allows for safer and easier access of config options.

Parses option strings into collections or other formats if needed.
"""
import configparser

_DEFAULT_AQL_SEARCH_STRING = 'items.find({{"artifact.name":"{artifact_name}",' \
                             '"artifact.module.build.url":{{"$match":"*{' \
                             'build_path_substring}*"}}}}).include("name",' \
                             '"repo","path")'

DEFAULT_CONFIG_FILENAME = 'conf/eiffelactory.config'

DEFAULT_CONFIG_OPTIONS = {
    'prefetch_count': '50',
    'vhost': '/',
    'routing_key': '#',
    'event_sources': None,
    'aql_search_string': _DEFAULT_AQL_SEARCH_STRING
}


class Config:
    """
    Holds all the different config sections.
    """

    def __init__(self, filename=DEFAULT_CONFIG_FILENAME):
        self._config = configparser.ConfigParser(defaults=DEFAULT_CONFIG_OPTIONS)
        self._config.read(filename)

        self.rabbitmq = RabbitMQConfig(self._config, 'rabbitmq')
        self.artifactory = ArtifactoryConfig(self._config, 'artifactory')
        self.eiffelactory = EiffelactoryConfig(self._config, 'eiffelactory')


class ConfigSection:
    """
    Wrapper parent class for easier and safer extraction of configs from
    the config file. Wraps a single config section.

    :param section: the config section
    """

    def __init__(self, config, section):
        self._config = config
        self._section = section

        if not self._config.has_section(section):
            self._config.add_section(section)

    def get(self, key):
        return self._config.get(self._section, key)

    def getint(self, key):
        return self._config.getint(self._section, key)

    def getboolean(self, key):
        return self._config.getboolean(self._section, key)


class RabbitMQConfig(ConfigSection):
    """
    Wraps the rabbitmq section of the config file for easier and safer
    extraction of RabbitMQ related options.
    """

    def __init__(self, config, section):
        super().__init__(config, section)

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
        return self.getint('port')

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
        return self.get('routing_key')

    @property
    def vhost(self):
        return self.get('vhost')

    @property
    def prefetch_count(self):
        return self.getint('prefetch_count')


class ArtifactoryConfig(ConfigSection):
    """
    Wraps the artifactory section of the config file for easier and safer
    extraction of artifactory related options.
    """

    def __init__(self, config, section):
        super().__init__(config, section)

    @property
    def username(self):
        return self.get('username')

    @property
    def password(self):
        return self.get('password')

    @property
    def url(self):
        return self.get('url')

    @property
    def aql_search_string(self):
        return self.get('aql_search_string')


class EiffelactoryConfig(ConfigSection):
    """
    Wraps the eiffelactory section of the config file for easier and safer
    extraction of app related options.
    """

    def __init__(self, config, section):
        super().__init__(config, section)

    @property
    def event_sources(self):
        event_sources = self.get('event_sources')
        if event_sources:
            return event_sources.replace(' ', '').split(',')
        return None
