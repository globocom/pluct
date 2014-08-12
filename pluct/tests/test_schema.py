# -*- coding: utf-8 -*-

from unittest import TestCase

from mock import Mock, patch

from pluct.schema import get_profile_from_header, LazySchema, Schema
from pluct.session import Session


class SchemaTestCase(TestCase):

    def setUp(self):
        self.session = Session()
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
        self.schema = Schema(
            self.url, raw_schema=self.data, session=self.session)

    def test_schema_required(self):
        self.assertListEqual(self.data["required"], self.schema['required'])

    def test_schema_title(self):
        self.assertEqual(self.data["title"], self.schema['title'])

    def test_schema_properties(self):
        self.assertEqual(self.data['properties'], self.schema['properties'])

    def test_schema_links(self):
        self.assertListEqual(self.data["links"], self.schema['links'])

    def test_schema_url(self):
        self.assertEqual(self.url, self.schema.url)

    def test_session(self):
        self.assertIs(self.session, self.schema.session)


class LazySchemaTestCase(TestCase):

    def run(self, *args, **kwargs):
        self.session = Session()
        self.schema = LazySchema('/schema', session=self.session)

        with patch.object(self.session, 'request') as request:
            self.data = {'fake': 'schema'}
            self.response = Mock()
            self.response.json.return_value = self.data
            self.request = request
            request.return_value = self.response

            return super(LazySchemaTestCase, self).run(*args, **kwargs)

    def test_loads_schema_once_accessing_data(self):
        self.assertEqual(self.schema.data, self.data)
        self.assertEqual(self.schema.data, self.data)

        self.request.assert_called_once_with('get', '/schema')

    def test_loads_schema_once_accessing_raw_schema(self):
        self.assertEqual(self.schema.raw_schema, self.data)
        self.assertEqual(self.schema.raw_schema, self.data)

        self.request.assert_called_once_with('get', '/schema')

    def test_url(self):
        self.assertEqual(self.schema.url, '/schema')

    def test_session(self):
        self.assertIs(self.session, self.schema.session)


class GetProfileFromHeaderTestCase(TestCase):

    SCHEMA_URL = 'http://a.com/schema'

    def test_return_none_for_missing_content_type(self):
        headers = {}
        url = get_profile_from_header(headers)
        self.assertIs(url, None)

    def test_return_none_for_missing_profile(self):
        headers = {'content-type': 'application/json'}
        url = get_profile_from_header(headers)
        self.assertIs(url, None)

    def test_should_read_schema_from_profile(self):
        headers = {
            'content-type': (
                'application/json; charset=utf-8; profile=%s'
                % self.SCHEMA_URL)
        }
        url = get_profile_from_header(headers)
        self.assertEqual(url, self.SCHEMA_URL)

    def test_should_parse_schema_from_quoted_profile(self):
        headers = {
            'content-type': (
                'application/json; charset=utf-8; profile="%s"'
                % self.SCHEMA_URL)
        }
        url = get_profile_from_header(headers)
        self.assertEqual(url, self.SCHEMA_URL)


class GetLinkTestCase(TestCase):

    def setUp(self):
        self.url = '/'
        self.data = {
            'links': [
                {
                    'rel': 'create',
                    'href': '/api/content',
                }
            ]
        }
        self.session = Session()
        self.schema = Schema(
            self.url, raw_schema=self.data, session=self.session)

    def test_returns_link_by_rel(self):
        link = self.schema.get_link('create')
        self.assertEqual(link, self.data['links'][0])

    def test_returns_none_for_missing_link(self):
        link = self.schema.get_link('missing')
        self.assertIs(link, None)
