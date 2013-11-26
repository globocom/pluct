pluct
=====

[![Build Status](https://drone.io/github.com/globocom/pluct/status.png)](https://drone.io/github.com/globocom/pluct/latest)
[![Build Status](https://travis-ci.org/globocom/pluct.png)](https://travis-ci.org/globocom/pluct)

```python
from pluct import resource
app = resource.get("http://myapi.com/app/myapp")
```

verifying if the resource is valid:
```python
app.is_valid()
```

retrieve the resource data:
```python
app.data
```

retrieve the resource schema:
```python
app.schema
```

Limitations
-----------

*pluct* is an experimental project. its limitations:

* partial support for draft 4.


Tests
-----

The ``tests`` directory contains the standard test stack for pluct.

The ``test_apis`` directory contains a different test stack, to validate APIs that are pluct-complaint.
If you adopt pluct to interact with a public API, you can add sub-folder to test_apis to document and test it.
If any test under ``test_apis`` breaks, this does not necessarily mean that there is a problem with pluct.
In order to validate pluct, check exclusively the ``tests`` stack.


