import warnings
from .base import LottieProp
from .helpers import VisualObject
from .properties import ColorValue, Value, GradientColors
from .shapes import GradientType


#ingroup Lottie
class LayerStyle(VisualObject):
    """!
    Style applied to a layer
    """
    _props = [
        LottieProp("type", "ty", int, False),
    ]
    type = None
    _classes = {}

    @classmethod
    def _load_get_class(cls, lottiedict):
        if not LayerStyle._classses:
            LayerStyle._classses = {
                sc.type: sc
                for sc in LayerStyle.__subclasses__()
            }
        type_id = lottiedict["ty"]
        if type_id not in LayerStyle._classses:
            warnings.warn("Unknown style type: %s" % type_id)
            return LayerStyle
        return LayerStyle._classses[type_id]


#ingroup Lottie
class BevelEmbossStyle(LayerStyle):
    type = 5
    _props = [
        LottieProp("type", "ty", int, False),
        LottieProp("bevel_style", "bs", Value, False),
        LottieProp("technique", "bt", Value, False),
        LottieProp("strength", "sr", Value, False),
        LottieProp("size", "s", Value, False),
        LottieProp("soften", "sf", Value, False),
        LottieProp("global_angle", "ga", Value, False),
        LottieProp("angle", "a", Value, False),
        LottieProp("altitude", "ll", Value, False),
        LottieProp("highlight_mode", "hm", Value, False),
        LottieProp("highlight_color", "hc", ColorValue, False),
        LottieProp("highlight_opacity", "ho", Value, False),
        LottieProp("shadow_mode", "sm", Value, False),
        LottieProp("shadow_color", "sc", ColorValue, False),
        LottieProp("shadow_opacity", "so", Value, False),
    ]

    def __init__(self):
        super().__init__()

        self.bevel_style = None
        self.technique = None
        self.strength = None
        self.size = None
        self.soften = None
        ## Use global light
        self.global_angle = None
        ## Local lighting angle
        self.angle = None
        ## Local lighting altitude
        self.altitude = None
        self.highlight_mode = None
        self.highlight_color = None
        self.highlight_opacity = None
        self.shadow_mode = None
        self.shadow_color = None
        self.shadow_opacity = None


#ingroup Lottie
class ColorOverlayStyle(LayerStyle):
    type = 7
    _props = [
        LottieProp("type", "ty", int, False),
        LottieProp("blend_mode", "bm", Value, False),
        LottieProp("color", "c", ColorValue, False),
        LottieProp("opacity", "so", Value, False),
    ]

    def __init__(self):
        super().__init__()

        self.blend_mode = None
        self.color = None
        self.opacity = None


#ingroup Lottie
class DropShadowStyle(LayerStyle):
    type = 1
    _props = [
        LottieProp("type", "ty", int, False),
        LottieProp("color", "c", ColorValue, False),
        LottieProp("opacity", "o", Value, False),
        LottieProp("angle", "a", Value, False),
        LottieProp("size", "s", Value, False),
        LottieProp("distance", "d", Value, False),
        LottieProp("choke_spread", "ch", Value, False),
        LottieProp("blend_mode", "bm", Value, False),
        LottieProp("noise", "no", Value, False),
        LottieProp("layer_conceal", "lc", Value, False),
    ]

    def __init__(self):
        super().__init__()

        self.color = None
        self.opacity = None
        ## Local light angle
        self.angle = None
        ## Blur size
        self.size = None
        self.distance = None
        self.choke_spread = None
        self.blend_mode = None
        self.noise = None
        ## Layer knowck out drop shadow
        self.layer_conceal = None


#ingroup Lottie
class GradientOverlayStyle(LayerStyle):
    type = 8
    _props = [
        LottieProp("type", "ty", int, False),
        LottieProp("blend_mode", "bm", Value, False),
        LottieProp("opacity", "o", Value, False),
        LottieProp("gradient", "gf", GradientColors, False),
        LottieProp("smoothness", "gs", Value, False),
        LottieProp("angle", "a", Value, False),
        LottieProp("gradient_type", "gt", GradientType, False),
        LottieProp("reverse", "re", Value, False),
        LottieProp("align", "al", Value, False),
        LottieProp("scale", "s", Value, False),
        LottieProp("offset", "of", Value, False),
    ]

    def __init__(self):
        super().__init__()

        self.blend_mode = None
        self.opacity = None
        self.gradient = None
        self.smoothness = None
        self.angle = None
        self.gradient_type = None
        self.reverse = None
        ## Align with layer
        self.align = None
        self.scale = None
        self.offset = None


#ingroup Lottie
class InnerGlowStyle(LayerStyle):
    type = 4
    _props = [
        LottieProp("type", "ty", int, False),
        LottieProp("color", "c", ColorValue, False),
        LottieProp("opacity", "o", Value, False),
        LottieProp("range", "r", Value, False),
        LottieProp("source", "sr", Value, False),
        LottieProp("choke_spread", "ch", Value, False),
        LottieProp("blend_mode", "bm", Value, False),
        LottieProp("noise", "no", Value, False),
        LottieProp("jitter", "j", Value, False),
    ]

    def __init__(self):
        super().__init__()

        self.color = None
        self.opacity = None
        self.range = None
        self.source = None
        self.choke_spread = None
        self.blend_mode = None
        self.noise = None
        self.jitter = None


#ingroup Lottie
class OuterGlowStyle(LayerStyle):
    type = 3
    _props = [
        LottieProp("type", "ty", int, False),
        LottieProp("color", "c", ColorValue, False),
        LottieProp("opacity", "o", Value, False),
        LottieProp("range", "r", Value, False),
        LottieProp("choke_spread", "ch", Value, False),
        LottieProp("blend_mode", "bm", Value, False),
        LottieProp("noise", "no", Value, False),
        LottieProp("jitter", "j", Value, False),
    ]

    def __init__(self):
        super().__init__()

        self.color = None
        self.opacity = None
        self.range = None
        self.choke_spread = None
        self.blend_mode = None
        self.noise = None
        self.jitter = None


#ingroup Lottie
class InnerShadowStyle(LayerStyle):
    type = 2
    _props = [
        LottieProp("type", "ty", int, False),
        LottieProp("color", "c", ColorValue, False),
        LottieProp("opacity", "o", Value, False),
        LottieProp("angle", "a", Value, False),
        LottieProp("size", "s", Value, False),
        LottieProp("distance", "d", Value, False),
        LottieProp("choke_spread", "ch", Value, False),
        LottieProp("blend_mode", "bm", Value, False),
        LottieProp("noise", "no", Value, False),
    ]

    def __init__(self):
        super().__init__()

        self.color = None
        self.opacity = None
        ## Local light angle
        self.angle = None
        ## Blur size
        self.size = None
        self.distance = None
        self.choke_spread = None
        self.blend_mode = None
        self.noise = None


#ingroup Lottie
class SatinStyle(LayerStyle):
    type = 6

    _props = [
        LottieProp("type", "ty", int, False),
        LottieProp("blend_mode", "bm", Value, False),
        LottieProp("color", "c", ColorValue, False),
        LottieProp("opacity", "o", Value, False),
        LottieProp("angle", "a", Value, False),
        LottieProp("distance", "d", Value, False),
        LottieProp("size", "s", Value, False),
        LottieProp("invert", "in", Value, False),
    ]

    def __init__(self):
        super().__init__()

        self.blend_mode = None
        self.color = None
        self.opacity = None
        self.angle = None
        self.distance = None
        self.size = None
        self.invert = None


#ingroup Lottie
class StrokeStyle(LayerStyle):
    """!
    Stroke / frame
    """
    type = 0

    _props = [
        LottieProp("type", "ty", int, False),
        LottieProp("size", "s", Value, False),
        LottieProp("color", "c", ColorValue, False),
    ]

    def __init__(self):
        super().__init__()

        self.size = None
        self.color = None
