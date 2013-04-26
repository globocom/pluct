from unittest import TestCase

from pluct import schema


class SchemaTestCase(TestCase):
    def test_get_should_returns_a_schema(self):
        instance = schema.get(uri="http://myapp.com/schema/myschema")
        self.assertIsInstance(instance, schema.Schema)
