from eiffelactory.eiffel import *

import unittest


class EiffelactoryTestSuite(unittest.TestCase):

    def test_create_eiffel_published_event(self):
        data = ArtifactPublishedData([Location("https://some.location/artifact.txt")])
        links = [Link(Link.ARTIFACT, "1234-1234-1234-1234")]
        meta = create_artifact_published_meta()

        event = Event(data, links, meta)
        assert(event['meta']['type'] == EIFFEL_ARTIFACT_PUBLISHED_EVENT)


if __name__ == '__main__':
    unittest.main()
