from unittest import TestCase
from mock import patch, Mock

from pluct import schema


class SchemaTestCase(TestCase):
    @patch("requests.get")
    def setUp(self, get):
        self.data = {
            "title": "app schema",
            "properties": {
                "cname": {"type": "string"},
                "ip": {"type": "string"},
                "name": {"type": "string"},
                "platform": {"type": "string"}
            },
            "links": [
                {
                    "href": "/apps/{name}/log",
                    "method": "GET",
                    "rel": "log"
                },
                {
                    "href": "/apps/{name}/env",
                    "method": "GET",
                    "rel": "get envs"
                }
            ],
            "required": ["platform", "name"],
        }
        mock = Mock(json=self.data)
        get.return_value = mock
        self.url = "http://app.com/myschema"
        self.result = schema.get(url=self.url)

    def test_get_should_returns_a_schema(self):
        self.assertIsInstance(self.result, schema.Schema)

    def test_schema_required(self):
        self.assertListEqual(self.data["required"], self.result.required)

    def test_schema_title(self):
        self.assertEqual(self.data["title"], self.result.title)

    def test_schema_properties(self):
        self.assertDictEqual(self.data["properties"], self.result.properties)

    def test_schema_links(self):
        self.assertListEqual(self.data["links"], self.result.links)

    def test_schema_url(self):
        self.assertEqual(self.url, self.result.url)
