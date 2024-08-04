from xml.dom import minidom
from xml.etree import ElementTree

from .base import exporter
from ..parsers.baseporter import ExtraOption
from ..parsers.svg.builder import to_svg
from ..utils.file import open_file


def _print_ugly_xml(dom, file):
    return dom.write(file, "utf-8", True)


def _print_pretty_xml(dom, file):
    with open_file(file) as fp:
        xmlstr = minidom.parseString(ElementTree.tostring(dom.getroot())).toprettyxml(indent="   ")
        fp.write(xmlstr)


@exporter("SVG", ["svg"], [
    ExtraOption("animated", action="store_true", help="Export animated svg"),
], {"pretty", "frame"})
def export_svg(animation, file, frame=0, pretty=True, animated=False):
    _print_xml = _print_pretty_xml if pretty else _print_ugly_xml
    _print_xml(to_svg(animation, frame, animated), file)
