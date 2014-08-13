# -*- coding: utf-8 -*-

from unittest import TestCase

from mock import Mock, patch

from pluct.schema import get_profile_from_header, LazySchema, Schema
from pluct.session import Session


SCHEMA = {
    'title': 'app schema',
    'properties': {
        'name': {'type': 'string'},
        'platform': {'type': 'string'},
    },
    'links': [
        {
            'rel': 'create',
            'href': '/api/content',
        }
    ],
    'required': ['platform', 'name'],
}


class BaseLazySchemaTestCase(TestCase):

    HREF = '/schema'

    def run(self, *args, **kwargs):
        self.session = Session()
        self.schema = LazySchema(self.HREF, session=self.session)

        with patch.object(self.session, 'request') as request:
            self.response = Mock()
            self.response.json.return_value = SCHEMA
            self.request = request
            request.return_value = self.response

            return super(BaseLazySchemaTestCase, self).run(*args, **kwargs)


class SchemaTestCase(TestCase):

    def setUp(self):
        self.session = Session()

        self.url = 'http://app.com/myschema'
        self.schema = Schema(
            self.url, raw_schema=SCHEMA, session=self.session)

    def test_schema_required(self):
        self.assertListEqual(SCHEMA['required'], self.schema['required'])

    def test_schema_title(self):
        self.assertEqual(SCHEMA['title'], self.schema['title'])

    def test_schema_properties(self):
        self.assertEqual(SCHEMA['properties'], self.schema['properties'])

    def test_schema_links(self):
        self.assertListEqual(SCHEMA['links'], self.schema['links'])

    def test_schema_url(self):
        self.assertEqual(self.url, self.schema.url)

    def test_session(self):
        self.assertIs(self.session, self.schema.session)


class LazySchemaTestCase(BaseLazySchemaTestCase):

    def test_loads_schema_once_accessing_data(self):
        self.assertEqual(self.schema.data, SCHEMA)
        self.assertEqual(self.schema.data, SCHEMA)

        self.request.assert_called_once_with('get', '/schema')

    def test_loads_schema_once_accessing_raw_schema(self):
        self.assertEqual(self.schema.raw_schema, SCHEMA)
        self.assertEqual(self.schema.raw_schema, SCHEMA)

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
        self.session = Session()
        self.schema = Schema(
            self.url, raw_schema=SCHEMA, session=self.session)

    def test_returns_link_by_rel(self):
        link = self.schema.get_link('create')
        self.assertEqual(link, SCHEMA['links'][0])

    def test_returns_none_for_missing_link(self):
        link = self.schema.get_link('missing')
        self.assertIs(link, None)


class SchemaPointerTestCase(TestCase):

    def setUp(self):
        self.session = Session()
        self.url = 'http://example.org/schema'
        self.pointer = ''
        self.href = '#'.join((self.url, self.pointer))

    def create_schema(self, href):
        return Schema(
            href, raw_schema=SCHEMA, session=self.session)

    def assertValidRefs(self, schema, url=None, pointer=None):
        url = url or self.url
        pointer = pointer or self.pointer
        href = '#'.join((url, pointer))

        self.assertEqual(schema.url, url)
        self.assertEqual(schema.pointer, pointer)
        self.assertEqual(schema.href, href)

    def test_splits_url_and_pointer_on_init(self):
        schema = self.create_schema(self.href)
        self.assertValidRefs(schema)

    def test_fixes_href_without_pointer(self):
        schema = self.create_schema(self.url)
        self.assertValidRefs(schema)

    def test_fixes_empty_pointer(self):
        schema = self.create_schema(self.url + '#')
        self.assertValidRefs(schema)

    def test_accepts_pointer(self):
        pointer = '/properties/name'
        schema = self.create_schema(self.href + pointer)
        self.assertValidRefs(schema, pointer=pointer)

    def test_returns_root_schema_data_from_empty_pointer(self):
        schema = self.create_schema(self.href)
        self.assertEqual(schema, SCHEMA)

    def test_returns_schema_data_from_pointer(self):
        pointer = '/properties/name'
        schema = self.create_schema(self.href + pointer)

        self.assertEqual(schema, SCHEMA['properties']['name'])


class LazySchemaPointerTestCase(BaseLazySchemaTestCase):

    HREF = '/schema#/properties/name'

    def test_applies_pointer_to_loaded_schema(self):
        self.assertEqual(self.schema, SCHEMA['properties']['name'])
