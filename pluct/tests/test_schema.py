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
                "platform": {"type": "string"},
                "media": {"$ref": "#/definitions/media"}
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
            "definitions": {
                "media": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "title": {"type": "string"},
                    }
                }
            }
        }
        mock = Mock()
        get.return_value = mock
        mock.json.return_value = self.data

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

    def test_schema_definitions(self):
        self.assertDictEqual(self.data["definitions"], self.result.definitions)

    def test_schema_url(self):
        self.assertEqual(self.url, self.result.url)

    def test_links_should_not_be_setted_by_default(self):
        s = schema.Schema(url="")
        self.assertFalse(hasattr(s, "links"))

    def test_properties_should_not_be_setted_by_default(self):
        s = schema.Schema(url="")
        self.assertFalse(hasattr(s, "properties"))

    def test_required_should_not_be_setted_by_default(self):
        s = schema.Schema(url="")
        self.assertFalse(hasattr(s, "required"))
