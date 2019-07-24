import unittest

from eiffelactory import eiffel


class EiffelTestCase(unittest.TestCase):

    def test_create_eiffel_published_event(self):
        artc_meta_id = '5de6f82d-52b6-44ae-bdbb-0be4fc213184'
        location = 'https://some.location/some-repo/some-path/artifact.txt'

        event = eiffel.create_artifact_published_event(artc_meta_id,
                                                       [eiffel.Location(
                                                           location)])

        self.assertEqual(event['meta']['type'], 'EiffelArtifactPublishedEvent')
        self.assertEqual(event['meta']['version'], '3.0.0')
        self.assertEqual(event['meta']['source']['name'], 'EIFFELACTORY')
        self.assertEqual(event['links'][0]['type'], 'ARTIFACT')
        self.assertEqual(event['links'][0]['target'],
                         '5de6f82d-52b6-44ae-bdbb-0be4fc213184')
        self.assertEqual(event['data']['locations'][0]['type'], 'ARTIFACTORY')
        self.assertEqual(event['data']['locations'][0]['uri'],
                         'https://some.location/some-repo/'
                         'some-path/artifact.txt')

    def test_is_eiffel_event_type(self):
        event = {'links': [],
                 'meta': {
                     'version': '2.0.0',
                     'time': 1563540212984,
                     'type': 'EiffelArtifactCreatedEvent',
                     'id': '3cb709fa-3ae8-4d6e-bdf4-cf86h654gf5e'},
                 'data': {
                     'identity': 'pkg:job/DIR/job/DIR/job/DIR/job/'
                                 'PROJECT/8/artifacts/whatever.zip@8'}}
        event_type = 'EiffelArtifactCreatedEvent'

        self.assertTrue(eiffel.is_eiffel_event_type(event, event_type))

    def test_is_artifact_created_event(self):
        event = {'links': [],
                 'meta': {
                     'version': '2.0.0',
                     'time': 1563540212984,
                     'type': 'EiffelArtifactCreatedEvent',
                     'id': '3cb709fa-3ae8-4d6e-bdf4-cf86h654gf5e'},
                 'data': {
                     'identity': 'pkg:job/DIR/job/DIR/job/DIR/job/PROJECT/8/'
                                 'artifacts/whatever.zip@8'}}

        self.assertTrue(eiffel.is_artifact_created_event(event))

    def test_is_event_sent_from_sources(self):
        with_source_name = eiffel.Meta(eiffel.EIFFEL_ARTIFACT_CREATED_EVENT,
                                       eiffel.VERSION_3_0_0,
                                       source=eiffel.Source(
                                           name='JENKINS_EIFFEL_BROADCASTER'))

        with_wrong_source_name = eiffel.Meta(
            eiffel.EIFFEL_ARTIFACT_CREATED_EVENT,
            eiffel.VERSION_3_0_0,
            source=eiffel.Source(name='OTHER_SOURCE'))

        without_source = eiffel.Meta(eiffel.EIFFEL_ARTIFACT_CREATED_EVENT,
                                     eiffel.VERSION_3_0_0)

        without_source_name = eiffel.Meta(eiffel.EIFFEL_ARTIFACT_CREATED_EVENT,
                                          eiffel.VERSION_3_0_0,
                                          source=eiffel.Source(
                                              host='some host'))

        event1 = {'data': {}, 'links': [], 'meta': with_source_name}
        event2 = {'data': {}, 'links': [], 'meta': with_wrong_source_name}
        event3 = {'data': {}, 'links': [], 'meta': without_source}
        event4 = {'data': {}, 'links': [], 'meta': without_source_name}

        self.assertTrue(eiffel.is_sent_from_sources(
            event1, ['JENKINS_EIFFEL_BROADCASTER']))
        self.assertTrue(eiffel.is_sent_from_sources(
            event2, ['JENKINS_EIFFEL_BROADCASTER', 'OTHER_SOURCE']))
        self.assertFalse(eiffel.is_sent_from_sources(
            event2, ['JENKINS_EIFFEL_BROADCASTER']))
        self.assertFalse(eiffel.is_sent_from_sources(
            event3, ['JENKINS_EIFFEL_BROADCASTER']))
        self.assertFalse(eiffel.is_sent_from_sources(
            event4, ['JENKINS_EIFFEL_BROADCASTER']))


if __name__ == '__main__':
    unittest.main()
