import unittest
from unittest import mock

from eiffelactory import artifactory

artifact_filename = 'artifact.txt'
build_path_substring = 'job/TEST/job/BUILD_NAME/255'
query_string =\
    'items.find({"artifact.name":"artifact.txt",' \
    '"artifact.module.build.url":' \
    '{"$match":"*job/TEST/job/BUILD_NAME/255*"}}' \
    ').include("name","repo","path")'
wrong_query_string = \
    'items.find({"artifact.name":"wrong_file.txt",' \
    '"artifact.module.build.url":' \
    '{"$match":"*job/TEST/job/BUILD_NAME/255*"}}' \
    ').include("name","repo","path")'
bad_query_string = \
    'items.find({"artifact.name":"{"file.txt"}"},' \
    '"artifact.module.build.url":' \
    '{"$match":"*{"job/TEST/job/BUILD_NAME/255"}*"}}' \
    ').include("name","repo","path")'
response_dict = \
    '{"results":[{"path":"eiffelactory","repo":"repo","name":"artifact.txt"}]}'
empty_dict = '{"results":[]}'
response_dict_binary = str.encode(response_dict)
empty_response_dict = str.encode(empty_dict)


def mocked_requests_post(search_url, auth, data):
    class MockedPostResponse:
        def __init__(self, status_code, content):
            self.content = content
            self.status_code = status_code

    if data == query_string:
        return MockedPostResponse(status_code=200,
                                  content=response_dict_binary)
    elif data == wrong_query_string:
        # imitating that the item was not found, but not that the query is
        # malformed
        return MockedPostResponse(status_code=200, content=empty_response_dict)
    elif data == bad_query_string:
        return MockedPostResponse(status_code=400,
                                  content=b'Failed to parse query')


class TestArtifactory(unittest.TestCase):

    def test__format_aql_query(self):
        print(artifactory._format_aql_query(
            artifact_filename, build_path_substring))
        self.assertEqual(artifactory._format_aql_query(
            artifact_filename, build_path_substring),
            query_string)

    @mock.patch('eiffelactory.artifactory.requests.post',
                side_effect=mocked_requests_post)
    def test__execute_aql_query(self, mocked_post):
        response_content = artifactory._execute_aql_query(query_string)
        self.assertEqual(response_content, response_dict)

        response_content = artifactory._execute_aql_query(wrong_query_string)
        self.assertEqual(response_content, empty_dict)

        response_content = artifactory._execute_aql_query(bad_query_string)
        self.assertEqual(response_content, None)

    @mock.patch('eiffelactory.artifactory.requests.post',
                side_effect=mocked_requests_post)
    def test_find_artifact_on_artifactory(self, mocked_post):
        result = artifactory.\
            find_artifact_on_artifactory(artifact_filename,
                                         build_path_substring)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], artifact_filename)

        artifact_filename2 = 'wrong_file.txt'
        result = artifactory.\
            find_artifact_on_artifactory(artifact_filename2,
                                         build_path_substring)
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()


