import math
import typing
import random

from dataclasses import dataclass
from .. import objects
from .color import Color
from ..nvector import NVector
from ..objects import easing
from . import ellipse


class Datum:
    def __init__(self, value: float, color: Color):
        self.value = value
        self.color = color

    def add_style(self, group: objects.Group):
        group.add_shape(objects.Fill(self.color))


class DataSet:
    def __init__(self, data: typing.List[Datum]):
        self.data = data

    def normalize_values(self, sum_to_one=False):
        """!
        Ensures all values are in [0, 1]

        @param sum_to_one if \b True, the sum all values will be 1
        """
        if sum_to_one:
            max_value = sum(datum.value for datum in self.data)
        else:
            max_value = max(datum.value for datum in self.data)

        if max_value == 0:
            return

        for datum in self.data:
            datum.value /= max_value

    def add(self, value: float, color: Color):
        self.data.append(Datum(value, color))


@dataclass
class AnimationSettings:
    #! Time at which the animation starts
    start: float = 0
    #! Duration from start until an item is fully visible
    fade_in: float = 0
    #! Duration the item is fully visible
    stay: float = 0
    #! Duration of the item disappearing
    fade_out: float = 0
    #! End time
    end: float = 0
    #! Offset between items
    offset: float = 0

    @classmethod
    def computed(cls, item_count, duration, stay, full_stay, start=0):
        """!
        @param item_count   Number of items to animate
        @param dutation     Total duration
        @param stay         Duration for which each item is fully visible
        @param full_stay    Duration for all each items are fully visible
        @param start        Start time
        """

        overlap = stay - full_stay
        offset = overlap / (item_count - 1)
        partial_stay = stay + overlap
        inout = duration - partial_stay

        return AnimationSettings(
            start=start,
            fade_in=inout * 2 / 3,
            stay=stay,
            fade_out=inout / 3,
            offset=offset,
            end=start+duration,
        )

    def to_global_times(self):
        """!
        Converts durations into global times
        """
        self.fade_in += self.start
        self.stay += self.fade_in
        self.fade_out += self.stay


class DatumAnimation:
    def __init__(self, datum: Datum, index_in: int, index_out: int, index_count: int, settings: AnimationSettings):
        self.datum = datum
        self.index_in = index_in
        self.index_out = index_out
        off1 = self.index_in * settings.offset
        off2 = self.index_out * settings.offset
        off_max = index_count * settings.offset
        self.times = AnimationSettings(
            start=settings.start + off1,
            end=settings.end - off_max + off2
        )
        self.times.fade_in = self.times.start + settings.fade_in
        self.times.fade_out = self.times.end - settings.fade_out
        self.times.stay = self.times.fade_out


class ChartType:
    def animate(self, area: objects.BoundingBox, anim: DatumAnimation, index: int, total: int, sum_before: float):
        raise NotImplementedError()


class Histogram(ChartType):
    def animate(self, area: objects.BoundingBox, anim: DatumAnimation, index: int, total: int, sum_before: float):
        x = area.width / total * (index + .5) + area.x1
        width = area.width / (total + 1)
        height = area.height * anim.datum.value

        group = objects.Group()
        rect = group.add_shape(objects.Rect())
        anim.datum.add_style(group)

        rect.position.add_keyframe(anim.times.start,    NVector(x, area.y2), easing.EaseOut())
        rect.position.add_keyframe(anim.times.fade_in,  NVector(x, area.y2 - height / 2), easing.EaseOut())
        rect.position.add_keyframe(anim.times.fade_out, NVector(x, area.y2 - height / 2), easing.EaseOut())
        rect.position.add_keyframe(anim.times.end,      NVector(x, area.y2), easing.EaseOut())

        rect.size.add_keyframe(anim.times.start,    NVector(width, 0), easing.EaseOut())
        rect.size.add_keyframe(anim.times.fade_in,  NVector(width, height), easing.EaseOut())
        rect.size.add_keyframe(anim.times.fade_out, NVector(width, height), easing.EaseOut())
        rect.size.add_keyframe(anim.times.end,      NVector(width, 0), easing.EaseOut())

        return group


class PieFan(ChartType):
    def animate(self, area: objects.BoundingBox, anim: DatumAnimation, index: int, total: int, sum_before: float):
        angle_start = sum_before * math.pi * 2
        angle_delta = anim.datum.value * math.pi * 2

        rad = min(area.width, area.height) / 2
        ellipser = ellipse.Ellipse(area.center(), NVector(rad, rad), 0)

        group = objects.Group()
        shape = group.add_shape(objects.Path())

        cache = {}

        self.add_transition(shape, ellipser, angle_start, 0, angle_delta, anim.times.start, anim.times.fade_in, cache)
        self.add_transition(shape, ellipser, angle_start, angle_delta, 0, anim.times.fade_out, anim.times.end, cache)

        anim.datum.add_style(group)
        return group

    def add_arc(self, shape, ellipser, angle_start, angle_delta, time, cache):
        if angle_delta not in cache:
            if angle_delta == 0:
                bez = objects.Bezier()
                p = ellipser.center + NVector(
                    math.cos(angle_start) * ellipser.radii.x,
                    math.sin(angle_start) * ellipser.radii.x
                )
                bez.add_point(p)
                bez.add_point(p)
                bez.add_point(p)
                bez.add_point(p)
            else:
                bez = ellipser.to_bezier(angle_start, angle_delta, angle_delta / 4)
                bez.in_tangents[0] = bez.out_tangents[-1] = NVector(0, 0)

            bez.add_point(ellipser.center)
            bez.add_point(ellipser.center)
            bez.close()

            cache[angle_delta] = bez
        else:
            bez = cache[angle_delta]

        shape.shape.add_keyframe(time, bez)

    def add_transition(self, shape, ellipser, angle_start, angle_delta_from, angle_delta_to, time_from, time_to, cache):
        chunks = round(max(angle_delta_from, angle_delta_to) / math.pi * 100)
        for step in range(chunks + 1):
            f = step / chunks
            angle_delta = f * angle_delta_to + (1-f) * angle_delta_from
            time = f * time_to + (1-f) * time_from
            self.add_arc(shape, ellipser, angle_start, angle_delta, time, cache)


class PieGrow(ChartType):
    def animate(self, area: objects.BoundingBox, anim: DatumAnimation, index: int, total: int, sum_before: float):
        angle_start = sum_before * math.pi * 2
        angle_delta = anim.datum.value * math.pi * 2

        group = objects.Group()
        shape = group.add_shape(objects.Path())

        rad = min(area.width, area.height) / 2
        bez_0 = self.arc_to_bezier(area.center(), 0, 0, 0)
        bez_1 = self.arc_to_bezier(area.center(), angle_start, angle_delta, rad)

        shape.shape.add_keyframe(anim.times.start,    bez_0, easing.EaseOut())
        shape.shape.add_keyframe(anim.times.fade_in,  bez_1, easing.EaseOut())
        shape.shape.add_keyframe(anim.times.fade_out, bez_1, easing.EaseOut())
        shape.shape.add_keyframe(anim.times.end,      bez_0, easing.EaseOut())

        anim.datum.add_style(group)
        return group

    def arc_to_bezier(self, center, angle_start, angle_delta, radius):
        if radius == 0:
            bez = objects.Bezier()
            p = center
            bez.add_point(p)
            bez.add_point(p)
            bez.add_point(p)
            bez.add_point(p)
        elif angle_delta == 0:
            bez = objects.Bezier()
            p = center + NVector(math.cos(angle_start) * radius, math.sin(angle_start) * radius)
            bez.add_point(p)
            bez.add_point(p)
            bez.add_point(p)
            bez.add_point(p)
        else:
            ellipser = ellipse.Ellipse(center, NVector(radius, radius), 0)
            bez = ellipser.to_bezier(angle_start, angle_delta, angle_delta / 4)
            bez.in_tangents[0] = bez.out_tangents[-1] = NVector(0, 0)

        # Dunno why we need to add it twice but it doesn't work with just one o_O
        bez.add_point(center)
        bez.add_point(center)
        bez.close()

        return bez


class AnimationOrder:
    def indices(self, data: DataSet):
        """!
        Returns two list of indices indicating the order of animation
        for fade in and out of the elements

        The lists are laid out so that the nth element is the index at
        which that element animates at
        """
        raise NotImplementedError

    def __call__(self, data: DataSet):
        return self.indices(data)


class RandomOrder(AnimationOrder):
    def indices(self, data: DataSet):
        indices_in = list(range(len(data.data)))
        indices_out = list(indices_in)
        random.shuffle(indices_in)
        random.shuffle(indices_out)
        return indices_in, indices_out


class SequentialOrder(AnimationOrder):
    def indices(self, data: DataSet):
        indices = list(range(len(data.data)))
        return indices, indices


class SortValueOrder(AnimationOrder):
    def __init__(self, largest_first=True):
        self.largest_first = largest_first

    def indices(self, data: DataSet):
        info = sorted(enumerate(data.data), key=lambda it: it[1].value)
        if self.largest_first:
            info = reversed(info)

        ranking = [it[0] for it in info]
        indices = list(map(ranking.index, range(len(data.data))))
        return indices, indices


class SimultaneousOrder(AnimationOrder):
    def indices(self, data: DataSet):
        n = len(data.data)
        return [0] * n, [n-1] * n


class FixedOrder(AnimationOrder):
    def __init__(self, indices_in, indices_out=None):
        self.indices_in = indices_in
        self.indices_out = indices_out or indices_in

    def indices(self, data: DataSet):
        return self.indices_in, self.indices_out


class Chart:
    def __init__(self, type=Histogram(), area=None, data=None, animation=None, order=SimultaneousOrder()):
        self.type = type
        self.area = area or objects.BoundingBox(0, 0, 512, 512)
        self.timing = animation or AnimationSettings()
        self.order = order

        if isinstance(data, DataSet):
            self.data = data
        else:
            self.data = DataSet(data or [])

    def compute_animation(self, *a, **kw):
        self.timing = AnimationSettings.computed(len(self.data.data), *a, **kw)

    def shapes(self):
        total = len(self.data.data)
        indices_in, indices_out = self.order(self.data)
        shapes = []

        value_sum = 0

        for i, (datum, ii, io) in enumerate(zip(self.data.data, indices_in, indices_out)):
            anim = DatumAnimation(datum, ii, io, total, self.timing)
            shapes.append(self.type.animate(self.area, anim, i, total, value_sum))
            value_sum += datum.value

        return shapes

    def layer(self):
        layer = objects.ShapeLayer()
        layer.shapes = self.shapes()
        return layer

    def animation(self):
        animation = objects.Animation()
        animation.width = self.area.x2
        animation.height = self.area.y2
        animation.in_point = self.timing.start
        animation.out_point = self.timing.end
        animation.add_layer(self.layer())
        return animation
