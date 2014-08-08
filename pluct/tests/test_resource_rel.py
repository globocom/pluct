# -*- coding: utf-8 -*-

from unittest import TestCase
from mock import patch

from pluct.resource import Resource
from pluct.schema import Schema
from pluct.session import Session


class ResourceRelTestCase(TestCase):

    def setUp(self):
        raw_schema = {
            'links': [
                {
                    'rel': 'item',
                    'href': '/root/{id}',
                },
                {
                    'rel': 'related',
                    'href': '/root/{slug}/{related}',
                },
                {
                    'rel': 'create',
                    'href': '/root',
                    'method': 'post',
                },
                {
                    'rel': 'list',
                    'href': '/root',
                }
            ]
        }
        data = {'id': '123', 'slug': 'slug'}

        self.session = Session()
        self.schema = Schema('/schema', raw_schema)
        self.resource = Resource(
            '/', data=data, schema=self.schema, session=self.session)

        self.request_patcher = patch.object(self.session, 'request')
        self.request = self.request_patcher.start()

    def tearDown(self):
        self.request_patcher.stop()

    def test_delegates_request_to_session(self):
        self.resource.rel('create')
        self.request.assert_called_with('post', '/root')

    def test_accepts_extra_parameters(self):
        self.resource.rel('create', timeout=333)
        self.request.assert_called_with('post', '/root', timeout=333)

    def test_uses_get_as_default_verb(self):
        self.resource.rel('list')
        self.request.assert_called_with('get', '/root')

    def test_expands_uri_using_resource_data(self):
        self.resource.rel('item')
        self.request.assert_called_with('get', '/root/123')

    def test_expands_uri_using_params(self):
        self.resource.rel('item', params={'id': 345})
        self.request.assert_called_with('get', '/root/345', params={})

    def test_expands_uri_using_resource_data_and_params(self):
        self.resource.rel('related', params={'related': 'something'})
        self.request.assert_called_with(
            'get', '/root/slug/something', params={})

    def test_extracts_expanded_params_from_the_uri(self):
        self.resource.rel('item', params={'id': 345, 'fields': 'slug'})
        self.request.assert_called_with(
            'get', '/root/345', params={'fields': 'slug'})
