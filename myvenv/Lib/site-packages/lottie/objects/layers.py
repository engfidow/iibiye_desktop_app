import warnings
from .base import LottieObject, LottieProp, PseudoBool, LottieEnum, LottieValueConverter
from .effects import Effect
from .helpers import Transform, Mask, VisualObject, BlendMode
from .shapes import ShapeElement
from .text import TextAnimatorData
from .properties import Value, MultiDimensional
from ..utils.color import Color, color_from_hex, color_to_hex
from .styles import LayerStyle


## @ingroup Lottie
## @todo SVG masks
class MatteMode(LottieEnum):
    Normal = 0
    Alpha = 1
    InvertedAlpha = 2
    Luma = 3
    InvertedLuma = 4


#ingroup Lottie
class Layer(VisualObject):
    """!
    Base class for all layers
    """
    _props = [
        LottieProp("threedimensional", "ddd", PseudoBool, False),
        LottieProp("hidden", "hd", bool, False),
        LottieProp("type", "ty", int, False),
        LottieProp("index", "ind", int, False),
        LottieProp("parent_index", "parent", int, False),
        LottieProp("time_stretch", "sr", float, False),
        LottieProp("in_point", "ip", float, False),
        LottieProp("out_point", "op", float, False),
        LottieProp("start_time", "st", float, False),
    ]
    ## %Layer type.
    ## @see https://github.com/bodymovin/bodymovin-extension/blob/master/bundle/jsx/enums/layerTypes.jsx
    type = None
    _classses = {}

    def __init__(self):
        super().__init__()

        ## Whether the layer is threedimensional
        self.threedimensional = 0
        ## Whether the layer is hidden
        self.hidden = None
        ## Index that can be used for parenting and referenced in expressions
        self.index = None
        ## Must be the `ind` property of another layer
        self.parent_index = None
        self.time_stretch = 1
        ## Frame when the layer becomes visible
        self.in_point = None
        ## Frame when the layer becomes invisible
        self.out_point = None
        ## Start Time of layer. Sets the start time of the layer.
        self.start_time = 0

    @classmethod
    def _load_get_class(cls, lottiedict):
        if not Layer._classses:
            Layer._classses = {
                sc.type: sc
                for sc in Layer.__subclasses__() + VisualLayer.__subclasses__()
                if sc.type is not None
            }
        type_id = lottiedict["ty"]
        if type_id not in Layer._classses:
            warnings.warn("Unknown layer type: %s" % type_id)
            return Layer
        return Layer._classses[type_id]


## @ingroup Lottie
class VisualLayer(Layer):
    """!
    Base class for layers that have a visual component
    """
    _props = [
        LottieProp("collapse_transform", "cp", bool, False),
        LottieProp("transform", "ks", Transform, False),
        LottieProp("auto_orient", "ao", PseudoBool, False),

        LottieProp("blend_mode", "bm", BlendMode, False),

        LottieProp("matte_mode", "tt", MatteMode, False),
        LottieProp("css_class", "cl", str, False),
        LottieProp("layer_xml_id", "ln", str, False),
        LottieProp("layer_xml_tag_name", "tg", str, False),

        LottieProp("motion_blur", "mb", bool, False),
        LottieProp("layer_style", "sy", LayerStyle, True),

        LottieProp("has_masks", "hasMask", bool, False),
        LottieProp("masks", "masksProperties", Mask, True),
        LottieProp("effects", "ef", Effect, True),
        LottieProp("matte_target", "td", int, False),
    ]

    @property
    def has_masks(self):
        """!
        Whether the layer has some masks applied
        """
        return bool(self.masks) if getattr(self, "masks") is not None else None

    def __init__(self):
        super().__init__()

        self.collapse_transform = None
        ## Transform properties
        self.transform = Transform()
        ## Auto-Orient along path AE property.
        self.auto_orient = False

        ## CSS class used by the SVG renderer
        self.css_class = None
        ## `id` attribute used by the SVG renderer
        self.layer_xml_id = None
        ## tag name used by the SVG renderer
        self.layer_xml_tag_name = None

        ## Whether motion blur is enabled for the layer
        self.motion_blur = None
        ## Styling effects for this layer
        self.layer_style = None

        ## List of Effects
        self.effects = None
        ## Layer Time Stretching
        self.stretch = 1
        ## List of Masks
        self.masks = None
        ## Blend Mode
        self.blend_mode = BlendMode.Normal
        ## Matte mode, the layer will inherit the transparency from the layer above
        self.matte_mode = None
        self.matte_target = None
        ## Composition owning the layer, set by add_layer
        self.composition = None

    def add_child(self, layer):
        if not self.composition or self.index is None:
            raise Exception("Must set composition / index first")
        self._child_inout_auto(layer)
        self.composition.add_layer(layer)
        layer.parent_index = self.index
        return layer

    def _child_inout_auto(self, layer):
        if layer.in_point is None:
            layer.in_point = self.in_point
        if layer.out_point is None:
            layer.out_point = self.out_point

    @property
    def parent(self):
        if self.parent_index is None:
            return None
        return self.composition.layer(self.parent_index)

    @parent.setter
    def parent(self, layer):
        if layer is None:
            self.parent_index = None
        else:
            self.parent_index = layer.index
            layer._child_inout_auto(self)

    @property
    def children(self):
        for layer in self.composition.layers:
            if layer.parent_index == self.index:
                yield layer

    def __repr__(self):
        return "<%s %s %s>" % (type(self).__name__, self.index, self.name)

    def __str__(self):
        return "%s %s" % (
            self.name or super().__str__(),
            self.index if self.index is not None else ""
        )

    def remove(self):
        """!
        @brief Removes this layer from the componsitin
        """
        self.composition.remove_layer(self)


## @ingroup Lottie
class NullLayer(VisualLayer):
    """!
    Layer with no data, useful to group layers together
    """
    ## %Layer type.
    type = 3

    def __init__(self):
        super().__init__()


## @ingroup Lottie
class TextLayer(VisualLayer):
    _props = [
        LottieProp("data", "t", TextAnimatorData, False),
    ]
    ## %Layer type.
    type = 5

    def __init__(self):
        super().__init__()
        ## Text Data
        self.data = TextAnimatorData()


## @ingroup Lottie
class ShapeLayer(VisualLayer):
    """!
    Layer containing ShapeElement objects
    """
    _props = [
        LottieProp("shapes", "shapes", ShapeElement, True),
    ]
    ## %Layer type.
    type = 4

    def __init__(self):
        super().__init__()
        ## Shape list of items
        self.shapes = [] # ShapeElement

    def add_shape(self, shape):
        self.shapes.append(shape)
        return shape

    def insert_shape(self, index, shape):
        self.shapes.insert(index, shape)
        return shape


## @ingroup Lottie
## @todo SIF I/O
class ImageLayer(VisualLayer):
    _props = [
        LottieProp("image_id", "refId", str, False),
    ]
    ## %Layer type.
    type = 2

    def __init__(self, image_id=""):
        super().__init__()
        ## id pointing to the source image defined on 'assets' object
        self.image_id = image_id


## @ingroup Lottie
class PreCompLayer(VisualLayer):
    _props = [
        LottieProp("reference_id", "refId", str, False),
        LottieProp("time_remapping", "tm", Value, False),
        LottieProp("width", "w", int, False),
        LottieProp("height", "h", int, False),
    ]
    ## %Layer type.
    type = 0

    def __init__(self, reference_id=""):
        super().__init__()
        ## id pointing to the source composition defined on 'assets' object
        self.reference_id = reference_id
        ## Comp's Time remapping
        self.time_remapping = None
        ## Width
        self.width = 512
        ## Height
        self.height = 512


ColorString = LottieValueConverter(color_from_hex, color_to_hex, "Color string")


## @ingroup Lottie
class SolidColorLayer(VisualLayer):
    """!
    Layer with a solid color rectangle
    """
    _props = [
        LottieProp("color", "sc", ColorString, False),
        LottieProp("height", "sh", float, False),
        LottieProp("width", "sw", float, False),
    ]
    ## %Layer type.
    type = 1

    def __init__(self, color=Color(), width=512, height=512):
        super().__init__()
        ## Color of the layer as a @c \#rrggbb hex
        self.color = color
        ## Height of the layer.
        self.height = height
        ## Width of the layer.
        self.width = width


#ingroup Lottie
class CameraLayer(Layer):
    """!
    3D Camera
    """
    type = 13
    _props = [
        LottieProp("type", "ty", int, False),
        LottieProp("transform", "ks", Transform, False),
        LottieProp("perspective", "pe", Value, False),
    ]

    def __init__(self):
        super().__init__()

        ## Layer transform
        self.transform = None
        ## Distance from the Z=0 plane.
        ## Small values yield a higher perspective effect.
        self.perspective = None


#ingroup Lottie
class DataLayer(Layer):
    _props = [
        LottieProp("type", "ty", int, False),
        LottieProp("data_source_id", "refId", str, False),
    ]
    type = 15

    def __init__(self):
        super().__init__()

        ## ID of the data source in assets
        self.data_source_id = None


#ingroup Lottie
class AudioSettings(LottieObject):
    _props = [
        LottieProp("level", "lv", MultiDimensional, False),
    ]

    def __init__(self):
        super().__init__()

        self.level = MultiDimensional([0, 0])


#ingroup Lottie
class AudioLayer(Layer):
    """!
    A layer playing sounds
    """
    _props = [
        LottieProp("type", "ty", int, False),
        LottieProp("audio_settings", "au", AudioSettings, False),
        LottieProp("sound_id", "refId", str, False),
    ]
    type = 6

    def __init__(self):
        super().__init__()

        self.audio_settings = None
        ## ID of the sound as specified in the assets
        self.sound_id = None
