# -*- coding: utf-8 -*-

from unittest import TestCase
from pluct.resource import get

API_ENDPOINT = "http://brainiak.semantica.dev.globoi.com"
#API_ENDPOINT = "http://localhost:5100"

class AcceptListContexts(TestCase):
    def setUp(self):
        self.proxy = get(API_ENDPOINT)

    def test_valid_root_json_schema(self):
        proxy_is_valid = self.proxy.is_valid()
        self.assertTrue(proxy_is_valid)
