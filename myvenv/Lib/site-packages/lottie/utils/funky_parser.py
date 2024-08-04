import re
import sys
import enum
import math
import typing

from ..parsers.svg.svgdata import color_table
from ..parsers.svg.importer import parse_color, parse_svg_file
from ..objects.animation import Animation
from ..objects import layers
from ..objects import shapes
from ..nvector import NVector
from .font import FontStyle


color_words = {
    "alice": {"blue": {"_": 1}},
    "antique": {"white": {"_": 1}},
    "aqua": {
        "_": 1,
        "marine": {"_": 1}
    },
    "azure": {"_": 1},
    "beige": {"_": 1},
    "bisque": {"_": 1},
    "black": {"_": 1},
    "blanched": {"almond": {"_": 1}},
    "blue": {
        "_": 1,
        "navy": "navy",
        "violet": {"_": 1},
    },
    "brown": {"_": 1},
    "burly": {"wood": {"_": 1}},
    "cadet": {"blue": {"_": 1}},
    "chartreuse": {"_": 1},
    "chocolate": {"_": 1},
    "coral": {"_": 1},
    "cornflower": {"blue": {"_": 1}},
    "corn": {
        "silk": {"_": 1},
        "flower": {"blue": {"_": 1}},
    },
    "crimson": {"_": 1},
    "cyan": {"_": 1},
    "dark": {
        "blue": {"_": 1},
        "cyan": {"_": 1},
        "golden": {"rod": {"_": 1}},
        "gray": {"_": 1},
        "green": {"_": 1},
        "grey": {"_": 1},
        "khaki": {"_": 1},
        "magenta": {"_": 1},
        "olive": {"green": {"_": 1}},
        "orange": {"_": 1},
        "orchid": {"_": 1},
        "red": {"_": 1},
        "salmon": {"_": 1},
        "sea": {"green": {"_": 1}},
        "slate": {
            "blue": {"_": 1},
            "gray": {"_": 1},
            "grey": {"_": 1}
        },
        "turquoise": {"_": 1},
        "violet": {"_": 1}
    },
    "deep": {
        "pink": {"_": 1},
        "sky": {"blue": {"_": 1}},
    },
    "dim": {
        "gray": {"_": 1},
        "grey": {"_": 1}
    },
    "dodger": {"blue": {"_": 1}},
    "fire": {"brick": {"_": 1}},
    "floral": {"white": {"_": 1}},
    "forest": {"green": {"_": 1}},
    "fuchsia": {"_": 1},
    "gainsboro": {"_": 1},
    "ghost": {"white": {"_": 1}},
    "gold": {"_": 1},
    "golden": {"rod": {"_": 1}},
    "gray": {"_": 1},
    "green": {
        "_": 1,
        "yellow": {"_": 1}
    },
    "grey": {"_": 1},
    "honeydew": {"_": 1},
    "hotpink": {"_": 1},
    "indian": {"red": {"_": 1}},
    "indigo": {"_": 1},
    "ivory": {"_": 1},
    "khaki": {"_": 1},
    "lavender": {
        "_": 1,
        "blush": {"_": 1},
    },
    "lawn": {"green": {"_": 1}},
    "lemon": {"chiffon": {"_": 1}},
    "light": {
        "blue": {"_": 1},
        "coral": {"_": 1},
        "cyan": {"_": 1},
        "golden": {
            "rod": {
                "_": 1,
                "yellow": {"_": 1},
            }
        },
        "gray": {"_": 1},
        "green": {"_": 1},
        "grey": {"_": 1},
        "pink": {"_": 1},
        "salmon": {"_": 1},
        "sea": {"green": {"_": 1}},
        "sky": {"blue": {"_": 1}},
        "slate": {
            "gray": {"_": 1},
            "grey": {"_": 1}
        },
        "steel": {"blue": {"_": 1}},
        "yellow": {"_": 1},
    },
    "lime": {
        "_": 1,
        "green": {"_": 1},
    },
    "linen": {"_": 1},
    "magenta": {"_": 1},
    "maroon": {"_": 1},
    "medium": {
        "aquamarine": {"_": 1},
        "blue": {"_": 1},
        "orchid": {"_": 1},
        "purple": {"_": 1},
        "sea": {"green": {"_": 1}},
        "slate": {"blue": {"_": 1}},
        "spring": {"green": {"_": 1}},
        "turquoise": {"_": 1},
        "violet": {"red": {"_": 1}},
    },
    "midnight": {"blue": {"_": 1}},
    "mint": {"cream": {"_": 1}},
    "misty": {"rose": {"_": 1}},
    "moccasin": {"_": 1},
    "navajo": {"white": {"_": 1}},
    "navy": {
        "_": 1,
        "blue": "navy",
    },
    "old": {"lace": {"_": 1}},
    "olive": {
        "_": 1,
        "drab": {"_": 1},
    },
    "orange": {
        "_": 1,
        "red": {"_": 1},
    },
    "orchid": {"_": 1},
    "pale": {
        "golden": {"rod": {"_": 1}},
        "green": {"_": 1},
        "turquoise": {"_": 1},
        "violet": {"red": {"_": 1}},
    },
    "papaya": {"whip": {"_": 1}},
    "peach": {"puff": {"_": 1}},
    "peru": {"_": 1},
    "pink": {"_": 1},
    "plum": {"_": 1},
    "powder": {"blue": {"_": 1}},
    "purple": {"_": 1},
    "red": {"_": 1},
    "rosy": {"brown": {"_": 1}},
    "royal": {"blue": {"_": 1}},
    "saddle": {"brown": {"_": 1}},
    "salmon": {"_": 1},
    "sandy": {"brown": {"_": 1}},
    "sea": {
        "green": {"_": 1},
        "shell": {"_": 1},
    },
    "seashell": {"_": 1},
    "sienna": {"_": 1},
    "silver": {"_": 1},
    "sky": {"blue": {"_": 1}},
    "slate": {
        "blue": {"_": 1},
        "gray": {"_": 1},
        "grey": {"_": 1},
    },
    "snow": {"_": 1},
    "spring": {"green": {"_": 1}},
    "steel": {"blue": {"_": 1}},
    "tan": {"_": 1},
    "teal": {"_": 1},
    "thistle": {"_": 1},
    "tomato": {"_": 1},
    "turquoise": {"_": 1},
    "violet": {"_": 1},
    "wheat": {"_": 1},
    "white": {
        "_": 1,
        "smoke": {"_": 1},
    },
    "yellow": {
        "_": 1,
        "green": {"_": 1},
    },
}


class TokenType(enum.Enum):
    Word = enum.auto()
    Number = enum.auto()
    Eof = enum.auto()
    String = enum.auto()
    Punctuation = enum.auto()
    Color = enum.auto()


class Token:
    def __init__(
        self,
        type: TokenType,
        line: int,
        col: int,
        start: int,
        end: int,
        value: typing.Any = None
    ):
        self.col = col
        self.line = line
        self.end = end
        self.start = start
        self.type = type
        self.value = value

    def __repr__(self):
        if self.type == TokenType.Eof:
            return "End of file"
        return repr(self.value)


class AnimatableType:
    Position = enum.auto()
    Color = enum.auto()
    Angle = enum.auto()
    Size = enum.auto()
    Number = enum.auto()
    Integer = enum.auto()


class AnimatableProperty:
    def __init__(self, name, phrase, props, type: AnimatableType):
        self.name = name.split()
        self.phrase = phrase
        self.props = props
        self.type = type

    def set_initial(self, value):
        for prop in self.props:
            prop.value = value

    def get_initial(self):
        return self.props[0].get_value(0)

    def add_keyframe(self, time, value):
        for prop in self.props:
            if not prop.animated and time > 0:
                prop.add_keyframe(0, prop.value)
            prop.add_keyframe(time, value)

    def loop(self, time):
        for prop in self.props:
            if prop.animated:
                prop.add_keyframe(time, prop.get_value(0))

    def get_value(self, time):
        return self.props[0].get_value(time)


class ShapeData:
    def __init__(self, extent):
        self.color = [0, 0, 0]
        self.color_explicit = False
        self.extent = extent
        self.size_multiplitier = 1
        self.portrait = False
        self.roundness = 0
        self.opacity = 1
        self.count = 1
        self.stroke = None
        self.stroke_on_top = True
        self.properties = {}

    def scale(self, multiplier):
        self.size_multiplitier *= multiplier
        self.extent *= multiplier

    def define_property(self, name, type, props, phrase=None):
        self.properties[name] = AnimatableProperty(name, phrase, props, type)

    def add_property(self, name, prop):
        self.properties[name].props.append(prop)


class Lexer:
    expression = re.compile(
        r'[\r\t ]*(?P<token>(?P<punc>[:,;.])|(?P<word>[a-zA-Z\']+)|(?P<color>#(?:[a-fA-F0-9]{3}){1,2})|' +
        r'(?P<number>-?[0-9]+(?P<fraction>\.[0-9]+)?)|(?P<string>"(?:[^"\\]|\\["\\nbt])+"))[\r\t ]*'
    )

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.token = None
        self.line = 1
        self.line_pos = 0
        self.tokens = []
        self.token_index = 0

    def _new_token(self, token: Token):
        self.token = token
        self.tokens.append(token)
        self.token_index = len(self.tokens)
        return token

    def next(self):
        if self.token_index < len(self.tokens):
            self.token = self.tokens[self.token_index]
            self.token_index += 1
            return self.token

        while True:
            if self.pos >= len(self.text):
                return self._new_token(Token(TokenType.Eof, self.line, self.pos - self.line_pos, self.pos, self.pos))

            if self.text[self.pos] == '\n':
                self.line += 1
                self.pos += 1
                self.line_pos = self.pos
            else:
                match = self.expression.match(self.text, self.pos)
                if match:
                    break

                self.pos += 1

        if match.group("word"):
            type = TokenType.Word
            value = match.group("word").lower()
        elif match.group("number"):
            type = TokenType.Number
            if match.group("fraction"):
                value = float(match.group("number"))
            else:
                value = int(match.group("number"))
        elif match.group("string"):
            type = TokenType.String
            value = match.group("string")[1:-1]
        elif match.group("punc"):
            value = match.group("punc")
            type = TokenType.Punctuation
        elif match.group("color"):
            value = match.group("color")
            type = TokenType.Color

        self.pos = match.end("token")
        return self._new_token(Token(type, self.line, self.pos - self.line_pos, match.start("token"), self.pos, value))

    def back(self):
        if self.token_index > 0:
            self.restore(self.token_index - 1)

    def save(self):
        return self.token_index

    def restore(self, index):
        self.token_index = index
        if index > 0:
            self.token = self.tokens[self.token_index-1]
        else:
            self.token = self.tokens[0]


class Logger:
    def warn(self, message):
        sys.stderr.write(message)
        sys.stderr.write("\n")


class DummyLogger(Logger):
    def warn(self, message):
        pass


class StorageLogger(Logger):
    def __init__(self):
        self.messages = []

    def warn(self, message):
        self.messages.append(message)


class Parser:
    sides = {
        "penta": 5,
        "hexa": 6,
        "hepta": 7,
        "octa": 8,
        "ennea": 9,
        "deca": 10,
    }

    def __init__(self, text, logger: Logger):
        self.lexer = Lexer(text)
        self.lexer.next()
        self.logger = logger
        self.allow_resize = True
        self.max_duration = None
        self.svg_shapes = []
        self.font = FontStyle("Ubuntu", 80)

    def next(self):
        return self.lexer.next()

    @property
    def token(self):
        return self.lexer.token

    def color(self):
        return self.get_color(color_words, "")

    def get_color_value(self, value, complete_word: str):
        if isinstance(value, str):
            return NVector(*color_table[value])
        elif isinstance(value, (list, tuple)):
            return NVector(*value)
        elif isinstance(value, NVector):
            return value
        else:
            return NVector(*color_table[complete_word])

    def complete_color(self, word_dict: dict, complete_word: str):
        if "_" in word_dict:
            return self.get_color_value(complete_word)
        else:
            next_item = next(iter(word_dict.item()))
            return self.complete_color(next_item[1], complete_word + next_item[0])

    def get_color(self, word_dict: dict, complete_word: str):
        if self.token.type == TokenType.Color:
            color = parse_color(self.token.value)
            self.next()
            return color

        if self.token.type != TokenType.Word:
            return None

        value = word_dict.get(self.token.value, None)
        if not value:
            return None

        if isinstance(value, dict):
            next_word = complete_word + self.token.value
            self.next()
            color = self.get_color(value, next_word)
            if color is not None:
                return color

            if "_" in value:
                return self.get_color_value(value["_"], next_word)

            self.warn("Incomplete color name")
        else:
            return self.get_color_value(value, complete_word)

    def warn(self, message):
        token = self.token
        self.logger.warn("At line %s column %s, near %r: %s" % (token.line, token.col, token, message))

    def parse(self):
        self.lottie = Animation(180, 60)
        if self.article():
            if self.check_words("animation", "composition"):
                self.next()
                self.animation()
            else:
                self.lexer.back()
        self.layers(self.lottie)
        if self.token.type != TokenType.Eof:
            self.warn("Extra tokens")
        return self.lottie

    def article(self):
        if self.check_words("a", "an", "the"):
            self.next()
            return True
        return False

    def check_words(self, *words):
        if self.token.type != TokenType.Word:
            return False

        return self.token.value in words

    def skip_words(self, *words):
        if self.check_words(*words):
            self.next()
            return True
        return False

    def require_one_of(self, *words):
        if self.check_words(*words):
            return True

        self.warn("Expected " + repr(words[0]))
        return False

    def check_word_sequence(self, words):
        token = self.token
        index = self.lexer.save()
        for word in words:
            if token.type != TokenType.Word or token.value != word:
                break
            token = self.next()
        else:
            return True

        self.lexer.restore(index)
        return False

    def possesive(self):
        return self.skip_words("its", "his", "her", "their")

    def properties(self, shape_data, callback, callback_args=[], words=["with"]):
        lexind_and = -1
        while True:
            must_have_property = self.skip_words(*words)

            self.article() or self.possesive()

            lexind = self.lexer.save()

            if not callback(*callback_args):
                self.lexer.restore(lexind)

                if shape_data and not self.shape_common_property(shape_data):
                    if must_have_property:
                        self.warn("Unknown property")
                        break
                if lexind_and != -1:
                    self.lexer.restore(lexind_and)
                break

            lexind_and = self.lexer.save()
            if not self.skip_and():
                break

    def simple_properties_callback(self, object, properties):
        if self.check_words(*properties.keys()):
            prop = self.token.value
            self.next()
            if self.check_words("of"):
                self.next()

            value = properties[prop](getattr(object, prop))
            setattr(object, prop, value)
            return True
        return False

    def animation(self):
        while True:
            if self.check_words("lasts", "lasting"):
                self.next()
                if self.check_words("for"):
                    self.next()
                self.lottie.out_point = self.time(self.lottie.out_point)
            elif self.check_words("stops", "stopping", "loops", "looping"):
                if self.check_words("for", "after"):
                    self.next()
                self.lottie.out_point = self.time(self.lottie.out_point)
                if self.max_duration and self.lottie.out_point > self.max_duration:
                    self.lottie.out_point = self.max_duration
            elif self.check_words("with", "has"):
                props = {
                    "width": self.integer,
                    "height": self.integer,
                    "name": self.string
                }
                if not self.allow_resize:
                    props.pop("width")
                    props.pop("height")
                self.properties(None, self.simple_properties_callback, [self.lottie, props], ["with", "has"])
            elif self.skip_and():
                pass
            else:
                return

    def time(self, default):
        if self.token.type != TokenType.Number:
            self.warn("Expected time")
            return default

        amount = self.token.value

        self.next()
        if self.check_words("seconds", "second"):
            amount *= self.lottie.frame_rate
        elif self.check_words("milliseconds", "millisecond"):
            amount *= self.lottie.frame_rate / 1000
        elif not self.check_words("frames", "frame"):
            self.warn("Missing time unit")
            return amount

        self.next()
        return amount

    def integer(self, default, warn=True):
        if self.token.type != TokenType.Number or not isinstance(self.token.value, int):
            if warn:
                self.warn("Expected integer")
            return default

        val = self.token.value
        self.next()
        return val

    def number(self, default):
        if self.token.type != TokenType.Number:
            self.warn("Expected number")
            return default

        val = self.token.value
        self.next()

        return val

    def string(self, default):
        if self.token.type != TokenType.String:
            self.warn("Expected string")
            return default

        val = self.token.value
        self.next()
        return val

    def layers(self, composition):
        while True:
            if self.token.type == TokenType.Punctuation and self.token.value in ";.":
                self.next()
            self.skip_and()
            self.skip_words("then") or self.skip_words("finally")

            if self.check_words("there's"):
                self.next()
                self.layer(composition)
            elif self.check_words("there"):
                self.next()
                if self.check_words("is", "are"):
                    self.next()
                    self.layer(composition)
            elif self.article():
                self.lexer.back()
                self.layer(composition)
            elif self.token.type == TokenType.Number and isinstance(self.token.value, int):
                self.layer(composition)
            else:
                break

    def count(self, default=1):
        if self.article():
            return 1
        return self.integer(default)

    def layer(self, composition):
        if self.token.type != TokenType.Word:
            self.warn("Expected shape")
            return

        layer = layers.ShapeLayer()
        layer.in_point = self.lottie.in_point
        layer.out_point = self.lottie.out_point
        composition.insert_layer(0, layer)

        self.shape_list(layer)

        if self.token.type == TokenType.Punctuation and self.token.value in ",;.":
            self.next()

    def skip_and(self):
        if self.token.type == TokenType.Punctuation and self.token.value == ",":
            self.next()
            self.skip_words("and")
            return True
        return self.skip_words("and")

    def shape_list(self, parent):
        extent = min(self.lottie.width, self.lottie.height) * 0.4
        shape = ShapeData(extent)
        shape.count = self.count()

        while True:
            ok = False

            color = self.color()
            if color:
                ok = True
                shape.color = color
                shape.color_explicit = True

            if self.check_words("transparent", "invisible"):
                self.next()
                shape.color = None
                ok = True

            size_mult = self.size_multiplitier()
            if size_mult:
                ok = True
                shape.scale(size_mult)

            if self.check_words("portrait"):
                self.next()
                shape.portrait = True
                ok = True

            if self.check_words("landscape"):
                self.next()
                shape.portrait = False
                ok = True

            lexind = self.lexer.save()
            qualifier = self.size_qualifier()
            if self.check_words("rounded"):
                shape.roundness = qualifier
                self.next()
                ok = True
            elif self.check_words("transparent"):
                shape.opacity = (1 / qualifier)
                self.next()
                ok = True
            elif lexind < self.lexer.token_index:
                self.lexer.restore(lexind)

            if self.check_words("star", "polygon", "ellipse", "rectangle", "circle", "square", "text"):
                shape_type = self.token.value
                function = getattr(self, "shape_" + shape_type)
                self.next()
                shape_object = function(shape)
                self.add_shape(parent, shape_object, shape)
                return

            if self.token.type == TokenType.Word:
                for name, sides in self.sides.items():
                    if self.token.value.startswith(name):
                        if self.token.value.endswith("gon"):
                            self.next()
                            shape_object = self.shape_polygon(shape, sides)
                            self.add_shape(parent, shape_object, shape)
                            return
                        elif self.token.value.endswith("gram"):
                            self.next()
                            shape_object = self.shape_star(shape, sides)
                            self.add_shape(parent, shape_object, shape)
                            return

            if self.check_words("triangle"):
                self.next()
                shape_object = self.shape_polygon(shape, 3)
                self.add_shape(parent, shape_object, shape)
                return

            sides = self.integer(None, False)
            if sides is not None:
                if self.check_words("sided", "pointed"):
                    self.next()
                    if self.check_words("polygon", "star"):
                        shape_type = self.token.value
                        function = getattr(self, "shape_" + shape_type)
                        self.next()
                        shape_object = function(shape, sides)
                        self.add_shape(parent, shape_object, shape)
                        return
                    else:
                        self.warn("Expected 'star' or 'polygon'")
                        return
                else:
                    continue

            for svg_shape in self.svg_shapes:
                if svg_shape.match(parent, self, shape):
                    return

            if not ok:
                self.next()
                break

        self.warn("Expected shape")

    def size_qualifier(self):
        base = 1

        while True:
            if self.check_words("very", "much"):
                self.next()
                base *= 1.33
            elif self.check_words("extremely"):
                self.next()
                base *= 1.5
            elif self.check_words("incredibly"):
                self.next()
                base *= 2
            else:
                break

        return base

    def size_multiplitier(self):
        lexind = self.lexer.save()
        base = self.size_qualifier()

        if self.check_words("small"):
            self.next()
            return 0.8 / base
        elif self.check_words("large", "big"):
            self.next()
            return 1.2 * base
        elif self.check_words("tiny"):
            self.next()
            return 0.5 / base
        elif self.check_words("huge"):
            self.next()
            return 1.6 * base
        else:
            self.lexer.restore(lexind)
            return None

    def add_shape(self, parent, shape_object, shape_data):
        g = shapes.Group()
        g.add_shape(shape_object)

        if shape_data.stroke and shape_data.stroke_on_top:
            g.add_shape(shape_data.stroke)

        if shape_data.color:
            fill = shapes.Fill(shape_data.color)
            g.add_shape(fill)
            shape_data.define_property("color", AnimatableType.Color, [fill.color])

        if shape_data.stroke and not shape_data.stroke_on_top:
            g.add_shape(shape_data.stroke)

        if shape_data.opacity != 1:
            g.transform.opacity.value = 100 * shape_data.opacity

        if "position" in shape_data.properties:
            center = shape_data.properties["position"].get_initial()
        else:
            center = g.bounding_box(0).center()
        g.transform.position.value = self.position(g, 0) + center
        g.transform.anchor_point.value = NVector(*center)
        shape_data.define_property("position", AnimatableType.Position, [g.transform.position], ["moves"])
        shape_data.define_property("rotation", AnimatableType.Angle, [g.transform.rotation], ["rotates"])

        if self.check_words("rotated"):
            self.next()
            g.transform.rotation.value = self.angle(0)

        parent.insert_shape(0, g)

        if self.skip_words("that"):
            self.animated_properties(shape_data)

        return g

    def position(self, shape: shapes.Group, time: float):
        px = 0
        py = 0

        qual = self.size_qualifier()

        if self.check_words("to", "in", "towards", "on", "at"):
            self.next()
            if self.check_words("the"):
                self.next()
            if self.token.type != TokenType.Word:
                self.warn("Expected position")
                return

            while True:
                if self.check_words("left"):
                    px = -1
                elif self.check_words("right"):
                    px = 1
                elif self.check_words("top"):
                    py = -1
                elif self.check_words("bottom"):
                    py = 1
                elif self.check_words("center", "middle"):
                    pass
                else:
                    break

                self.next()

            if self.check_words("side", "corner"):
                self.next()

        if px == 0 and py == 0:
            return shape.transform.position.get_value(time)

        box = shape.bounding_box(time)
        center = box.center()
        left = box.width / 2
        right = self.lottie.width - box.width / 2
        top = box.height / 2
        bottom = self.lottie.height - box.height / 2

        pos = shape.transform.position.get_value(time)
        x = pos.x
        y = pos.y
        dx = dy = 0

        if px < 0:
            dx = left - center.x
        elif px > 0:
            dx = right - center.y

        if py < 0:
            dy = top - center.y
        elif py > 0:
            dy = bottom - center.y

        return NVector(
            x + dx * qual,
            y + dy * qual,
        )

    def animation_time(self, time, required):
        if self.skip_words("at"):
            if self.skip_words("the"):
                self.require_one_of("end")
                self.next()
                return self.lottie.out_point
            return self.time(time)
        if self.skip_words("after"):
            return self.time(0) + time
        if required:
            return time
        return None

    def animated_properties(self, shape_data: ShapeData):
        time = 0

        while True:
            prop_time = self.animation_time(time, False)
            changing = self.skip_words("changing", "changes")
            possesive = self.possesive()
            found_property = None
            value = None
            loop = False

            if possesive or changing:
                for property in shape_data.properties.values():
                    if self.check_word_sequence(property.name):
                        found_property = property
                        if possesive and not changing:
                            if self.skip_words("loops"):
                                self.skip_words("back")
                                loop = True
                                break
                            else:
                                self.skip_words("changes")
                        value = self.animated_property(shape_data, property, time)
                        break
            else:
                for property in shape_data.properties.values():
                    if property.phrase and self.check_word_sequence(property.phrase):
                        found_property = property
                        value = self.animated_property(shape_data, property, time)
                        break

            if not found_property:
                self.warn("Unknown property")
                break

            if prop_time is None:
                self.prop_time = self.animation_time(time, True)
            time = prop_time

            if loop:
                found_property.loop(time)
            else:
                if value is None:
                    break

                found_property.add_keyframe(time, value)

            cont = self.skip_and()
            cont = self.skip_words("then") or cont
            if not cont:
                break

    def animated_property_value(self, property: AnimatableProperty, time):
        if property.type == AnimatableType.Angle:
            return self.angle(None)
        elif property.type == AnimatableType.Number:
            return self.number(None)
        elif property.type == AnimatableType.Integer:
            return self.integer(None)
        elif property.type == AnimatableType.Color:
            value = self.color()
            if not value:
                self.warn("Expected color")
            return value
        elif property.type == AnimatableType.Position:
            return self.position_value(property.get_value(time))
        elif property.type == AnimatableType.Size:
            return self.vector_value()
        return None

    def animated_property(self, shape_data: ShapeData, property: AnimatableProperty, time):
        relative = False
        if not self.skip_words("to"):
            relative = self.skip_words("by")

        value = self.animated_property_value(property, time)

        if value is not None and relative:
            value += property.get_value(time)

        return value

    def vector_value(self):
        x = self.number(0)
        if self.token.type == TokenType.Punctuation and self.token.value == ",":
            self.next()
        y = self.number(0)

        return NVector(x, y)

    def position_value(self, start: NVector):

        if self.token.type == TokenType.Word:
            direction = None

            if self.check_words("left") or self.check_word_sequence("the", "left"):
                direction = NVector(-1, 0)
            elif self.check_words("right") or self.check_word_sequence("the", "right"):
                direction = NVector(1, 0)
            elif self.check_words("up", "upwards", "upward"):
                direction = NVector(0, -1)
            elif self.check_words("down", "downwards", "downward"):
                direction = NVector(0, 1)

            if direction is None:
                self.warn("Expected direction or position")
                return start

            self.skip_words("by")

            return start + direction * self.number()

        return self.vector_value()

    def shape_common_property(self, shape_data: ShapeData):
        color = NVector(0, 0, 0)
        width = 4

        while True:
            got_color = self.color()
            if got_color:
                color = got_color
                continue

            quant = self.size_qualifier()
            if self.check_words("thick"):
                self.next()
                width *= 1.5 * quant
                continue
            elif self.check_words("thin"):
                self.next()
                width *= 0.6 / quant
                continue
            else:
                break

        if self.check_words("stroke", "border", "outline", "edge", "borders", "edges"):
            self.next()
            shape_data.stroke = shapes.Stroke(color, width)
            return True

        return False

    def animated_properties_callback(self, shape_data: ShapeData):
        for property in shape_data.properties.values():
            if self.check_word_sequence(property.name):
                self.skip_words("to", "is", "are")
                property.set_initial(self.animated_property_value(property, 0))
                return True
        return False

    def shape_square(self, shape_data: ShapeData):
        pos = NVector(self.lottie.width / 2, self.lottie.height / 2)
        size = NVector(shape_data.extent, shape_data.extent)
        round_base = shape_data.extent / 5
        shape = shapes.Rect(pos, size, shape_data.roundness * round_base)
        shape_data.define_property("position", AnimatableType.Position, [shape.position])
        shape_data.define_property("size", AnimatableType.Size, [shape.position])
        self.properties(shape_data, self.animated_properties_callback, [shape_data], ["with", "of"])
        return shape

    def shape_circle(self, shape_data: ShapeData):
        pos = NVector(self.lottie.width / 2, self.lottie.height / 2)
        size = NVector(shape_data.extent, shape_data.extent)
        shape = shapes.Ellipse(pos, size)
        shape_data.define_property("position", AnimatableType.Position, [shape.position])
        shape_data.define_property("size", AnimatableType.Size, [shape.position])
        self.properties(shape_data, self.animated_properties_callback, [shape_data], ["with", "of"])
        return shape

    def shape_star(self, shape_data: ShapeData, sides: int = None):
        pos = NVector(self.lottie.width / 2, self.lottie.height / 2)
        round_base = shape_data.extent / 5
        roundness = shape_data.roundness * round_base
        shape = shapes.Star()
        shape.position.value = pos
        shape.inner_roundness.value = roundness
        shape.outer_radius.value = shape_data.extent / 2
        shape.outer_roundness.value = roundness
        shape.star_type = shapes.StarType.Star
        shape.points.value = sides or 5

        def callback():
            if self.animated_properties_callback(shape_data):
                return True

            if self.check_words("diameter"):
                shape.outer_radius.value = self.number(shape.outer_radius.value) / 2
                return True
            elif self.token.type == TokenType.Number:
                if sides:
                    self.warn("Number of sides already specified")
                shape.points.value = self.integer(shape.points.value)
                if self.require_one_of("points", "sides", "point", "side"):
                    self.next()
                return True
            return False

        shape.inner_radius.value = shape.outer_radius.value / 2

        shape_data.define_property("position", AnimatableType.Position, [shape.position])
        shape_data.define_property("outer radius", AnimatableType.Number, [shape.outer_radius])
        shape_data.define_property("radius", AnimatableType.Number, [shape.outer_radius])
        shape_data.define_property("inner radius", AnimatableType.Number, [shape.inner_radius])
        self.properties(shape_data, callback, [], ["with", "of", "has"])

        return shape

    def shape_polygon(self, shape_data: ShapeData, sides: int = None):
        shape = self.shape_star(shape_data, sides)
        shape.inner_radius = None
        shape.inner_roundness = None
        shape.star_type = shapes.StarType.Polygon
        return shape

    def angle_direction(self):
        if self.check_words("clockwise"):
            self.next()
            return 1
        elif self.check_words("counter"):
            self.next()
            if self.check_words("clockwise"):
                self.next()
            return -1
        return 0

    def fraction(self):
        if self.article():
            amount = 1
        else:
            amount = self.number(1)

        if self.check_words("full", "entire"):
            self.next()
            return amount, True
        elif self.check_words("half", "halfs"):
            self.next()
            return amount / 2, True
        elif self.check_words("third", "thirds"):
            self.next()
            return amount / 3, True
        elif self.check_words("quarter", "quarters"):
            self.next()
            return amount / 3, True

        return amount, False

    def angle(self, default):
        direction = self.angle_direction()

        amount, has_fraction = self.fraction()

        if self.skip_and():
            more_frac = self.fraction()[0]
            if has_fraction:
                amount += amount * more_frac
            else:
                amount += more_frac

        if self.check_words("turns"):
            self.next()
            amount *= 360
        elif self.require_one_of("degrees"):
            self.next()
        elif self.check_word_sequence(["pi", "radians"]):
            amount *= 180
            if direction == 0:
                direction = -1

        if direction == 0:
            direction = 1
        return amount * direction

    def rect_properties(self, shape_data: ShapeData, shape):
        extent = shape_data.extent
        parse_data = {
            "width": None,
            "height": None,
            "ratio": math.sqrt(2),
            "size_specified": False
        }
        handle_orientation = True

        shape_data.define_property("position", AnimatableType.Position, [shape.position])
        shape_data.define_property("size", AnimatableType.Size, [shape.size])

        def callback():
            if self.animated_properties_callback(shape_data):
                return True

            if self.check_words("ratio"):
                self.next()
                ratio = self.fraction()[0]
                if ratio <= 0:
                    self.warn("Ratio must be positive")
                else:
                    parse_data["ratio"] = ratio
                return True
            elif self.check_words("width"):
                self.next()
                parse_data["width"] = self.number(0)
                return True
            elif self.check_words("height"):
                self.next()
                parse_data["height"] = self.number(0)
                return True
            elif self.check_words("size"):
                parse_data["size_specified"] = True

            return False

        self.properties(shape_data, callback, [], ["with", "of", "has"])

        if not parse_data["size_specified"]:
            width = parse_data["width"]
            height = parse_data["height"]
            ratio = parse_data["ratio"]

            if width is None and height is None:
                width = extent
                height = width / ratio
            elif width is None:
                width = height * ratio
            elif height is None:
                height = width / ratio
            else:
                handle_orientation = False

            if handle_orientation:
                if (width > height and shape_data.portrait) or (width < height and not shape_data.portrait):
                    width, height = height, width

            shape.size.value = NVector(width, height)

    def shape_rectangle(self, shape_data: ShapeData):
        pos = NVector(self.lottie.width / 2, self.lottie.height / 2)
        round_base = shape_data.extent / 5

        shape = shapes.Rect(pos, NVector(0, 0), shape_data.roundness * round_base)
        shape_data.define_property("roundness", AnimatableType.Number, [shape.rounded])
        self.rect_properties(shape_data, shape)
        return shape

    def shape_ellipse(self, shape_data: ShapeData):
        pos = NVector(self.lottie.width / 2, self.lottie.height / 2)
        shape = shapes.Ellipse(pos, NVector(0, 0))
        self.rect_properties(shape_data, shape)
        return shape

    def shape_text(self, shape_data: ShapeData):
        text = self.string("")
        font = self.font.clone()
        shape = font.render(text)

        box = shape.bounding_box()

        center = box.center()
        anim_center = NVector(self.lottie.width / 2, self.lottie.height / 2)
        shape.transform.anchor_point.value = anim_center
        shape.transform.position.value.y = self.lottie.height - center.y
        shape.transform.position.value.x = self.lottie.width - center.x

        scale = shape_data.size_multiplitier
        if box.width > self.lottie.width > 0:
            scale *= self.lottie.width / box.width

        if scale != 1:
            wrapper = shapes.Group()
            wrapper.transform.position.value = wrapper.transform.anchor_point.value = anim_center
            wrapper.transform.scale.value *= scale
            wrapper.add_shape(shape)
            return wrapper

        return shape


class SvgLoader:
    def __init__(self):
        self.cache = {}

    def load(self, filename):
        if filename in self.cache:
            return self.cache[filename]

        anim = parse_svg_file(filename)
        self.cache[filename] = anim
        return anim


class SvgFeature:
    def __init__(self, layer_names, colors):
        self.layer_names = layer_names
        self.colors = [parse_color(color) for color in colors]

    def iter_stylers(self, lottie_object):
        objects = []
        if self.layer_names:
            for layer_name in self.layer_names:
                found = lottie_object.find(layer_name)
                if found:
                    objects.append(found)
        else:
            objects = [lottie_object]

        for object in objects:
            for styler in object.find_all((shapes.Fill, shapes.Stroke)):
                if len(self.colors) == 0 or styler.color.value in self.colors:
                    yield styler

    def process(self, lottie_object, new_color):
        for styler in self.iter_stylers(lottie_object):
            styler.color.value = new_color


class SvgShape:
    def __init__(self, file, phrase, feature_map, main_feature, facing_direction, svg_loader: SvgLoader):
        self.file = file
        self.phrase = phrase
        self.feature_map = feature_map
        if isinstance(main_feature, str):
            self.main_feature = feature_map[main_feature]
        else:
            self.main_feature = main_feature
        self.facing_direction = facing_direction
        self.svg_loader = svg_loader

    def callback(self, parser: Parser, shape_data: ShapeData):
        lexind = parser.lexer.save()
        color = parser.color()
        if color:
            if parser.check_words(*self.feature_map.keys()):
                feature_name = parser.lexer.token.value
                shape_data.properties[feature_name].set_initial(color)
                parser.next()
                return True
        else:
            parser.lexer.restore(lexind)

        return False

    def match(self, parent, parser: Parser, shape_data: ShapeData):
        if not parser.check_word_sequence(self.phrase):
            return False

        shape_data.stroke_on_top = False
        svg_anim = parse_svg_file(self.file, 0, parser.lottie.out_point, parser.lottie.frame_rate)
        layer = svg_anim.layers[0].clone()
        group = shapes.Group()
        group.name = layer.name
        group.shapes = layer.shapes + group.shapes
        layer.transform.clone_into(group.transform)

        wrapper = shapes.Group()
        wrapper.add_shape(group)

        delta_ap = group.bounding_box(0).center()
        wrapper.transform.anchor_point.value += delta_ap
        wrapper.transform.position.value += delta_ap
        wrapper.transform.scale.value *= shape_data.size_multiplitier

        for name, feature in self.feature_map.items():
            singular = name[:-1] if name.endswith("s") else name
            shape_data.properties[name] = AnimatableProperty(singular + " color", None, [], AnimatableType.Color)
            for styler in feature.iter_stylers(group):
                shape_data.add_property(name, styler.color)

        if self.main_feature:
            shape_data.define_property("color", AnimatableType.Color, [])

            for styler in self.main_feature.iter_stylers(group):
                shape_data.add_property("color", styler.color)

            if shape_data.color and shape_data.color_explicit:
                shape_data.properties["color"].set_initial(shape_data.color)

        parser.properties(shape_data, self.callback, [parser, shape_data], ["with"])

        if self.facing_direction != 0 and parser.check_words("facing", "looking"):
            parser.next()
            if parser.skip_words("to"):
                parser.skip_words("the")

            if parser.check_words("left", "right"):
                direction = -1 if parser.token.value == "left" else 1
                if direction != self.facing_direction:
                    wrapper.transform.scale.value.x *= -1
            else:
                parser.warn("Missing facing direction")

            parser.next()

        shape_data.color = None
        parser.add_shape(parent, wrapper, shape_data)
        return True
