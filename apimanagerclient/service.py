#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests


class Service(object):
    def __init__(self, url, version):
        self.api_url = "http://{0}/{1}".format(url,version)
        self.version = version
        self.resources = []

    def get_resources(self):
        response = requests.get(url=self.api_url, params={'format':'json'})
        resource_dict = json.loads(response.content)
        return resource_dict.keys()
