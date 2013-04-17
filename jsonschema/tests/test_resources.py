#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
        self.request_mock = mock.patch('requests.get').start()
        self.request_mock.return_value = ResourceSchemaMock()

        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')

    def test_should_obtain_service_url(self):
        self.assertEqual(self.my_resource.url, 'http://my-awesome-api.com/g1/airports')

    def test_should_store_PATCH_method(self):
        self.assertIn('PATCH', self.my_resource._methods.keys())

    def test_should_not_store_PUT_method(self):
        self.assertNotIn('PUT', self.my_resource._methods.keys())

    def test_should_store_POST_method(self):
        self.assertIn('POST', self.my_resource._methods.keys())

    def test_should_store_DELETE_method(self):
        self.assertIn('DELETE', self.my_resource._methods.keys())

    def test_should_call_alloewd_metods_on_server(self):
        self.request_mock.assert_called_with(
            url='http://my-api.com/v1/foo'
        )

    def test_should_exists_create_method(self):
        self.assertTrue(self.my_resource.create)

    def test_should_exists_edit_method(self):
        self.assertTrue(self.my_resource.edit)

    def test_should_not_exists_replace_method(self):
        with self.assertRaises(AttributeError):
            self.my_resource.replace

    def test_should_exists_delete_method(self):
        self.assertTrue(self.my_resource.delete)


class ResourceListTestCase(unittest.TestCase):

    def setUp(self):
        super(ResourceListTestCase, self).setUp()

        self.fake_schema = {
            u'links': [
                {
                    u'href': u'http://my-awesome-api.com/g1/airports',
                    u'rel': u'self'
                },
            ]
        }

        self.patch_request = mock.patch('requests.get')
        self.patch_schema = mock.patch('jsonschema.service.Resource._get_schema')

        self.request_mock = self.patch_request.start()
        self.request_mock.return_value = ResourceItemsMock()

        self.schema_mock = self.patch_schema.start()
        self.schema_mock.return_value = self.fake_schema

    def tearDown(self):
        super(ResourceListTestCase, self).tearDown()
        self.patch_schema.stop()
        self.patch_request.stop()

    def test_should_be_possible_obtain_all_elements_of_the_resource(self):
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        expected_element = [
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
        ]

        self.assertEqual(self.my_resource(), expected_element)

    def test_should_call_correct_repository(self):
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource()
        self.request_mock.assert_called_with(
            url='http://my-awesome-api.com/g1/airports'
        )
