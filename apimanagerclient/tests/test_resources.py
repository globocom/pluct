#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
from apimanagerclient.service import Resource
from apimanagerclient.tests.mocks import ResourceSchemaMock, ResourceItemsMock


class ResourceFake(Resource):
    url = 'fake-url'
    methods = ['get']


class ResourceTestCase(unittest.TestCase):
    def setUp(self):
        super(ResourceTestCase, self).setUp()
        self.request_mock = mock.patch('requests.get').start()
        self.request_mock.return_value = ResourceSchemaMock()

        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')

    def test_should_obtain_service_url(self):
        self.assertEqual(self.my_resource.url, 'http://my-api.com/v1/foo')

    def test_should_call_alloewd_metods_on_server(self):
        self.request_mock.assert_called_with(
            url='http://my-api.com/v1/foo/schema'
        )

    def test_should_store_allowed_methods(self):
        self.assertEqual(self.my_resource.methods, ['get',])


class ResourceListTestCase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super(ResourceListTestCase, self).__init__(methodName)
        self.request_mock = mock.patch('requests.get').start()
        self.request_mock.return_value = ResourceItemsMock()

    @mock.patch('apimanagerclient.service.Resource._get_allowed_methods')
    def test_should_be_possible_obtain_all_elementos_of_the_resource(self, mock):
        self.my_resource = Resource(name='foo', service_url='http://my-api.com/v1')
        self.my_resource.methods = ['get']
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
        self.assertEqual(self.my_resource.all(), expected_element)



