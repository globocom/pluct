from unittest import TestCase
from mock import patch, Mock

from pluct import schema


class SchemaTestCase(TestCase):
    @patch("requests.get")
    def test_get_should_returns_a_schema(self, get):
        instance = schema.get(url="http://myapp.com/schema/myschema")
        self.assertIsInstance(instance, schema.Schema)

    @patch("requests.get")
    def test_schema_required(self, get):
        data = {
            "title": "app schema",
            "properties": {
                "cname": {"type": "string"},
                "ip": {"type": "string"},
                "name": {"type": "string"},
                "platform": {"type": "string"}
            },
            "required": ["platform", "name"],
        }
        mock = Mock()
        mock.json = data
        get.return_value = mock
        s = schema.get(url="http://myapp.com/schema/myschema")
        required = ["platform", "name"]
        self.assertListEqual(required, s.required)

    @patch("requests.get")
    def test_schema_url(self, get):
        url = "http://ble.com/schema"
        s = schema.get(url=url)
        self.assertEqual(url, s.url)
