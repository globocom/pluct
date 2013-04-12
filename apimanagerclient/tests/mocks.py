#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import mock


class ServiceSchemaMock(mock.MagicMock):
    headers = {
        'content-type': 'application/json'
    }
    status_code = 200
    content = json.dumps(
        {
            'items': [
                {
                    'collection_name': "airports",
                    # 'resource_id': "airport",
                },
                {
                    'collection_name': "cities",
                    # 'resource_id': "city",
                }
            ],
            'item_count': 2
        }
    )


class ResourceSchemaMock(mock.MagicMock):
    headers = {
        'content-type': 'application/json'
    }
    status_code = 200
    content = json.dumps({
        'allowed_list_http_methods': [
            "get"
        ],
        }
    )


class ResourceItemsMock(mock.MagicMock):
    headers = {
        'content-type': 'application/json'
    }
    status_code = 200
    content = json.dumps({
        'items': [
            {
                u'name': u"Rio de Janeiro",
                u'resource_id': u"rio-de-janeiro"
            },
            {
                u'name': u"São Paulo",
                u'resource_id': u"sao-paulo"
            },
            {
                u'name': u"Recife",
                u'resource_id': u"recife"
            },
        ],
        }
    )