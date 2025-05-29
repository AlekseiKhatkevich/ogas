import functools

from faststream.constants import ContentTypes

contentype_json = functools.partial(lambda msg: msg.content_type == ContentTypes.json)
