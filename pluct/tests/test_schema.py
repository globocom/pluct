# -*- coding: utf-8 -*-

from unittest import TestCase

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

        self.url = "http://app.com/myschema"
        self.result = schema.Schema(self.url, raw_schema=self.data)

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

    def test_links_should_not_be_setted_by_default(self):
        s = schema.Schema(url="")
        self.assertFalse(hasattr(s, "links"))

    def test_properties_should_not_be_setted_by_default(self):
        s = schema.Schema(url="")
        self.assertFalse(hasattr(s, "properties"))

    def test_required_should_not_be_setted_by_default(self):
        s = schema.Schema(url="")
        self.assertFalse(hasattr(s, "required"))


class GetProfileFromHeaderTestCase(TestCase):

    SCHEMA_URL = 'http://a.com/schema'

    def test_return_none_for_missing_content_type(self):
        headers = {}
        url = schema.get_profile_from_header(headers)
        self.assertIs(url, None)

    def test_return_none_for_missing_profile(self):
        headers = {'content-type': 'application/json'}
        url = schema.get_profile_from_header(headers)
        self.assertIs(url, None)

    def test_should_read_schema_from_profile(self):
        headers = {
            'content-type': (
                'application/json; charset=utf-8; profile=%s'
                % self.SCHEMA_URL)
        }
        url = schema.get_profile_from_header(headers)
        self.assertEqual(url, self.SCHEMA_URL)

    def test_should_parse_schema_from_quoted_profile(self):
        headers = {
            'content-type': (
                'application/json; charset=utf-8; profile="%s"'
                % self.SCHEMA_URL)
        }
        url = schema.get_profile_from_header(headers)
        self.assertEqual(url, self.SCHEMA_URL)
