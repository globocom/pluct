# -*- coding: utf-8 -*-
# Used to mock validate method on tests
from pluct import resource
resources = resource

# Shortcuts
from pluct.resource import Resource  # noqa
from pluct.schema import LazySchema, Schema  # noqa
from pluct.session import Session as Pluct  # noqa

_pluct = Pluct()

resource = _pluct.resource
schema = _pluct.schema
