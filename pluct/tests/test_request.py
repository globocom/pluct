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

    def test_should_raise_an_error_when_passed_wrong_parameter(self):
        request = Request(method='FAKE',
            href='http://my-awesome-api.com/collection/{my_parameter}',
            auth={}
        )
        self.assertRaises(TypeError, request.get_url, wrong_parameter='foo')

    def test_should_raise_mesage_with_wrong_and_correct_parameters(self):
        request = Request(method='FAKE',
            href='http://my-awesome-api.com/collection/{my_parameter}',
            auth={}
        )
        try:
            request.get_url(wrong_parameter='foo')
        except TypeError, e:
            self.assertEqual(e.message, 'Wrong parameters: "wrong_parameter". Valid parameters: "my_parameter"')

    def test_should_raise_mesage_with_wrong_parameters(self):
        request = Request(method='FAKE',
            href='http://my-awesome-api.com/collection/',
            auth={}
        )
        try:
            request.get_url(extra_parameter='foo')
        except TypeError, e:
            self.assertEqual(e.message, 'Wrong parameters: "extra_parameter". This method takes no parameter.')

    def test_should_raise_mesage_with_no_parameters_passed(self):
        request = Request(method='FAKE',
            href='http://my-awesome-api.com/collection/{the_parameter}',
            auth={}
        )
        try:
            request.get_url()
        except TypeError, e:
            self.assertEqual(e.message, 'You did not set any parameter. Valid parameters: "the_parameter"')