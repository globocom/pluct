from unittest import TestCase
from mock import patch, Mock

from pluct import resource, schema


class NewResourceTestCase(TestCase):
    @patch("requests.get")
    def setUp(self, get):
        self.data = {
            "name": "repos",
        }
        self.schema = schema.Schema(
            url="url.com"
        )
        self.headers = {
            'content-type': 'application/json; profile=url.com'
        }
        mock = Mock(json=self.data, headers=self.headers)
        get.return_value = mock
        self.url = "http://app.com/content"
        self.result = resource.get(url=self.url)
        self.result.data

    def test_get_should_returns_a_resource(self):
        self.assertIsInstance(self.result, resource.NewResource)

    def test_data(self):
        self.assertEqual(self.data, self.result.data)

    def test_schema(self):
        self.assertEqual(self.schema.url, self.result.schema.url)
