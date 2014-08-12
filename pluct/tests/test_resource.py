# -*- coding: utf-8 -*-


from unittest import TestCase
from mock import patch, Mock

from pluct import schema
from pluct.resource import Resource, ObjectResource, ArrayResource
from pluct.session import Session
from pluct.schema import Schema


class ResourceTestCase(TestCase):

    def setUp(self):
        self.data = {
            "name": "repos",
            "platform": "js",
        }
        raw_schema = {
            'type': "object",
            'required': ["platform"],
            'title': "some title",
            'properties': {
                u'name': {u'type': u'string'},
                u'platform': {u'type': u'string'}
            },
            'links': [
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
            ]}
        self.schema = schema.Schema(href="url.com", raw_schema=raw_schema)

        self.url = "http://app.com/content"

        self.result = Resource.from_data(
            url=self.url, data=self.data, schema=self.schema)

    def test_get_should_returns_a_resource(self):
        self.assertIsInstance(self.result, Resource)

    def test_missing_attribute(self):
        with self.assertRaises(AttributeError):
            self.result.not_found

    def test_str(self):
        self.assertEqual(str(self.data), str(self.result))

    def test_data(self):
        self.assertEqual(self.data, self.result.data)

    def test_iter(self):
        iterated = [i for i in self.result]
        self.assertEqual(iterated, self.data.keys())

    def test_schema(self):
        self.assertEqual(self.schema.url, self.result.schema.url)

    def test_is_valid_schema_error(self):
        old = self.result.schema['required']
        try:
            self.result.schema['required'] = ["ble"]
            self.assertFalse(self.result.is_valid())
        finally:
            self.result.schema.required = old

    def test_is_valid_invalid(self):
        data = {
            u'doestnotexists': u'repos',
        }
        result = Resource.from_data('/url', data=data, schema=self.schema)
        self.assertFalse(result.is_valid())

    def test_is_valid(self):
        self.assertTrue(self.result.is_valid())


class ParseResourceTestCase(TestCase):

    def setUp(self):
        self.item_schema = {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'integer'
                }
            },
            'links': [{
                "href": "http://localhost/foos/{id}/",
                "method": "GET",
                "rel": "item",
            }]
        }

        self.raw_schema = {
            'title': "title",
            'type': "object",

            'properties': {
                u'objects': {
                    u'type': u'array',
                    u'items': self.item_schema,
                },
                u'values': {
                    u'type': u'array'
                }
            }
        }
        self.schema = schema.Schema(href="url.com", raw_schema=self.raw_schema)

    def test_wraps_array_objects_as_resources(self):
        data = {
            'objects': [
                {'id': 111}
            ]
        }
        app = Resource.from_data(
            url="appurl.com", data=data, schema=self.schema)
        item = app.data['objects'][0]

        self.assertIsInstance(item, Resource)
        self.assertEqual(item.data['id'], 111)
        self.assertEqual(item.schema.raw_schema, self.item_schema)

    def test_wraps_array_objects_as_resources_even_without_items_key(self):
        data = {
            'values': [
                {'id': 1}
            ]
        }
        resource = Resource.from_data(
            url="appurl.com", data=data, schema=self.schema)

        item = resource['values'][0]
        self.assertIsInstance(item, Resource)
        self.assertEqual(item.data['id'], 1)

    @patch("requests.get")
    def test_doesnt_wrap_non_objects_as_resources(self, get):
        data = {
            'values': [
                1,
                'string',
                ['array']
            ]
        }
        resource_list = Resource.from_data(
            url="appurl.com", data=data, schema=self.schema)
        values = resource_list['values']

        self.assertEqual(values, data['values'])


class ParseResourceWithExternalSchemaTestCase(TestCase):

    def setUp(self):
        self.item_schema_url = 'http://appurl.com/schema'
        self.raw_schema = {
            'title': "title",
            'type': "object",

            'properties': {
                'objects': {
                    'type': 'array',
                    'items': {
                        '$ref': self.item_schema_url
                    }
                }
            }
        }
        self.schema = schema.Schema(href="url.com", raw_schema=self.raw_schema)
        self.session = Session()

    def test_assigns_lazy_schema_to_array_resources_with_external_schema(self):
        item_schema = Mock()
        with patch('pluct.resource.validate'):
            with patch('pluct.resource.LazySchema') as LazySchema:
                LazySchema.return_value = item_schema

                data = {
                    'objects': [
                        {'id': 111}
                    ]
                }

                resource = Resource.from_data(
                    url="appurl.com", data=data, schema=self.schema,
                    session=self.session)

                item = resource.data['objects'][0]

                LazySchema.assert_called_with(
                    self.item_schema_url, session=self.session)
                self.assertEqual(item.schema, item_schema)


class FromResponseTestCase(TestCase):

    def setUp(self):
        self._response = Mock()
        self._response.url = 'http://example.com'

        content_type = 'application/json; profile=http://example.com/schema'
        self._response.headers = {
            'content-type': content_type
        }
        self.session = Session()
        self.schema = Schema('/', raw_schema={})

    def test_should_return_resource_from_response(self):
        self._response.json.return_value = {}
        returned_resource = Resource.from_response(
            self._response, session=self.session, schema=self.schema)
        self.assertEqual(returned_resource.url, 'http://example.com')
        self.assertEqual(returned_resource.data, {})

    def test_should_return_resource_from_response_with_no_json_data(self):
        self._response.json = Mock(side_effect=ValueError())
        returned_resource = Resource.from_response(
            self._response, session=self.session, schema=self.schema)
        self.assertEqual(returned_resource.url, 'http://example.com')
        self.assertEqual(returned_resource.data, {})

    def test_resource_with_an_array_without_schema(self):
        data = {
            u'units': [
                {u'name': u'someunit'}
            ],
            u'name': u'registry',
        }
        s = schema.Schema(
            href='url',
            raw_schema={
                'title': 'app schema',
                'type': 'object',
                'required': ['name'],
                'properties': {'name': {'type': 'string'}}
            })
        response = Resource.from_data("url", data, s)
        self.assertDictEqual(data, response.data)


class ResourceFromDataTestCase(TestCase):

    def test_should_create_array_resource_from_list(self):
        data = []
        resource = Resource.from_data('/', data=data)
        self.assertIsInstance(resource, ArrayResource)
        self.assertEqual(resource.url, '/')
        self.assertEqual(resource.data, data)

    def test_should_create_object_resource_from_dict(self):
        data = {}
        resource = Resource.from_data('/', data=data)
        self.assertIsInstance(resource, ObjectResource)
        self.assertEqual(resource.url, '/')
        self.assertEqual(resource.data, data)
