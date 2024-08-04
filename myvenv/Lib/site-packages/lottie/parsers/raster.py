from PIL import Image
import glaxnimate
from . import glaxnimate_helpers
import enum
from .. import objects
from ..nvector import NVector
from .pixel import _vectorizing_func


class QuantizationMode(enum.Enum):
    Nearest = 1
    Exact = 2


class PaletteAlgorithm:
    def get_colors(self, image, n_colors):
        pass


class KMeansPalette(PaletteAlgorithm):
    def __init__(self, iterations=100, match=glaxnimate.utils.quantize.MatchType.MostFrequent):
        self.iterations = iterations
        self.match = match

    def get_colors(self, image, n_colors):
        return glaxnimate.utils.quantize.k_means(image, n_colors, self.iterations, self.match)


class OctreePalette(PaletteAlgorithm):
    def get_colors(self, image, n_colors):
        return glaxnimate.utils.quantize.octree(image, n_colors)


class KModesPalette(PaletteAlgorithm):
    def get_colors(self, image, n_colors):
        return glaxnimate.utils.quantize.k_modes(image, n_colors)


class EdgeExclusionModesPalette(PaletteAlgorithm):
    def __init__(self, min_frequency=0.0005):
        self.min_frequency = min_frequency

    def get_colors(self, image, n_colors):
        return glaxnimate.utils.quantize.edge_exclusion_modes(image, n_colors, self.min_frequency)


class TraceOptions:
    def __init__(
        self,
        color_mode=QuantizationMode.Nearest,
        palette_algorithm=OctreePalette(),
        tolerance=100,
        stroke_width=1,
        smoothness=0.75,
        min_area=16
    ):
        self.trace_options = glaxnimate.utils.trace.TraceOptions()
        self.palette_algorithm = palette_algorithm
        self.color_mode = color_mode
        self.tolerance = tolerance
        self.stroke_width = stroke_width
        self.min_area = min_area
        self.smoothness = smoothness

    @property
    def smoothness(self):
        return self.trace_options.smoothness

    @smoothness.setter
    def smoothness(self, value):
        self.trace_options.smoothness = value

    @property
    def min_area(self):
        return self.trace_options.min_area

    @min_area.setter
    def min_area(self, value):
        self.trace_options.min_area = value

    def quantize(self, image, n_colors):
        """!
        Returns a list of RGB values
        """
        return self.palette_algorithm.get_colors(image, n_colors)

    def trace(self, image, codebook):
        """!
        Returns a list of tuple [color, data] where for each color in codebook
        data is a list of bezier

        You can get codebook from quantize()
        """

        if codebook is None or len(codebook) == 0:
            tracer = glaxnimate.utils.trace.Tracer(image, self.trace_options)
            tracer.set_target_alpha(128, False)
            return [glaxnimate.utils.Color(0, 0, 0), tracer.trace()]

        if self.color_mode == QuantizationMode.Nearest:
            return list(zip(codebook, glaxnimate.utils.trace.quantize_and_trace(image, self.trace_options, codebook)))

        mono_data = []
        tracer = glaxnimate.utils.trace.Tracer(image, self.trace_options)
        for color in codebook:
            tracer.set_target_color(color, self.tolerance)
            mono_data.append((color, tracer.trace()))

        return mono_data


class Vectorizer:
    def __init__(self, trace_options: TraceOptions):
        self.palette = None
        self.layers = {}
        self.trace_options = trace_options

    def _create_layer(self, animation, layer_name):
        layer = animation.add_layer(objects.ShapeLayer())
        if layer_name:
            self.layers[layer_name] = layer
            layer.name = layer_name
        return layer

    def prepare_layer(self, animation, layer_name=None):
        layer = self._create_layer(animation, layer_name)
        layer._max_verts = {}
        for color in self.palette:
            group = layer.add_shape(objects.Group())
            group.name = "color_%s" % color.name
            layer._max_verts[group.name] = 0
            fcol = glaxnimate_helpers.color_from_glaxnimate(color)
            group.add_shape(objects.Fill(NVector(*fcol)))
            if self.trace_options.stroke_width > 0:
                group.add_shape(objects.Stroke(NVector(*fcol), self.trace_options.stroke_width))
        return layer

    def raster_to_layer(self, animation, raster, layer_name=None):
        layer = self.prepare_layer(animation, layer_name)
        mono_data = self.trace_options.trace(raster, self.palette)
        for (color, beziers), group in zip(mono_data, layer.shapes):
            self.traced_to_shapes(group, beziers)
        return layer

    def traced_to_shapes(self, group, beziers):
        shapes = []
        for bezier in beziers:
            shape = group.insert_shape(0, objects.Path())
            shapes.append(shape)
            shape.shape.value = self.traced_to_bezier(bezier)
        return shapes

    def traced_to_bezier(self, path):
        bezier = objects.Bezier()
        for point in path:
            pos = glaxnimate_helpers.point_from_glaxnimate(point.pos)
            tan_in = glaxnimate_helpers.point_from_glaxnimate(point.tan_in - point.pos)
            tan_out = glaxnimate_helpers.point_from_glaxnimate(point.tan_out - point.pos)
            bezier.add_point(pos, tan_in, tan_out)
        if path.closed:
            bezier.closed = True
        return bezier


def raster_to_animation(
    filenames,
    n_colors=1,
    frame_delay=1,
    framerate=60,
    palette=[],
    trace_options=TraceOptions()
):
    vc = Vectorizer(trace_options)

    def callback(animation, raster, frame, time, duration):
        if vc.palette is None:
            if palette:
                vc.palette = [glaxnimate_helpers.color_to_glaxnimate(c) for c in palette]
            elif n_colors > 1:
                vc.palette = trace_options.quantize(raster, n_colors)
            else:
                vc.palette = [glaxnimate.utils.Color(0, 0, 0, 255)]
        layer = vc.raster_to_layer(animation, raster, "frame_%s" % frame)
        layer.in_point = time
        layer.out_point = layer.in_point + duration

    animation = _vectorizing_func(filenames, frame_delay, framerate, callback)

    return animation
