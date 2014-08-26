# -*- coding: utf-8 -*-

# Shortcuts
from pluct.resource import Resource  # noqa
from pluct.schema import LazySchema, Schema  # noqa
from pluct.session import Session as Pluct

_pluct = Pluct()

resource = _pluct.resource
schema = _pluct.schema
