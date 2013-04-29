#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import mock
from pluct.request import Request


class RequestTestCase(unittest.TestCase):

    def test_should_pass_correct_parameter_to_request(self):
        request = Request(method='FAKE',
            href='http://my-awesome-api.com/collection/{my_parameter}',
            auth={}
        )
        url = request.get_url(my_parameter='foo')
        expected_url = 'http://my-awesome-api.com/collection/foo'
        self.assertEqual(url, expected_url)

    def test_should_be_possible_pass_many_parameter_in_single_url(self):
        request = Request(method='FAKE',
            href='http://my-awesome-api.com/collection/{my_parameter}/{my_other_parameter}',
            auth={}
        )
        url = request.get_url(my_parameter='foo', my_other_parameter='bar')
        expected_url = 'http://my-awesome-api.com/collection/foo/bar'
        self.assertEqual(url, expected_url)

