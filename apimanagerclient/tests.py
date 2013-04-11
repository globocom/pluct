#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import unittest
import mock
from apimanagerclient import Service
from apimanagerclient.service import Resource


class ServiceSchemaMock(mock.MagicMock):
    headers = {
        'content-type': 'application/json'
    }
    status_code = 200
    content = json.dumps(
        {
            'items': [
                {
                    'collection_name': "airports",
                    # 'resource_id': "airport",
                },
                {
                    'collection_name': "cities",
                    # 'resource_id': "city",
                }
            ],
            'item_count': 2
        }
    )

class ResourceFake(Resource):
    url = 'fake-url'
    methods = ['get']

class ServiceTestCase(unittest.TestCase):


    def setUp(self):
        super(ServiceTestCase, self).setUp()
        self.request_mock = mock.patch('requests.get').start()
        self.request_mock.return_value = ServiceSchemaMock()

        self.resource_mock = mock.patch('apimanagerclient.service.Resource').start()
        self.resource_mock.return_value = ResourceFake

        self.my_service = Service('http://my-api.com', 'v1')

    def test_should_have_url(self):
        self.assertEqual(self.my_service.url, 'http://my-api.com/v1')

    def test_should_have_version(self):
        self.assertEqual(self.my_service.version, 'v1')


    def test_should_call_the_get_method(self):
        self.request_mock.assert_called_with(
            url='http://my-api.com/v1/schemas'
        )

    def test_should_obtain_resources(self):
        self.assertIn({u'collection_name': u'airports'}, self.my_service.resources)
        self.assertIn({u'collection_name': u'cities'}, self.my_service.resources)

    def test_should_create_resources(self):
        self.assertTrue(self.my_service.airports)
        self.assertTrue(self.my_service.cities)




class ResourceSchemaMock(mock.MagicMock):
    headers = {
        'content-type': 'application/json'
    }
    status_code = 200
    content = json.dumps({
        'allowed_list_http_methods': [
            "get"
        ],
        }
    )



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


class ResourceItemsMock(mock.MagicMock):
    headers = {
        'content-type': 'application/json'
    }
    status_code = 200
    content = json.dumps({
        'items': [
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
        ],
        }
    )


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




if __name__ == '__main__':
    unittest.main()
