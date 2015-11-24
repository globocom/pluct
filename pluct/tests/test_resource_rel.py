# -*- coding: utf-8 -*-

import json

from unittest import TestCase
from mock import patch, Mock
from copy import deepcopy

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
                    'method': 'POST',
                },
                {
                    'rel': 'list',
                    'href': '/root',
                }
            ]
        }
        self.data = {'id': '123',
                     'slug': 'slug',
                     'items': [{"ide": 1},
                               {"ida": 2}]}

        self.session = Session()
        self.schema = Schema('/schema', raw_schema, session=self.session)

        self.response = Mock()
        self.response.url = 'http://example.com'

        self.profile_url = 'http://example.com/schema'

        content_type = 'application/json; profile=%s' % (self.profile_url)
        self.response.headers = {
            'content-type': content_type
        }

        self.resource = Resource.from_data(
            'http://much.url.com/',
            data=deepcopy(self.data), schema=self.schema, session=self.session
        )

        self.resource2 = Resource.from_data(
            'http://much.url.com/',
            data=deepcopy(self.data), schema=self.schema,
            session=self.session, response=self.response
        )

        self.request_patcher = patch.object(self.session, 'request')
        self.request = self.request_patcher.start()

    def tearDown(self):
        self.request_patcher.stop()

    def test_rel_follows_content_type_profile(self):
        self.resource2.rel('create', data=self.resource2)
        self.request.assert_called_with(
            'http://much.url.com/root',
            method='post',
            data=json.dumps(self.data),
            headers=self.response.headers
        )

    def test_get_content_type_for_resource_default(self):
        content_type = self.resource._get_content_type_for_resource(
            self.resource)
        self.assertEqual(content_type, 'application/json; profile=/schema')

    def test_get_content_type_for_resource_with_response(self):
        content_type = self.resource2._get_content_type_for_resource(
            self.resource2)
        self.assertEqual(content_type, self.response.headers['content-type'])

    def test_expand_uri_returns_simple_link(self):
        uri = self.resource.expand_uri('create')
        self.assertEqual(uri, '/root')

    def test_expand_uri_returns_interpolated_link(self):
        uri = self.resource.expand_uri('related', related='foo')
        self.assertEqual(uri, '/root/slug/foo')

    def test_has_rel_finds_existent_link(self):
        self.assertTrue(self.resource.has_rel('create'))

    def test_has_rel_detects_unexistent_link(self):
        self.assertFalse(self.resource.has_rel('foo_bar'))

    def test_delegates_request_to_session(self):
        self.resource.rel('create', data=self.resource)
        self.request.assert_called_with(
            'http://much.url.com/root',
            method='post',
            data=json.dumps(self.data),
            headers={'content-type': 'application/json; profile=/schema'}
        )

    def test_accepts_extra_parameters(self):
        self.resource.rel('create', data=self.resource, timeout=333)
        self.request.assert_called_with(
            'http://much.url.com/root',
            method='post',
            data=json.dumps(self.data),
            headers={'content-type': 'application/json; profile=/schema'},
            timeout=333
        )

    def test_accepts_dict(self):
        resource = {'name': 'Testing'}
        self.resource.rel('create', data=resource)
        self.request.assert_called_with(
            'http://much.url.com/root',
            method='post',
            data=json.dumps(resource),
            headers={'content-type': 'application/json'}
        )

    def test_uses_get_as_default_verb(self):
        self.resource.rel('list')
        self.request.assert_called_with(
            'http://much.url.com/root', method='get'
        )

    def test_expands_uri_using_resource_data(self):
        self.resource.rel('item')
        self.request.assert_called_with(
            'http://much.url.com/root/123', method='get'
        )

    def test_expands_uri_using_params(self):
        self.resource.rel('item', params={'id': 345})
        self.request.assert_called_with(
            'http://much.url.com/root/345', method='get', params={}
        )

    def test_expands_uri_using_resource_data_and_params(self):
        self.resource.rel('related', params={'related': 'something'})
        self.request.assert_called_with(
            'http://much.url.com/root/slug/something', method='get', params={}
        )

    def test_extracts_expanded_params_from_the_uri(self):
        self.resource.rel('item', params={'id': 345, 'fields': 'slug'})
        self.request.assert_called_with(
            'http://much.url.com/root/345',
            method='get', params={'fields': 'slug'}
        )
