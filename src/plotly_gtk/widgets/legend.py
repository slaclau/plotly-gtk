import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from typing import TYPE_CHECKING

import numpy as np
from gi.repository import Gdk, Gtk  # noqa: E402

from plotly_gtk.utils import parse_color, update_dict
from plotly_gtk.widgets.base import Base

if TYPE_CHECKING:
    from plotly_gtk.chart import PlotlyGtk


class Legend(Base):
    def __init__(self, plot: "PlotlyGtk", legend: dict):
        super().__init__()
        grid = Gtk.Grid(row_spacing=4, column_spacing=4)
        self.append(grid)

        if legend["xref"] == "paper":
            x_default = 1.02 if legend["orientation"] == "v" else 0
        elif legend["xref"] == "container":
            x_default = 1 if legend["orientation"] == "v" else 0
        else:
            raise ValueError(f"Unknown legend.xref {legend["xref"]}")

        if legend["yref"] == "paper":
            y_default = 1 if legend["orientation"] == "v" else -0.1
        elif legend["yref"] == "container":
            y_default = 1
        else:
            raise ValueError(f"Unknown legend.yref {legend["yref"]}")

        default = dict(bgcolor=plot.layout["paper_bgcolor"], x=x_default, y=y_default)
        legend = update_dict(default, legend)

        if legend["yanchor"] == "auto":
            yanchor_default = (
                "top" if legend["y"] > 2 / 3 else "bottom" if legend["y"] < 1 / 3 else 0
            )
            legend["yanchor"] = yanchor_default

        self.spec = legend

        if legend["orientation"] == "v":
            self.set_orientation(Gtk.Orientation.VERTICAL)
        elif legend["orientation"] == "h":
            self.set_orientation(Gtk.Orientation.HORIZONTAL)
        else:
            raise ValueError(f"Unknown legend.orientation {legend["orientation"]}")

        def on_click(n, _trace):
            if n == 1:
                action = legend["itemclick"]
            elif n == 2:
                action = legend["itemdoubleclick"]

            if action == "toggle":
                if "_visible" not in _trace:
                    _trace["_visible"] = _trace["visible"]
                _trace["_visible"] = not _trace["_visible"]
            elif action == "toggleothers":
                for trace in plot.data:
                    trace["_visible"] = not _trace["visible"]
                _trace["_visible"] = not _trace["_visible"]
            elif action == "none":
                pass
            else:
                raise ValueError(f"Unknown action {action}")

            plot.update(dict(data=plot.data, layout=plot.layout))

        index = 0
        for trace in plot.data:
            if trace["type"] not in ["scatter", "scattergl"]:
                continue
            if "visible" in trace and not trace["visible"]:
                continue

            icon = Icon(plot, trace, index)
            icon.set_size_request(legend["itemwidth"], -1)
            icon.set_cursor_from_name("pointer")
            click = Gtk.GestureClick.new()
            click.connect(
                "pressed", lambda g, n, x, y: on_click(n, g.get_widget().trace)
            )
            icon.add_controller(click)
            grid.attach(icon, 0, index, 1, 1)
            name = trace["name"] if "name" in trace else ""
            label = Gtk.Label(label=name)
            label.set_halign(Gtk.Align.START)
            label.set_cursor_from_name("pointer")
            label.trace = trace
            click = Gtk.GestureClick.new()
            click.connect(
                "pressed", lambda g, n, x, y: on_click(n, g.get_widget().trace)
            )
            if "_visible" in trace and not trace["_visible"]:
                label.add_css_class("plotly-legend-clicked")
            label.add_controller(click)

            grid.attach(label, 1, index, 1, 1)
            index += 1

        if index == 1:
            self.remove(grid)
            return

        font = legend["font"]
        custom_css = Gtk.CssProvider()
        custom_css.load_from_string(
            f"""
            .plotly-legend {{
                background-color: {legend["bgcolor"]};
                border: {legend["borderwidth"]}px solid {legend["bordercolor"]};
                box-shadow: none;
            }}
            .plotly-legend label {{
                color: {font["color"]};
                font-family: {font["family"]};
                font-size: {font["size"]}px;
                font-style: {font["style"]};
                font-variant: {font["variant"]};
                font-weight: {font["weight"]};
            }}
            .plotly-legend-clicked {{
                color: lighter({legend["font"]["color"]});
            }}
            """
        )
        Gtk.StyleContext().add_provider_for_display(
            Gdk.Display().get_default(),
            custom_css,
            Gtk.STYLE_PROVIDER_PRIORITY_USER,
        )

        self.add_css_class("plotly-legend")


class Icon(Gtk.DrawingArea):
    def __init__(self, plot, trace, index):
        super().__init__()
        self.plot = plot
        self.trace = trace
        self.index = index
        self.set_draw_func(self.on_draw)

        self.line_width = None
        self.marker_radius = None

    def on_draw(self, area, context, x, y):
        if "mode" in self.trace:
            mode = self.trace["mode"]
        elif len(self.trace["x"]) <= 20:
            mode = "lines+markers"
        else:
            mode = "lines"
        modes = mode.split("+")

        width = area.get_size(Gtk.Orientation.HORIZONTAL)
        height = area.get_size(Gtk.Orientation.VERTICAL)

        if "markers" in modes:
            if "color" in self.trace["marker"]:
                color = self.trace["marker"]["color"]
            else:
                color = self.plot.layout["template"]["layout"]["colorway"][self.index]
            color = parse_color(color)
            if "_visible" in self.trace and not self.trace["_visible"]:
                color = [c + (1 - c) / 2 for c in color]
            context.set_source_rgb(*color)

            radius = (
                self.trace["marker"]["size"] / 2
                if self.trace["marker"]["sizemode"] == "diameter"
                else np.sqrt(self.trace["marker"]["size"] / np.pi)
            )
            context.arc(width / 2, height / 2, radius, 0, 2 * np.pi)
            context.fill()
            self.marker_radius = radius
        if "lines" in modes:
            if "color" in self.trace["line"]:
                color = self.trace["line"]["color"]
            else:
                color = self.plot.layout["template"]["layout"]["colorway"][self.index]
            color = parse_color(color)
            if "_visible" in self.trace and not self.trace["_visible"]:
                color = [c + (1 - c) / 2 for c in color]
            context.set_source_rgb(*color)
            context.set_line_width(self.trace["line"]["width"])
            context.line_to(0, height / 2)
            context.line_to(width, height / 2)
            context.stroke()
            self.line_width = self.trace["line"]["width"]
