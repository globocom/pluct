# -*- coding: utf-8 -*-

from unittest import TestCase

from mock import ANY, Mock, patch

from pluct.session import Session
from pluct.resource import Resource


class SessionInitializationTestCase(TestCase):

    def test_keeps_timeout(self):
        session = Session(timeout=999)
        self.assertEqual(session.timeout, 999)

    def test_uses_requests_session_as_default_client(self):
        with patch('pluct.session.RequestsSession') as client:
            Session()
            client.assert_called_with()

    def test_allows_custom_client(self):
        custom_client = Mock()
        session = Session(client=custom_client)
        self.assertEqual(session.client, custom_client)


class SessionRequestsTestCase(TestCase):

    def setUp(self):
        self.response = Mock()
        self.client = Mock()
        self.client.request.return_value = self.response

        self.session = Session()
        self.session.client = self.client

    def test_delegates_request_to_client(self):
        self.session.request('get', '/')
        self.client.request.assert_called_with(
            'get', '/', headers=ANY)

    def test_uses_default_timeout(self):
        self.session.timeout = 333
        self.session.request('get', '/')
        self.client.request.assert_called_with(
            'get', '/', timeout=333, headers=ANY)

    def test_allows_custom_timeout_per_request(self):
        self.session.request('get', '/', timeout=999)
        self.client.request.assert_called_with(
            'get', '/', timeout=999, headers=ANY)

    def test_applies_json_content_type_header(self):
        self.session.request('get', '/')
        self.client.request.assert_called_with(
            'get', '/', headers={'content-type': 'application/json'})

    def test_allows_custom_content_type_header(self):
        custom_headers = {'content-type': 'application/yaml'}
        self.session.request('get', '/', headers=custom_headers)
        self.client.request.assert_called_with(
            'get', '/', headers=custom_headers)

    def test_returns_response(self):
        response = self.session.request('get', '/')
        self.assertIs(response, self.response)


class SessionResourceTestCase(TestCase):

    def setUp(self):
        self.response = Mock()
        self.session = Session()

        patch.object(self.session, 'request').start()
        self.session.request.return_value = self.response

    def tearDown(self):
        patch.stopall()

    def test_creates_resource_from_response(self):
        with patch('pluct.session.from_response') as from_response:
            self.session.resource('get', '/')
            from_response.assert_called_with(
                klass=Resource, response=self.response)
