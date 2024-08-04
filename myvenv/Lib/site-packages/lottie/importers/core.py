from .base import importer
from ..parsers.tgs import parse_tgs


@importer("Lottie JSON / Telegram Sticker", ["json", "tgs"], slug="lottie")
def import_tgs(file, *a, **kw):
    """
    Imports a (optionally gzipped) Lottie JSON file
    """
    return parse_tgs(file, *a, **kw)


import_lottie = import_tgs
