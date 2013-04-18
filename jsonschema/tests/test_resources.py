#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import unittest
import mock
from jsonschema.service import Resource
from jsonschema.tests.mocks import ResourceSchemaMock, ResourceItemsMock


class ResourceFake(Resource):
    url = 'fake-url'
    _methods = {u'DELETE': u'delete',
                u'PATCH': u'edit',
                u'POST': u'create',
                u'PUT': u'replace'}


class ResourceTestCase(unittest.TestCase):
    def setUp(self):
        super(ResourceTestCase, self).setUp()

        self.patch_request = mock.patch('requests.get')

        self.request_mock = self.patch_request.start()
        self.request_mock.return_value = ResourceSchemaMock()

        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')

    def tearDown(self):
        super(ResourceTestCase, self).tearDown()
        self.patch_request.stop()


    def test_should_obtain_service_url(self):
        self.assertEqual(self.my_resource.url, 'http://my-awesome-api.com/g1/airports')

    def test_should_store_GET_method(self):
        self.assertIn('GET', self.my_resource._methods)

    def test_should_exists_self_method(self):
        self.assertTrue(self.my_resource.self)

    def test_should_exists_item_method(self):
        self.assertTrue(self.my_resource.item)

    def test_should_store_PATCH_method(self):
        self.assertIn('PATCH', self.my_resource._methods)

    def test_should_exists_edit_method(self):
        self.assertTrue(self.my_resource.edit)

    def test_should_store_POST_method(self):
        self.assertIn('POST', self.my_resource._methods)

    def test_should_exists_create_method(self):
        self.assertTrue(self.my_resource.create)

    def test_should_store_DELETE_method(self):
        self.assertIn('DELETE', self.my_resource._methods)

    def test_should_exists_delete_method(self):
        self.assertTrue(self.my_resource.delete)

    def test_should_store_PUT_method(self):
        self.assertIn('PUT', self.my_resource._methods)

    def test_should_exists_replace_method(self):
        self.assertTrue(self.my_resource.replace)

    def test_should_call_allowed_metods_on_server(self):
        self.request_mock.assert_called_with(
            url='http://my-api.com/v1/foo',
            headers={'content-type': 'application/json'}
        )



class ResourceListTestCase(unittest.TestCase):

    def setUp(self):
        super(ResourceListTestCase, self).setUp()

        self.fake_schema = {
            u'links': [
                {
                    u'href': u'http://my-awesome-api.com/g1/airports',
                    u'rel': u'self'
                },
                {
                    u'href': u'http://my-awesome-api.com/g1/airports',
                    u'method': u'POST',
                    u'rel': u'create'
                },
                {
                    u'href': u'http://my-awesome-api.com/g1/airports/{resource_id}',
                    u'method': u'DELETE',
                    u'rel': u'delete'
                },
                {
                    u'href': u'http://my-awesome-api.com/g1/airports/{resource_id}',
                    u'rel': u'item'
                },
                {
                    u'href': u'http://my-awesome-api.com/g1/airports/{resource_id}',
                    u'method': u'PATCH',
                    u'rel': u'edit'
                },
                {
                    u'href': u'http://my-awesome-api.com/g1/airports/{resource_id}',
                    u'method': u'PUT',
                    u'rel': u'replace'
                }
            ]
        }

        self.patch_schema = mock.patch('jsonschema.service.Resource._get_schema')


        self.schema_mock = self.patch_schema.start()
        self.schema_mock.return_value = self.fake_schema

    def tearDown(self):
        super(ResourceListTestCase, self).tearDown()
        self.patch_schema.stop()

    @mock.patch('requests.get')
    def test_should_be_possible_obtain_all_elements_throught_Selft_method(self, request_mock):
        request_mock.return_value = ResourceItemsMock()

        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        expected_element = {
            'items':
            [
            {
                u'name': u"Rio de Janeiro",
                u'resource_id': u"rio-de-janeiro"
            },
            {
                u'name': u"São Paulo",
                u'resource_id': u"sao-paulo"
            },
            {
                u'name': u"Recife",
                u'resource_id': u"recife"
            },
        ]}
        response = self.my_resource.self()
        self.assertEqual(json.loads(response.content), expected_element)

    def test_GET_method_should_be_in_methods(self):
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.assertIn('GET', self.my_resource._methods)

    def test_POST_method_should_be_in_methods(self):
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.assertIn('POST', self.my_resource._methods)

    @mock.patch('requests.get')
    def test_should_call_self_with_correct_repository(self, request_mock):
        request_mock.return_value = ResourceItemsMock()

        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.self()
        self.assertEqual(request_mock.call_args[1]['url'], 'http://my-awesome-api.com/g1/airports')

    @mock.patch('requests.get')
    def test_should_call_self__with_json_on_content_type(self, request_mock):
        request_mock.return_value = ResourceItemsMock()

        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.self()
        self.assertEqual(request_mock.call_args[1]['headers'], {'content-type': 'application/json'})

    @mock.patch('requests.get')
    def test_should_call_item_with_correct_path(self, request_mock):
        request_mock.return_value = ResourceItemsMock()

        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.item('resource-id-value')

        self.assertEqual(request_mock.call_args[1]['url'], 'http://my-awesome-api.com/g1/airports/resource-id-value')

    @mock.patch('requests.get')
    def test_should_call_self__with_json_on_content_type(self, request_mock):
        request_mock.return_value = ResourceItemsMock()

        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.item('resource-id-value')
        self.assertEqual(request_mock.call_args[1]['headers'], {'content-type': 'application/json'})


    @mock.patch('requests.post')
    def test_should_call_create_with_correct_repository(self, request_mock):
        request_mock.return_value = ResourceItemsMock()
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.create({'foo':'bar'})
        self.assertEqual(request_mock.call_args[1]['url'], 'http://my-awesome-api.com/g1/airports')

    @mock.patch('requests.post')
    def test_should_call_create_with_json_on_content_type(self, request_mock):
        request_mock.return_value = ResourceItemsMock()
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.create({'foo':'bar'})
        self.assertEqual(request_mock.call_args[1]['headers'], {'content-type': 'application/json'})

    @mock.patch('requests.post')
    def test_should_call_create_with_correct_data(self, request_mock):
        request_mock.return_value = ResourceItemsMock()
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.create({'foo':'bar'})
        self.assertEqual(request_mock.call_args[1]['data'], json.dumps({'foo':'bar'}))

    @mock.patch('requests.delete')
    def test_should_call_create_with_correct_repository(self, request_mock):
        request_mock.return_value = ResourceItemsMock()
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.delete('resource-id-value')
        self.assertEqual(request_mock.call_args[1]['url'], 'http://my-awesome-api.com/g1/airports/resource-id-value')

    @mock.patch('requests.delete')
    def test_should_call_create_with_json_on_content_type(self, request_mock):
        request_mock.return_value = ResourceItemsMock()
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.delete('resource-id-value')
        self.assertEqual(request_mock.call_args[1]['headers'], {'content-type': 'application/json'})

    @mock.patch('requests.patch')
    def test_should_call_edit_with_correct_repository(self, request_mock):
        request_mock.return_value = ResourceItemsMock()
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.edit('resource-id-value', {'foo':'bar'})
        self.assertEqual(request_mock.call_args[1]['url'], 'http://my-awesome-api.com/g1/airports/resource-id-value')

    @mock.patch('requests.patch')
    def test_should_call_edit_with_json_on_content_type(self, request_mock):
        request_mock.return_value = ResourceItemsMock()
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.edit('resource-id-value', {'foo':'bar'})
        self.assertEqual(request_mock.call_args[1]['headers'], {'content-type': 'application/json'})

    @mock.patch('requests.patch')
    def test_should_call_edit_with_correct_data(self, request_mock):
        request_mock.return_value = ResourceItemsMock()
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.edit('resource-id-value', {'foo':'bar'})
        self.assertEqual(request_mock.call_args[1]['data'], json.dumps({'foo':'bar'}))

    @mock.patch('requests.put')
    def test_should_call_replace_with_correct_repository(self, request_mock):
        request_mock.return_value = ResourceItemsMock()
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.replace('resource-id-value', {'foo':'bar'})
        self.assertEqual(request_mock.call_args[1]['url'], 'http://my-awesome-api.com/g1/airports/resource-id-value')

    @mock.patch('requests.put')
    def test_should_call_replace_with_json_on_content_type(self, request_mock):
        request_mock.return_value = ResourceItemsMock()
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.replace('resource-id-value', {'foo':'bar'})
        self.assertEqual(request_mock.call_args[1]['headers'], {'content-type': 'application/json'})

    @mock.patch('requests.put')
    def test_should_call_replace_with_correct_data(self, request_mock):
        request_mock.return_value = ResourceItemsMock()
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.replace('resource-id-value', {'foo':'bar'})
        self.assertEqual(request_mock.call_args[1]['data'], json.dumps({'foo':'bar'}))
