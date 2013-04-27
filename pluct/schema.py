from pluct.request import Request


class Schema(object):
    def __init__(self, url, title=None, required=None):
        self.url = url
        self.required = required
        self.title = title


def get(url, auth=None):
    data = Request("GET", url, auth).process().json
    return Schema(
        url=url,
        required=data.get("required"),
        title=data.get("title")
    )
