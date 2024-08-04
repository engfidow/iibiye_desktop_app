from .base import LottieObject, LottieProp, PseudoBool, Index
from .layers import Layer, PreCompLayer
from .assets import Asset, Precomp
from .text import FontList, Chars
from .composition import Composition
from .helpers import VisualObject, Marker

##\defgroup Lottie Lottie
#
# Objects of the lottie file structure.

## \defgroup LottieCheck Lottie (to check)
#
# Lottie objects that have not been tested


## @ingroup Lottie
class Metadata(LottieObject):
    """!
    Document metadata
    """
    _props = [
        LottieProp("author", "a", str, False),
        LottieProp("generator", "g", str, False),
        LottieProp("keywords", "k", str, True),
        LottieProp("description", "d", str, False),
        LottieProp("theme_color", "tc", str, False),
    ]

    def __init__(self):
        self.generator = None
        self.author = None
        self.keywords = None
        self.description = None
        self.theme_color = None


#ingroup Lottie
class UserMetadata(LottieObject):
    """!
    User-defined metadata
    """
    _props = [
        LottieProp("filename", "filename", str, False),
        LottieProp("custom_properties", "customProps", dict, False),
    ]

    def __init__(self):
        super().__init__()

        self.filename = None
        self.custom_properties = {}


#ingroup Lottie
class MotionBlur(LottieObject):
    """!
    Motion blur settings
    """
    _props = [
        LottieProp("shutter_angle", "sa", float, False),
        LottieProp("shutter_phase", "sp", float, False),
        LottieProp("samples_per_frame", "spf", float, False),
        LottieProp("adaptive_sample_limit", "asl", float, False),
    ]

    def __init__(self):
        super().__init__()

        ## Angle in degrees
        self.shutter_angle = None
        ## Angle in degrees
        self.shutter_phase = None
        self.samples_per_frame = None
        self.adaptive_sample_limit = None


## @ingroup Lottie
class Animation(Composition, VisualObject):
    """!
    Top level object, describing the animation

    @see http://docs.aenhancers.com/items/compitem/
    """
    _props = [
        LottieProp("version", "v", str, False),
        LottieProp("frame_rate", "fr", float, False),
        LottieProp("in_point", "ip", float, False),
        LottieProp("out_point", "op", float, False),
        LottieProp("width", "w", int, False),
        LottieProp("height", "h", int, False),
        LottieProp("threedimensional", "ddd", PseudoBool, False),
        LottieProp("assets", "assets", Asset, True),
        LottieProp("extra_compositions", "comps", Precomp, True),
        LottieProp("fonts", "fonts", FontList),
        LottieProp("chars", "chars", Chars, True),
        LottieProp("markers", "markers", Marker, True),
        LottieProp("motion_blur", "mb", MotionBlur, False),
        LottieProp("metadata", "meta", Metadata, False),
        LottieProp("user_metadata", "metadata", UserMetadata, False),
    ]
    _version = "5.5.2"

    def __init__(self, n_frames=60, framerate=60):
        super().__init__()
        ## The time when the composition work area begins, in frames.
        self.in_point = 0
        ## The time when the composition work area ends.
        ## Sets the final Frame of the animation
        self.out_point = n_frames
        ## Frames per second
        self.frame_rate = framerate
        ## Composition Width
        self.width = 512
        ## Composition has 3-D layers
        self.threedimensional = False
        ## Composition Height
        self.height = 512
        ## Bodymovin Version
        self.version = self._version
        ## source items that can be used in multiple places. Comps and Images for now.
        self.assets = [] # Image, Precomp
        ## List of Extra compositions not referenced by anything
        self.extra_compositions = None
        ## source chars for text layers
        self.chars = None
        ## Available fonts
        self.fonts = None
        self.metadata = None
        self.user_metadata = None
        self.motion_blur = None
        self.markers = None

    def precomp(self, name):
        for ass in self.assets:
            if isinstance(ass, Precomp) and ass.id == name:
                return ass
        return None

    def _on_prepare_layer(self, layer):
        if layer.in_point is None:
            layer.in_point = self.in_point
        if layer.out_point is None:
            layer.out_point = self.out_point

    def to_precomp(self):
        """!
        Turns the main comp into a precomp
        """
        precomp = Precomp()
        #precomp.frame_rate = self.frame_rate
        precomp.layers = self.layers
        precomp.name = self.name
        name_id = 0
        base_name = self.name or "Animation"
        name = base_name
        index = 0
        while True:
            if index >= len(self.assets):
                break

            while self.assets[index].id == name:
                name_id += 1
                name = "%s %s" % (base_name, name_id)
                index = -1

            index += 1
        precomp.id = name
        self.assets.append(precomp)

        precomp_layer = PreCompLayer()
        precomp_layer.width = self.width
        precomp_layer.height = self.height
        precomp_layer.in_point = self.in_point
        precomp_layer.out_point = self.out_point
        precomp_layer.reference_id = name
        self.layers = [precomp_layer]
        return precomp

    def scale(self, width, height):
        """!
        Scales the animation so it fits in width/height
        """
        if self.width != width or self.height != height:
            self.to_precomp()

            scale = min(width/self.width, height/self.height)
            self.width = width
            self.height = height

            self.layers[0].transform.scale.value *= scale

    def tgs_sanitize(self):
        """!
        Cleans up some things to ensure it works as a telegram sticker
        """
        self.scale(512, 512)

        if self.frame_rate < 45:
            self.frame_rate = 30
        else:
            self.frame_rate = 60

    def _fixup(self):
        super()._fixup()
        if self.assets:
            for ass in self.assets:
                if isinstance(ass, Precomp):
                    ass.animation = self
                    ass._fixup()

    def __str__(self):
        return self.name or super().__str__()
