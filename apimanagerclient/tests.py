#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import unittest
from mock import patch, MagicMock
from apimanagerclient import Service


class SchemaMock(MagicMock):
    content = json.dumps({
        "extensions": {
            "list_endpoint": "/v1/extensions/",
            "schema": "/v1/extensions/schema/"
        },
        "portals": {
            "list_endpoint": "/v1/portals/",
            "schema": "/v1/portals/schema/"
        }
    })


class ServiceTestCase(unittest.TestCase):


    def setUp(self):
        super(ServiceTestCase, self).setUp()
        self.request_mock = patch('requests.get').start()
        self.request_mock.return_value = SchemaMock()

    def test_should_format_api_url(self):
        my_service = Service('my-api.com', 'v1')
        self.assertEqual(my_service.api_url, 'http://my-api.com/v1')

    def test_should_call_the_get_method(self):
        my_service = Service('my-api.com', 'v1')
        my_service.get_resources()
        self.request_mock.assert_called_once_with(
            url='http://my-api.com/v1', params={'format': 'json'}
        )

    def test_should_obtain_resources(self):
        my_service = Service('my-api.com', 'v1')
        expected_resources = my_service.get_resources()

        self.assertEqual(expected_resources, [u'portals', u'extensions'])


if __name__ == '__main__':
    unittest.main()
