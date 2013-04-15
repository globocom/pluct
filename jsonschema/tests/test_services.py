#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
from jsonschema import Service
from jsonschema.tests.mocks import ServiceSchemaMock
from jsonschema.tests.test_resources import ResourceFake


class ServiceTestCase(unittest.TestCase):

    def setUp(self):
        super(ServiceTestCase, self).setUp()
        self.request_mock = mock.patch('requests.get').start()
        self.request_mock.return_value = ServiceSchemaMock()

        self.resource_mock = mock.patch('jsonschema.service.Resource').start()
        self.resource_mock.return_value = ResourceFake

        self.my_service = Service('http://my-awesome-api.com', 'v1')

    def test_should_have_url(self):
        self.assertEqual(self.my_service.url, 'http://my-awesome-api.com/v1')

    def test_should_have_version(self):
        self.assertEqual(self.my_service.version, 'v1')

    def test_should_call_the_get_method(self):
        self.request_mock.assert_called_with(
            url='http://my-awesome-api.com/v1/schemas'
        )


    def test_should_obtain_resources(self):
        self.assertIn({u'collection_name': u'airports'}, self.my_service.resources)
        self.assertIn({u'collection_name': u'cities'}, self.my_service.resources)

    def test_should_create_resources(self):
        self.assertTrue(self.my_service.airports)
        self.assertTrue(self.my_service.cities)