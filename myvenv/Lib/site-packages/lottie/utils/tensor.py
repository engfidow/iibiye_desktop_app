from .. import objects


class TensorSerializer:
    def process(self, animation: objects.Animation, flatten: bool = True):
        data = []
        for layer in animation.layers:
            self.process_layer(layer, data)

        if flatten:
            return self.flatten(data)

        return data

    def process_layer(self, layer, data):
        if not isinstance(layer, objects.ShapeLayer):
            return

        self.process_shape_group(layer, data)

    def process_shape(self, shape: objects.Path, data: dict):
        bez = shape.shape.get_value()
        if bez and len(bez.vertices) > 1:
            data["curves"].append(bez)

    def process_styler(self, styler):
        return {
            "opacity": (styler.opacity.get_value() or 100) / 100,
            "color":
                styler.gradient.get_stops()[0][0]
                if isinstance(styler, objects.Gradient)
                else styler.color.get_value()
        }

    def process_shape_group(self, group, data):
        shape_data = {
            "curves": [],
            "fill": None,
            "stroke": None
        }

        for shape in group.shapes:
            if shape.hidden:
                continue

            if isinstance(shape, objects.Group):
                child_data = self.process_shape_group(shape, data)
                shape_data["curves"] += child_data["curves"]
            elif isinstance(shape, objects.Path):
                self.process_shape(shape, shape_data)
            elif isinstance(shape, objects.Shape):
                self.process_shape(shape.to_bezier(), shape_data)
            elif isinstance(shape, (objects.Fill, objects.GradientFill)):
                shape_data["fill"] = self.process_styler(shape)
            elif isinstance(shape, objects.BaseStroke):
                shape_data["stroke"] = self.process_styler(shape)
                shape_data["stroke"]["width"] = shape.width.get_value()

        if shape_data["curves"] and (shape_data["fill"] or shape_data["stroke"]):
            data.append(shape_data)

        return shape_data

    def flatten_color(self, data):
        if not data:
            return None
        return list(data["color"])[0:3] + [data["opacity"]]

    def flatten(self, data):
        flattened = []
        for item in data:
            base = {
                "fill": self.flatten_color(item["fill"]),
                "stroke": self.flatten_color(item["stroke"]),
                "stroke_width": item["stroke"]["width"] if item["stroke"] else 0,
            }
            base["color"] = base["fill"] or base["stroke"]

            for curve in item["curves"]:
                points = []
                for i in range(len(curve.vertices)):
                    v = curve.vertices[i]
                    points.append(list(v))
                    points.append(list(curve.out_tangents[i] + v))
                    next_i = (i+1) % len(curve.vertices)
                    points.append(list(curve.in_tangents[next_i] + curve.vertices[next_i]))

                if curve.closed:
                    points.push(list(curve.vertices[0]))
                else:
                    points.pop()
                    points.pop()

                flattened.append({
                    **base,
                    "points": points,
                    "closed": int(curve.closed)
                })

        return flattened
