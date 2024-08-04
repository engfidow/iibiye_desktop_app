import re
from xml.etree import ElementTree

from .base import importer


_fixcrap_re = re.compile(r'(")([^"]+)(")')


def _fixcrap_item(s) -> str:
    return s.group(1) + s.group(2).replace("&", "&amp;") + s.group(3)


def _fixcrap(s: str) -> str:
    return _fixcrap_re.sub(_fixcrap_item, s)


@importer("OpenToonz", ["tnz"])
def import_opentoonz(file):
    if isinstance(file, str):
        with open(file, "r") as fobj:
            xml_data = fobj.read()
    else:
        xml_data = file.read()
        if not isinstance(xml_data, str):
            xml_data = xml_data.decode("utf-8")

    xml_data = _fixcrap(xml_data)

    xml = ElementTree.fromstring(xml_data)

    width, height = map(float, xml.find("./properties/cameras/camera/cameraRes").text.strip().split())

    print((width, height))

    import sys; sys.exit(0)

