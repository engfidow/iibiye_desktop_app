try:
    import glaxnimate
    has_glaxnimate = True
except ImportError:
    has_glaxnimate = False

import json
from ..nvector import NVector, Point


def convert(animation, exporter_slug):
    with glaxnimate.environment.Headless():
        document = glaxnimate.model.Document("")
        glaxnimate.io.registry.from_slug("lottie").load(document, json.dumps(animation.to_dict()).encode("utf8"))
        return glaxnimate.io.registry.from_slug(exporter_slug).save(document)


def serialize(animation, serializer_slug, time=0):
    with glaxnimate.environment.Headless():
        document = glaxnimate.model.Document("")
        glaxnimate.io.registry.from_slug("lottie").load(document, json.dumps(animation.to_dict()).encode("utf8"))
        document.current_time = time
        return glaxnimate.io.registry.serializer_from_slug(serializer_slug).serialize([document.main])


class GlaxnimateRenderer:
    def __init__(self, animation, serializer_slug, dpi):
        self.context = glaxnimate.environment.Headless()
        self.serializer_slug = serializer_slug
        self.serializer = None
        self.document = None
        self.animation = animation
        # TODO dpi

    def __enter__(self):
        self.context.__enter__()
        self.serializer = glaxnimate.io.registry.serializer_from_slug(self.serializer_slug)
        self.document = glaxnimate.model.Document("")
        glaxnimate.io.registry.from_slug("lottie").load(self.document, json.dumps(self.animation.to_dict()).encode("utf8"))
        return self

    def __exit__(self, *a, **k):
        self.context.__exit__(*a, **k)

    def serialize(self, frame, fp):
        self.document.current_time = frame
        data = self.serializer.serialize([self.document.main])
        if fp:
            fp.write(data)
        return data


def color_to_glaxnimate(color: NVector):
    return glaxnimate.utils.Color(*(color * 255).components)


def color_from_glaxnimate(color):
    return NVector(color.red / 255., color.green / 255., color.blue / 255., color.alpha / 255.)


def point_from_glaxnimate(point):
    return Point(point.x, point.y)
