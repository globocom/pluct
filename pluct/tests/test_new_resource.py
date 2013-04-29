from unittest import TestCase
from mock import patch, Mock

from pluct import resource, schema



class NewResourceTestCase(TestCase):
    @patch("pluct.schema.get")
    @patch("requests.get")
    def setUp(self, get, schema_get):
        self.data = {
            "name": "repos",
        }
        self.schema = schema.Schema(
            url="url.com",
            links=[
                {
                    "href": "/apps/{name}/log",
                    "method": "GET",
                    "rel": "log"
                },
                {
                    "href": "/apps/{name}/env",
                    "method": "GET",
                    "rel": "env"
                }
            ]
        )
        schema_get.return_value = self.schema
        self.headers = {
            'content-type': 'application/json; profile=url.com'
        }
        mock = Mock(headers=self.headers)
        mock.json.return_value = self.data
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

    def test_methods(self):
        self.assertTrue(hasattr(self.result, "log"))
        self.assertTrue(hasattr(self.result, "env"))
