from pluct.request import Request


class Schema(object):
    def __init__(self, url, required):
        self.url = url
        self.required = required


def get(url, auth=None):
    data = Request("GET", url, auth).process().json
    return Schema(
        url=url,
        required=data.get("required")
    )
