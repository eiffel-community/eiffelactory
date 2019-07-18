from eiffelactory.eiffel import *
from eiffelactory.artifactory import parse_purl
from eiffelactory import utils

import unittest


class EiffelactoryTestSuite(unittest.TestCase):

    def test_create_eiffel_published_event(self):
        artc_event_id = '5de6f82d-52b6-44ae-bdbb-0be4fc213184'
        location = 'https://some.location/some-repo/some-path/artifact.txt'

        event = create_artifact_published_event(artc_event_id, [Location(location)])

        assert(event['meta']['type'] == 'EiffelArtifactPublishedEvent')
        assert(event['links'][0]['type'] == 'ARTIFACT')
        assert(event['links'][0]['target'] == '5de6f82d-52b6-44ae-bdbb-0be4fc213184')
        assert(event['data']['locations'][0]['type'] == 'ARTIFACTORY')
        assert(event['data']['locations'][0]['uri'] == 'https://some.location/some-repo/some-path/artifact.txt')

    def test_parse_identity_purl(self):
        purl = 'pkg:job/DEPT/job/USR/job/TEST/job/FOO/job/BAR_BAR/1234/artifacts/some_file.txt@1234'

        filename, build_url = parse_purl(purl)

        assert(filename == 'some_file.txt')
        assert(build_url == 'job/DEPT/job/USR/job/TEST/job/FOO/job/BAR_BAR/1234')

    def test_remove_none_from_dict(self):
        dictionary = {"test": None,
                      "test2": "not none",
                      "test3": {"nested": None, "nested2": "not none"}}

        clean = utils.remove_none_from_dict(dictionary)

        expected = {"test2": "not none", "test3": {"nested2": "not none"}}
        assert(clean == expected)

    def test_is_event_sent_from_sources(self):
        with_source_name = Meta(EIFFEL_ARTIFACT_CREATED_EVENT,
                                VERSION_3_0_0,
                                source=Source(name='JENKINS_EIFFEL_BROADCASTER'))

        with_wrong_source_name = Meta(EIFFEL_ARTIFACT_CREATED_EVENT,
                                      VERSION_3_0_0,
                                      source=Source(name='OTHER_SOURCE'))

        without_source = Meta(EIFFEL_ARTIFACT_CREATED_EVENT, VERSION_3_0_0)

        without_source_name = Meta(EIFFEL_ARTIFACT_CREATED_EVENT,
                                   VERSION_3_0_0,
                                   source=Source(host='some host'))

        event1 = {'data': {}, 'links': [], 'meta': with_source_name}
        event2 = {'data': {}, 'links': [], 'meta': with_wrong_source_name}
        event3 = {'data': {}, 'links': [], 'meta': without_source}
        event4 = {'data': {}, 'links': [], 'meta': without_source_name}

        assert(is_event_sent_from_sources(event1, [JENKINS_EIFFEL_BROADCASTER]))
        assert(is_event_sent_from_sources(event2, [JENKINS_EIFFEL_BROADCASTER, 'OTHER_SOURCE']))
        assert(not is_event_sent_from_sources(event2, [JENKINS_EIFFEL_BROADCASTER]))
        assert(not is_event_sent_from_sources(event3, [JENKINS_EIFFEL_BROADCASTER]))
        assert(not is_event_sent_from_sources(event4, [JENKINS_EIFFEL_BROADCASTER]))


if __name__ == '__main__':
    unittest.main()
