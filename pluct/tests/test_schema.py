from unittest import TestCase
from mock import patch, Mock

from pluct import schema


class SchemaTestCase(TestCase):
    def setUp(self):
        self.data = {
            "title": "app schema",
            "properties": {
                "cname": {"type": "string"},
                "ip": {"type": "string"},
                "name": {"type": "string"},
                "platform": {"type": "string"}
            },
            "required": ["platform", "name"],
        }

    @patch("requests.get")
    def test_get_should_returns_a_schema(self, get):
        instance = schema.get(url="http://myapp.com/schema/myschema")
        self.assertIsInstance(instance, schema.Schema)

    @patch("requests.get")
    def test_schema_required(self, get):
        mock = Mock()
        mock.json = self.data
        get.return_value = mock
        s = schema.get(url="http://myapp.com/schema/myschema")
        required = ["platform", "name"]
        self.assertListEqual(required, s.required)

    @patch("requests.get")
    def test_schema_title(self, get):
        mock = Mock()
        mock.json = self.data
        get.return_value = mock
        s = schema.get(url="http://myapp.com/schema/myschema")
        title = "app schema"
        self.assertEqual(title, s.title)

    @patch("requests.get")
    def test_schema_properties(self, get):
        mock = Mock()
        mock.json = self.data
        get.return_value = mock
        s = schema.get(url="http://myapp.com/schema/myschema")
        properties = {
            "cname": {"type": "string"},
            "ip": {"type": "string"},
            "name": {"type": "string"},
            "platform": {"type": "string"}
        }
        self.assertDictEqual(properties, s.properties)

    @patch("requests.get")
    def test_schema_url(self, get):
        url = "http://ble.com/schema"
        s = schema.get(url=url)
        self.assertEqual(url, s.url)
