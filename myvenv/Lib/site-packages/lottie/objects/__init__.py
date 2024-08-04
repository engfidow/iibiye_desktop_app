"""!
Package with all the Lottie Python bindings
"""
from . import (
    animation, base, effects, enums, helpers, layers, shapes, assets, easing,
    text, bezier, composition, styles
)
from .animation import Animation
from .layers import *
from .shapes import *
from .styles import *
from .assets import Precomp, Image, Asset, FileAsset
from .bezier import Bezier
from .composition import Composition

__all__ = [
    "animation", "base", "effects", "enums", "helpers", "layers", "shapes", "assets",
    "easing", "text", "bezier", "styles",
    "Animation",
    "NullLayer", "TextLayer", "ShapeLayer", "ImageLayer", "PreCompLayer", "SolidColorLayer",
    "Rect", "Fill", "Trim", "Repeater", "GradientFill", "Stroke", "RoundedCorners", "Path",
    "TransformShape", "Group", "Star", "Ellipse", "Merge", "GradientStroke",
    "Bezier", "Precomp", "Composition", "Image", "Asset", "FileAsset", "LayerStyle"
]
