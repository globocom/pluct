from unittest import TestCase
from mock import patch

from pluct import resource


class NewResourceTestCase(TestCase):
    @patch("requests.get")
    def setUp(self, get):
        self.url = "http://app.com/content"
        self.result = resource.get(url=self.url)

    def test_get_should_returns_a_resource(self):
        self.assertIsInstance(self.result, resource.NewResource)
