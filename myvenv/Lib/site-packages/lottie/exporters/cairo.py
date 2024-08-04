try:
    import cairosvg
    has_cairo = True
except (ImportError, OSError):
    has_cairo = False

from ..parsers import glaxnimate_helpers

import io

from .base import exporter
from .svg import export_svg


if glaxnimate_helpers.has_glaxnimate:
    @exporter("PNG", ["png"], [], {"frame"})
    def export_png(animation, fp, frame=0, dpi=96):
        data = glaxnimate_helpers.serialize(animation, "raster")

        if isinstance(fp, str):
            with open(fp, 'wb') as file:
                file.write(data)
        else:
            fp.write(data)

    def PngRenderer(animation, dpi):
        return glaxnimate_helpers.GlaxnimateRenderer(animation, "raster", dpi)

elif has_cairo:
    def _export_cairo(func, animation, fp, frame, dpi):
        intermediate = io.BytesIO()
        export_svg(animation, intermediate, frame, pretty=False)
        intermediate.seek(0)
        func(file_obj=intermediate, write_to=fp, dpi=dpi)

    @exporter("PNG", ["png"], [], {"frame"})
    def export_png(animation, fp, frame=0, dpi=96):
        _export_cairo(cairosvg.svg2png, animation, fp, frame, dpi)

    class PngRenderer:
        def __init__(self, animation, dpi):
            self.animation = animation
            self.dpi = dpi

        def __enter__(self):
            return self

        def __exit__(self, *a, **k):
            return

        def serialize(self, frame, file):
            export_png(self.animation, file, frame, self.dpi)

    @exporter("PDF", ["pdf"], [], {"frame"})
    def export_pdf(animation, fp, frame=0, dpi=96):
        _export_cairo(cairosvg.svg2pdf, animation, fp, frame, dpi)

    @exporter("PostScript", ["ps"], [], {"frame"})
    def export_ps(animation, fp, frame=0, dpi=96):
        _export_cairo(cairosvg.svg2ps, animation, fp, frame, dpi)
