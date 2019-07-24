import unittest
from eiffelactory import config


class ConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.config = config.Config("tests/all_options.config")
        self.no_default_options = config.Config(
            'tests/no_default_options.config')

    def test_option_event_sources_should_be_parsed_to_list(self):
        event_sources = self.config.eiffelactory.event_sources

        self.assertIs(type(event_sources), list)
        self.assertEqual(len(event_sources), 3)
        self.assertEqual(event_sources[0], "JENKINS_EIFFEL_BROADCASTER")
        self.assertEqual(event_sources[1], "EVENT-source_2")
        self.assertEqual(event_sources[2], "eventSource3")

    def test_returns_default_values_if_option_is_missing(self):
        cfg = self.no_default_options
        defaults = config.DEFAULT_CONFIG_OPTIONS

        self.assertIs(cfg.rabbitmq.prefetch_count,
                      int(defaults['prefetch_count']))

        self.assertIs(cfg.rabbitmq.vhost, defaults['vhost'])
        self.assertIs(cfg.rabbitmq.routing_key, defaults['routing_key'])
        self.assertIs(cfg.eiffelactory.event_sources, defaults['event_sources'])
        self.assertIs(cfg.artifactory.aql_search_string,
                      defaults['aql_search_string'])

    def test_missing_sections_are_added(self):
        cfg = self.no_default_options

        self.assertTrue(cfg._config.has_section('eiffelactory'))

    def test_port_is_int(self):
        port = self.config.rabbitmq.port

        self.assertIs(type(port), int)

    def test_prefetch_count_is_int(self):
        prefetch_count = self.config.rabbitmq.prefetch_count

        self.assertIs(type(prefetch_count), int)

    def tearDown(self):
        self.config = None
        self.no_default_options = None


if __name__ == '__main__':
    unittest.main()
