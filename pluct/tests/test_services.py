#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
from pluct import Service
from pluct.tests.mocks import ServiceSchemaMock
from pluct.tests.test_resources import ResourceFake


class ServiceTestCase(unittest.TestCase):

    def setUp(self):
        super(ServiceTestCase, self).setUp()
        self.patch_request = mock.patch('requests.get')
        self.patch_resource = mock.patch('pluct.service.Resource')

        self.request_mock = self.patch_request.start()
        self.request_mock.return_value = ServiceSchemaMock()

        self.resource_mock = self.patch_resource.start()
        self.resource_mock.return_value = ResourceFake

        self.my_service = Service('http://my-awesome-api.com', 'v1')

    def tearDown(self):
        super(ServiceTestCase, self).tearDown()
        self.patch_request.stop()
        self.patch_resource.stop()

    def test_should_have_url(self):
        self.assertEqual(self.my_service.url, 'http://my-awesome-api.com/v1')

    def test_should_have_version(self):
        self.assertEqual(self.my_service.version, 'v1')

    def test_should_call_the_get_method(self):
        self.request_mock.assert_called_with(
            url='http://my-awesome-api.com/v1/schemas', headers={'content-type': 'application/json'}
        )

    def test_should_obtain_resources(self):
        self.assertIn({u'collection_name': u'airports'}, self.my_service.resources)
        self.assertIn({u'collection_name': u'cities'}, self.my_service.resources)

    def test_should_create_resources(self):
        self.assertTrue(self.my_service.airports)
        self.assertTrue(self.my_service.cities)

    def test_should_have_connect_variable(self):
        self.assertEqual(self.my_service.auth, {})

    def test_connect_with_apikey_should_tore_auth_values(self):
        self.my_service.connect('apikey', 'fake-user', 'fake-pass')

        expected_value = {'credentials': 'fake-user:fake-pass', 'type': 'apikey'}
        self.assertEqual(self.my_service.auth, expected_value)

    @mock.patch('pluct.service.Service._create_resources_attributes')
    def test_connect_with_apikey_recreate_resource_attributes(self, my_mock):
        self.my_service.connect('apikey', 'fake-user', 'fake-pass')

        expected_value = {'credentials': 'fake-user:fake-pass', 'type': 'apikey'}
        self.assertEqual(self.my_service.auth, expected_value)
        self.assertTrue(my_mock.called, 'should regenerate resource methods')

    def test_should_ignore_when_connect_with_unsuported_method(self):
        self.my_service.connect('other_method', 'fake-user', 'fake-pass')
        self.assertEqual(self.my_service.auth, {})

    def test_should_ignore_when_connect_with_unsuported_method(self):
        self.my_service.connect('other_method', 'fake-user', 'fake-pass')
        self.assertEqual(self.my_service.auth, {})

    @mock.patch('pluct.service.Service._create_resources_attributes')
    def test_should_ignore_when_connect_with_unsuported_method(self, my_mock):
        self.my_service.connect('other_method', 'fake-user', 'fake-pass')
        self.assertFalse(my_mock.called, 'should not regenerate resource methods')
