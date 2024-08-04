import re

from .font import FontStyle
from ..nvector import NVector
from ..parsers.svg.importer import parse_color
from ..objects.shapes import Group, Fill


class FancyStyle:
    def __init__(self, font: FontStyle, color: NVector, font_size: float, offset: NVector, scale: NVector, rotation: float):
        self.font = font
        self.color = color.clone()
        self.font_size = font_size
        self.offset = offset.clone()
        self.scale = scale.clone()
        self.rotation = rotation

    def clone(self):
        return FancyStyle(self.font, self.color, self.font_size, self.offset, self.scale, self.rotation)

    def render(self, text, pos, start_x):
        pos += self.offset
        g = self.font.renderer.render(text, self.font_size, pos, True, start_x)
        g.add_shape(Fill(self.color))
        if self.scale.x != 1 or self.scale.y != 1 or self.rotation != 0:
            center = g.bounding_box().center()
            g.transform.anchor_point.value = center
            g.transform.position.value += center
            g.transform.scale.value = self.scale * 100
            g.transform.rotation.value = self.rotation
        pos -= self.offset
        return g


class FancyTextRenderer:
    _regex = re.compile(r'\\([a-z0-9]+)(?:\{([^}]*)\})?')

    def __init__(self, font: FontStyle, default_color: NVector, font_size: float):
        self.font = font
        self.font_size = font_size
        self.default_color = default_color
        self.groups = []

    @staticmethod
    def _int_arg(value, default=0):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def render(self, text: str, pos: NVector = None):
        if pos is None:
            pos = NVector(0, 0)

        line_start = pos.x
        default_style = FancyStyle(self.font, self.default_color, self.font_size, NVector(0, 0), NVector(1, 1), 0)
        style = default_style.clone()
        container = Group()
        last_pos = 0

        for match in self._regex.finditer(text):
            prev_text = text[last_pos:match.start()]
            last_pos = match.end()
            if prev_text:
                container.insert_shape(0, style.render(prev_text, pos, line_start))

            style = style.clone()

            command = match.group(1)
            arg = match.group(2)

            if command == "color":
                if arg:
                    style.color = parse_color(arg, self.default_color)
                else:
                    style.color = self.default_color
            elif command == "huge":
                style.font_size = self.font_size * 2
            elif command == "large":
                style.font_size = self.font_size * 1.5
            elif command == "normal":
                style.font_size = self.font_size
            elif command == "small":
                style.font_size = self.font_size / 1.5
            elif command == "tiny":
                style.font_size = self.font_size / 2
            elif command == "super":
                style.offset.y -= self.font_size / 2
            elif command == "sub":
                style.offset.y += self.font_size / 2
            elif command == "center":
                style.offset.y = 0
            elif command == "clear":
                style = default_style.clone()
            elif command == "flip":
                style.scale.x *= -1
            elif command == "vflip":
                style.scale.y *= -1
            elif command == "r":
                pos.x = line_start
            elif command == "n":
                pos.x = line_start
                pos.y += self.font.line_height
            elif command == "hspace":
                pos.x += self._int_arg(arg)
            elif command == "rot":
                style.rotation = self._int_arg(arg)

            # Eat space after no argument command
            if arg is None and len(text) > last_pos and text[last_pos] == ' ':
                last_pos += 1

        last_text = text[last_pos:]
        if last_text:
            container.insert_shape(0, style.render(last_text, pos, line_start))

        if len(container.shapes) > 1:
            container.next_x = container.shapes[-2].next_x
        else:
            container.next_x = pos.x

        return container


def render_fancy_text(text: str, font: FontStyle, default_color: NVector, font_size: float, pos: NVector = None):
    renderer = FancyTextRenderer(font, default_color, font_size)
    return renderer.render(text, pos)
