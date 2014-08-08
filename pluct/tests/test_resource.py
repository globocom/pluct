# -*- coding: utf-8 -*-


from requests import Response

from unittest import TestCase
from mock import patch, Mock

from pluct import resource, schema
from pluct.resource import Resource
from pluct.request import from_response


class ResourceTestCase(TestCase):

    @patch("pluct.schema.get")
    @patch("requests.get")
    def setUp(self, mock_get, mock_schema_get):
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
        self.schema = schema.Schema(url="url.com", raw_schema=raw_schema)
        mock_schema_get.return_value = self.schema
        self.headers = {
            'content-type': 'application/json; profile=url.com'
        }
        mock = Mock(headers=self.headers)
        mock.json.return_value = self.data
        mock_get.return_value = mock
        self.url = "http://app.com/content"
        self.result = resource.get(url=self.url)
        mock_schema_get.assert_called_with("url.com")

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
        old = self.result.schema.required
        try:
            self.result.schema.required = ["ble"]
            self.assertFalse(self.result.is_valid())
        finally:
            self.result.schema.required = old

    @patch("pluct.schema.from_header")
    @patch("requests.get")
    def test_is_valid_invalid(self, get, from_header):
        from_header.return_value = self.schema
        data = {
            u'doestnotexists': u'repos',
        }
        mock = Mock(headers={})
        mock.json.return_value = data
        get.return_value = mock
        result = resource.get(url="appurl.com")
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
        self.schema = schema.Schema(url="url.com", raw_schema=self.raw_schema)

    def test_wraps_array_objects_as_resources(self):
        data = {
            'objects': [
                {'id': 111}
            ]
        }
        app = Resource(url="appurl.com", data=data, schema=self.schema)
        item = app.data['objects'][0]

        self.assertIsInstance(item, Resource)
        self.assertEqual(item.data['id'], 111)
        self.assertEqual(item.schema._raw_schema, self.item_schema)

    def test_wraps_array_objects_as_resources_even_without_items_key(self):
        data = {
            'values': [
                {'id': 1}
            ]
        }
        resource = Resource(url="appurl.com", data=data, schema=self.schema)

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
        resource_list = Resource(
            url="appurl.com", data=data, schema=self.schema)
        values = resource_list['values']

        self.assertEqual(values, data['values'])


class FromResponseTestCase(TestCase):

    def setUp(self):
        self._response = Response()
        self._response.url = 'http://example.com'
        content_type = 'application/json; profile=http://example.com/schema'
        self._response.headers = {
            'content-type': content_type
        }

    @patch('pluct.schema.from_header')
    def test_should_return_resource_from_response(self, from_header):
        self._response.json = Mock(return_value={})
        self._response.status_code = 200
        returned_resource = from_response(Resource, self._response)
        self.assertEqual(returned_resource.url, 'http://example.com')
        self.assertEqual(returned_resource.data, {})
        self.assertEqual(returned_resource.response.status_code, 200)

    @patch('pluct.schema.from_header')
    def test_should_return_resource_from_response_with_no_json_data(
            self, from_header):
        self._response.json = Mock(side_effect=ValueError())
        returned_resource = from_response(Resource, self._response)
        self.assertEqual(returned_resource.url, 'http://example.com')
        self.assertEqual(returned_resource.data, {})

    @patch('pluct.schema.from_header')
    def test_should_obtain_schema_from_header(self, from_header):
        self._response.json = Mock(side_effect=ValueError())
        from_response(Resource, self._response)
        from_header.assert_called_with(self._response.headers)

    def test_resource_with_an_array_without_schema(self):
        data = {
            u'units': [
                {u'name': u'someunit'}
            ],
            u'name': u'registry',
        }
        s = schema.Schema(
            url='url',
            raw_schema={
                'title': 'app schema',
                'type': 'object',
                'required': ['name'],
                'properties': {'name': {'type': 'string'}}
            })
        response = Resource("url", data, s)
        self.assertDictEqual(data, response.data)
