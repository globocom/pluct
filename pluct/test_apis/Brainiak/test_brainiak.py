# -*- coding: utf-8 -*-

from unittest import TestCase
from pluct.resource import get

API_ENDPOINT = "http://brainiak.semantica.dev.globoi.com"
#API_ENDPOINT = "http://localhost:5100"


class ValidateResources(TestCase):

    def test_valid_root(self):
        root = get(API_ENDPOINT)
        self.assertTrue(root.is_valid())
