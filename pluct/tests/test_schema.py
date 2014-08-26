# -*- coding: utf-8 -*-

from copy import deepcopy
from unittest import TestCase

from mock import Mock, patch
from pluct.schema import get_profile_from_header, LazySchema, Schema
from pluct.session import Session


SCHEMA = {
    'title': 'app schema',
    'properties': {
        'name': {'type': 'string'},
        'platform': {'type': 'string'},
        'pointer': {'$ref': '#/pointer'},
        'pointers': {
            'items': {
                'oneOf': [
                    {'$ref': '#/pointer'},
                    {'$ref': '#/pointer2'},
                ]
            }
        },
        'repointer': {'$ref': '#/repointer'},
        'external': {'$ref': 'http://example.com/schema#/pointer'},
        'external2': {'$ref': 'http://example.com/schema#/pointer'},
        'self': {'$ref': '#'},
    },
    'links': [
        {
            'rel': 'create',
            'href': '/api/content',
        }
    ],
    'required': ['platform', 'name'],
    'pointer': {
        'type': 'string',
        'description': 'local-pointer-str',
    },
    'pointer2': {
        'type': 'integer',
        'description': 'local-pointer-int',
    },
    'repointer': {
        '$ref': '#/pointer',
    },
}


class BaseLazySchemaTestCase(TestCase):

    HREF = '/schema'
    RAW_SCHEMA = SCHEMA

    def run(self, *args, **kwargs):
        self.session = Session()
        self.schema = LazySchema(self.HREF, session=self.session)

        with patch.object(self.session, 'request') as self.request:
            self.response = Mock()
            self.response.json.return_value = deepcopy(self.RAW_SCHEMA)
            self.request.return_value = self.response

            return super(BaseLazySchemaTestCase, self).run(*args, **kwargs)


class SchemaTestCase(TestCase):

    def setUp(self):
        self.session = Session()

        self.url = 'http://app.com/myschema'
        self.schema = Schema(
            self.url, raw_schema=deepcopy(SCHEMA), session=self.session)

    def test_schema_required(self):
        self.assertListEqual(SCHEMA['required'], self.schema['required'])

    def test_schema_title(self):
        self.assertEqual(SCHEMA['title'], self.schema['title'])

    def test_schema_properties(self):
        self.assertEqual(
            SCHEMA['properties']['name'],
            self.schema.data['properties']['name'])

    def test_schema_links(self):
        self.assertListEqual(SCHEMA['links'], self.schema['links'])

    def test_schema_url(self):
        self.assertEqual(self.url, self.schema.url)

    def test_session(self):
        self.assertIs(self.session, self.schema.session)


class LazySchemaTestCase(BaseLazySchemaTestCase):

    def test_loads_schema_once_accessing_data(self):
        self.assertEqual(self.schema.data['title'], SCHEMA['title'])
        self.assertEqual(self.schema.data['title'], SCHEMA['title'])

        self.request.assert_called_once_with('/schema')

    def test_loads_schema_once_accessing_raw_schema(self):
        self.assertEqual(self.schema.raw_schema['title'], SCHEMA['title'])
        self.assertEqual(self.schema.raw_schema['title'], SCHEMA['title'])

        self.request.assert_called_once_with('/schema')

    def test_url(self):
        self.assertEqual(self.schema.url, '/schema')

    def test_session(self):
        self.assertIs(self.session, self.schema.session)


class CircularSchemaTestCase(TestCase):

    def test_uses_original_ref_on_representation(self):
        raw_schema = {
            'properties': {
                'inner': {'$ref': '/schema'},
            }
        }
        session = Session()
        schema = Schema('/schema', raw_schema=raw_schema, session=session)
        self.assertEqual(repr(schema), repr(raw_schema))


class LazyCircularSchemaTestCase(BaseLazySchemaTestCase):

    HREF = '/schema#'
    RAW_SCHEMA = {
        'properties': {
            'inner': {'$ref': HREF},
        }
    }

    def test_uses_original_ref_on_representation(self):
        self.assertEqual(repr(self.schema), repr({'$ref': self.HREF}))


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
            self.url, raw_schema=deepcopy(SCHEMA), session=self.session)

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
        schema = deepcopy(SCHEMA)
        return Schema(
            href, raw_schema=schema, session=self.session)

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
        self.assertEqual(schema['title'], SCHEMA['title'])

    def test_returns_schema_data_from_pointer(self):
        pointer = '/properties/name'
        schema = self.create_schema(self.href + pointer)
        self.assertEqual(schema, SCHEMA['properties']['name'])

    def test_resolves_local_pointer_on_objects(self):
        schema = self.create_schema(self.href)
        self.assertEqual(schema['properties']['pointer'], SCHEMA['pointer'])

    def test_resolves_local_pointer_on_arrays(self):
        schema = self.create_schema(self.href)
        pointers = schema['properties']['pointers']['items']['oneOf']
        expected = [SCHEMA['pointer'], SCHEMA['pointer2']]
        self.assertEqual(pointers, expected)

    def test_keeps_context_between_refs(self):
        schema = self.create_schema(self.href)
        self.assertEqual(schema['properties']['repointer'], SCHEMA['pointer'])

    def test_resolves_external_ref_with_lazy_schema(self):
        schema = self.create_schema(self.href)
        external = schema['properties']['external']
        self.assertIsInstance(external, LazySchema)
        self.assertEqual(
            external.href, SCHEMA['properties']['external']['$ref'])

    def test_resolves_self_reference(self):
        schema = self.create_schema(self.href)
        self_ref = schema['properties']['self']
        self.assertEqual(
            self_ref['title'], SCHEMA['title'])

    def test_is_instance_of_dict(self):
        schema = self.create_schema(self.href)
        self.assertIsInstance(schema, dict)

    def test_is_instance_of_schema(self):
        schema = self.create_schema(self.href)
        self.assertIsInstance(schema, Schema)


class LazySchemaPointerTestCase(BaseLazySchemaTestCase):

    HREF = '/schema#/properties/name'

    def test_applies_pointer_to_loaded_schema(self):
        self.assertEqual(self.schema, SCHEMA['properties']['name'])


class SchemaStoreMixinTestCase(object):

    SCHEMA_URL = 'http://a.com/schema'

    def setUp(self):
        self.session = Session()

    def test_reuses_schema_for_same_href(self):
        schema1 = self.create_schema(self.SCHEMA_URL)
        schema2 = self.create_schema(self.SCHEMA_URL)
        self.assertIs(schema1, schema2)

    def test_doesnt_reuse_schema_with_empty_url(self):
        schema1 = self.create_schema('')
        schema2 = self.create_schema('')
        self.assertIs(schema1, schema2)

    def test_reuses_schema_for_different_pointers(self):
        schema1 = self.create_schema(self.SCHEMA_URL)
        schema2 = self.create_schema(
            self.SCHEMA_URL + '#/pointer')
        self.assertIs(schema1, schema2)

    def test_does_not_reuse_schema_on_different_sessions(self):
        other_session = Session()

        schema1 = self.create_schema(self.SCHEMA_URL)
        schema2 = self.create_schema(
            self.SCHEMA_URL, session=other_session)

        self.assertIsNot(schema1, schema2)


class SchemaStoreTestCase(SchemaStoreMixinTestCase, TestCase):

    def create_schema(self, url, session=None):
        if session is None:
            session = self.session
        return Schema(self.SCHEMA_URL, raw_schema={}, session=session)


class LazySchemaStoreTestCase(SchemaStoreMixinTestCase, TestCase):

    def create_schema(self, url, session=None):
        if session is None:
            session = self.session
        return LazySchema(self.SCHEMA_URL, session=session)
