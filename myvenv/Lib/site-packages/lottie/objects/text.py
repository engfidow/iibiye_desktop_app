from .base import LottieObject, LottieProp, LottieEnum
from .properties import Value, MultiDimensional, ColorValue, Color
from ..nvector import NVector
from .helpers import Transform
from .shapes import ShapeElement


#ingroup Lottie
class MaskedPath(LottieObject):
    """!
    Uses the path described by a layer mask to put the text on said path.
    """
    _props = [
        LottieProp("mask", "m", int, False),
        LottieProp("first_margin", "f", Value, False),
        LottieProp("last_margin", "l", Value, False),
        LottieProp("reverse_path", "r", Value, False),
        LottieProp("force_alignment", "a", Value, False),
        LottieProp("perpendicular_to_path", "p", Value, False),
    ]

    def __init__(self):
        super().__init__()

        ## Index of the mask to use
        self.mask = None
        self.first_margin = None
        self.last_margin = None
        self.reverse_path = None
        self.force_alignment = None
        self.perpendicular_to_path = None


## @ingroup Lottie
## @ingroup LottieCheck
class TextAnimatorDataProperty(Transform):
    _props = [
        LottieProp("rotate_x", "rx", Value),
        LottieProp("rotate_y", "ry", Value),

        LottieProp("stroke_width", "sw", Value),
        LottieProp("stroke_color", "sc", ColorValue),
        LottieProp("stroke_hue", "sh", Value, False),
        LottieProp("stroke_saturation", "ss", Value, False),
        LottieProp("stroke_brightness", "sb", Value, False),
        LottieProp("stroke_opacity", "so", Value, False),

        LottieProp("fill_color", "fc", ColorValue),
        LottieProp("fill_hue", "fh", Value),
        LottieProp("fill_saturation", "fs", Value),
        LottieProp("fill_brightness", "fb", Value),
        LottieProp("fill_opacity", "fo", Value, False),

        LottieProp("tracking", "t", Value),
        LottieProp("scale", "s", MultiDimensional),
        LottieProp("blur", "bl", Value, False),
        LottieProp("line_spacing", "ls", Value, False),

    ]

    def __init__(self):
        super().__init__()
        ## Angle?
        self.rx = Value()
        ## Angle?
        self.ry = Value()

        ## Stroke width
        self.stroke_width = Value()
        ## Stroke color
        self.stroke_color = ColorValue()
        self.stroke_hue = None
        self.stroke_saturation = None
        self.stroke_brightness = None
        self.stroke_opacity = None

        ## Fill color
        self.fill_color = ColorValue()
        ## Hue
        self.fill_hue = Value()
        ## Saturation 0-100
        self.fill_saturation = Value()
        ## Brightness 0-100
        self.fill_brightness = Value()
        self.fill_opacity = None

        ## Tracking
        self.tracking = Value()
        self.blur = None
        self.line_spacing = None


## @ingroup Lottie
class TextGrouping(LottieEnum):
    Characters = 1
    Word = 2
    Line = 3
    All = 4

    @classmethod
    def default(cls):
        return cls.Characters


## @ingroup Lottie
## @ingroup LottieCheck
class TextMoreOptions(LottieObject):
    _props = [
        LottieProp("alignment", "a", MultiDimensional),
        LottieProp("grouping", "g", TextGrouping),
    ]

    def __init__(self):
        self.alignment = MultiDimensional(NVector(0, 0))
        self.grouping = TextGrouping.default()


## @ingroup Lottie
class TextJustify(LottieEnum):
    Left = 0
    Right = 1
    Center = 2
    JustifyWithLastLineLeft = 3
    JustifyWithLastLineRight = 4
    JustifyWithLastLineCenter = 5
    JustifyWithLastLineFull = 6


#ingroup Lottie
class TextCaps(LottieEnum):
    Regular = 0
    AllCaps = 1
    SmallCaps = 2


## @ingroup Lottie
class TextDocument(LottieObject):
    """!
    @see http://docs.aenhancers.com/other/textdocument/

    Note that for multi-line text, lines are separated by \\r
    """
    _props = [
        LottieProp("font_family", "f", str),
        LottieProp("fill_color", "fc", Color),

        LottieProp("stroke_color", "sc", Color, False),
        LottieProp("stroke_width", "sw", float, False),
        LottieProp("stroke_over_fill", "of", bool, False),

        LottieProp("font_size", "s", float),
        LottieProp("line_height", "lh", float),
        LottieProp("wrap_size", "sz", NVector),
        LottieProp("wrap_position", "ps", NVector, False),

        LottieProp("text", "t", str),
        LottieProp("justify", "j", TextJustify),
        LottieProp("text_caps", "ca", TextCaps, False),
        LottieProp("tracking", "tr", float, False),
        LottieProp("baseline_shift", "ls", float, False),
    ]

    def __init__(self, text="", font_size=10, color=None, font_family=""):
        self.font_family = font_family

        ## Text color
        self.fill_color = color or Color(0, 0, 0)

        self.stroke_color = None
        self.stroke_width = 0
        ## Render stroke above the fill
        self.stroke_over_fill = None

        ## Line height when wrapping
        self.line_height = None
        ## Text alignment
        self.justify = TextJustify.Left
        ## Size of the box containing the text
        self.wrap_size = None
        ## Position of the box containing the text
        self.wrap_position = None
        ## Text
        self.text = text
        ## Font Size
        self.font_size = font_size
        ## Text caps
        self.text_caps = None
        ## Text Tracking
        self.tracking = None
        self.baseline_shift = None


## @ingroup Lottie
class TextDataKeyframe(LottieObject):
    _props = [
        LottieProp("start", "s", TextDocument),
        LottieProp("time", "t", float),
    ]

    def __init__(self, time=0, start=None):
        ## Start value of keyframe segment.
        self.start = start
        ## Start time of keyframe segment.
        self.time = time


## @ingroup Lottie
class TextData(LottieObject):
    _props = [
        LottieProp("keyframes", "k", TextDataKeyframe, True),
    ]

    def __init__(self):
        self.keyframes = []

    def get_value(self, time):
        for kf in self.keyframes:
            if kf.time >= time:
                return kf.start
        return None


## @ingroup Lottie
class TextAnimatorData(LottieObject):
    _props = [
        LottieProp("properties", "a", TextAnimatorDataProperty, True),
        LottieProp("data", "d", TextData, False),
        LottieProp("more_options", "m", TextMoreOptions, False),
        LottieProp("masked_path", "p", MaskedPath),
    ]

    def __init__(self):
        self.properties = []
        self.data = TextData()
        self.more_options = TextMoreOptions()
        self.masked_path = MaskedPath()

    def add_keyframe(self, time, item):
        self.data.keyframes.append(TextDataKeyframe(time, item))

    def get_value(self, time):
        return self.data.get_value(time)


## @ingroup Lottie
class FontPathOrigin(LottieEnum):
    Local = 0
    CssUrl = 1
    ScriptUrl = 2
    FontUrl = 3


## @ingroup Lottie
class Font(LottieObject):
    _props = [
        LottieProp("ascent", "ascent", float),
        LottieProp("font_family", "fFamily", str),
        LottieProp("name", "fName", str),
        LottieProp("font_style", "fStyle", str),
        LottieProp("path", "fPath", str),
        LottieProp("weight", "fWeight", str),
        LottieProp("origin", "origin", FontPathOrigin),
        LottieProp("css_class", "fClass", str),
    ]

    def __init__(self, font_family="sans", font_style="Regular", name=None):
        self.ascent = None
        self.font_family = font_family
        self.font_style = font_style
        self.name = name or "%s-%s" % (font_family, font_style)
        self.path = None
        self.weight = None
        self.origin = None
        self.css_class = None


## @ingroup Lottie
class FontList(LottieObject):
    _props = [
        LottieProp("list", "list", Font, True),
    ]

    def __init__(self):
        self.list = []

    def append(self, font):
        self.list.append(font)


## @ingroup Lottie
class CharacterData(LottieObject):
    """!
    Character shapes
    """
    _props = [
        LottieProp("shapes", "shapes", ShapeElement, True),
    ]

    def __init__(self):
        self.shapes = []


## @ingroup Lottie
class Chars(LottieObject):
    """!
    Defines character shapes to avoid loading system fonts
    """
    _props = [
        LottieProp("character", "ch", str, False),
        LottieProp("font_family", "fFamily", str, False),
        LottieProp("font_size", "size", float, False),
        LottieProp("font_style", "style", str, False),
        LottieProp("width", "w", float, False),
        LottieProp("data", "data", CharacterData, False),
    ]

    def __init__(self):
        ## Character Value
        self.character = ""
        ## Character Font Family
        self.font_family = ""
        ## Character Font Size
        self.font_size = 0
        ## Character Font Style
        self.font_style = "" # Regular
        ## Character Width
        self.width = 0
        ## Character Data
        self.data = CharacterData()

    @property
    def shapes(self):
        return self.data.shapes
