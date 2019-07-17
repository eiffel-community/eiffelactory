from eiffelactory import dummy, eiffel


import unittest
import json


class EiffelactoryTestSuite(unittest.TestCase):

    # all tests names must start with "test_"
    def test_dummy_is_true(self):
        assert dummy.dummy()

    def test_create_eiffel_published_event(self):
        data = eiffel.ArtifactPublishedData([eiffel.Location("https://some.location/artifact.txt")])
        links = [eiffel.Link(eiffel.Link.ARTIFACT, "1234-1234-1234-1234")]
        meta = eiffel.create_artifact_published_meta()

        event = eiffel.Event(data, links, meta)

        assert(event['meta']['type'] == eiffel.EIFFEL_ARTIFACT_PUBLISHED_EVENT)


if __name__ == '__main__':
    unittest.main()
