"""Contains a private class to handle plotting for
:class:`plotly_gtk.chart.PlotlyGTK`."""

import gi
import numpy as np

from plotly_gtk.utils import *  # pylint: disable=wildcard-import,unused-wildcard-import

gi.require_version("Gtk", "4.0")
from gi.repository import (  # pylint: disable=wrong-import-position,wrong-import-order
    Gtk,
    Pango,
    PangoCairo,
)

DEBUG = False


class _PlotlyGtk(Gtk.DrawingArea):
    def __init__(self, fig: dict):
        super().__init__()
        self.data = fig["data"]
        self.layout = fig["layout"]

        self.set_draw_func(self._on_draw)

    def update(self, fig: dict[str, plotly_types.Data, plotly_types.Layout]):
        """Update the plot with a new figure.

        Parameters
        ----------
        fig: dict[str, plotly_types.Data | plotly_types.Layout]
            A dictionary representing a plotly figure
        """
        self.data = fig["data"]
        self.layout = fig["layout"]
        self.queue_draw()

    def _on_draw(self, area, context, x, y):  # pylint: disable=unused-argument
        self.get_parent().automargin()

        width = area.get_size(Gtk.Orientation.HORIZONTAL)
        height = area.get_size(Gtk.Orientation.VERTICAL)

        self._draw_bg(context, width, height)
        self._draw_grid(context, width, height)
        self._plot(context, width, height)
        self._draw_axes(context, width, height)
        self._draw_all_ticks(context, width, height)

    def _draw_bg(self, context, width, height):
        context.set_source_rgb(*parse_color(self.layout["paper_bgcolor"]))
        context.rectangle(0, 0, width, height)
        context.fill()

        if DEBUG:
            context.set_source_rgb(*parse_color("pink"))
            context.rectangle(
                self.layout["_margin"]["l"],
                self.layout["_margin"]["t"],
                width - self.layout["_margin"]["l"] - self.layout["_margin"]["r"],
                height - self.layout["_margin"]["t"] - self.layout["_margin"]["b"],
            )
            context.fill()

        context.set_source_rgb(*parse_color(self.layout["plot_bgcolor"]))
        cartesian_subplots = get_cartesian_subplots(self.data)

        for xaxis, yaxis in cartesian_subplots:
            x = self.layout[xaxis]["_range"]
            y = self.layout[yaxis]["_range"]
            x_pos, y_pos = self._calc_pos(
                x, y, width, height, xaxis, yaxis, ignore_log_x=True, ignore_log_y=True
            )
            context.rectangle(
                x_pos[0], y_pos[0], x_pos[-1] - x_pos[0], y_pos[-1] - y_pos[0]
            )
            context.fill()

    def _draw_grid(self, context, width, height):
        axes = [k for k in self.layout if "axis" in k]
        for axis in axes:
            self._draw_gridlines(context, width, height, axis)

    def _draw_gridlines(self, context, width, height, axis):
        if "_range" not in self.layout[axis]:
            return
        if axis.startswith("x"):
            self.layout[axis]["_ticksobject"].length = (
                width - self.layout["_margin"]["l"] - self.layout["_margin"]["r"]
            ) * (self.layout[axis]["domain"][-1] - self.layout[axis]["domain"][0])

            self.layout[axis]["_ticksobject"].calculate()
        else:
            self.layout[axis]["_ticksobject"].length = (
                height - self.layout["_margin"]["t"] - self.layout["_margin"]["b"]
            ) * (self.layout[axis]["domain"][-1] - self.layout[axis]["domain"][0])
            self.layout[axis]["_ticksobject"].calculate()
        if "anchor" in self.layout[axis] and self.layout[axis]["anchor"] != "free":
            anchor = (
                self.layout[axis]["anchor"][0]
                + "axis"
                + self.layout[axis]["anchor"][1:]
            )
        else:
            cartesian_subplots = get_cartesian_subplots(self.data)
            cartesian_subplots = [
                subplot for subplot in cartesian_subplots if axis in subplot
            ]
            if axis.startswith("x"):
                anchors = [subplot[-1] for subplot in cartesian_subplots]
            else:
                anchors = [subplot[0] for subplot in cartesian_subplots]
            anchors.sort()
            anchor = anchors[-1]
        anchor_range = self.layout[anchor]["_range"]
        context.set_source_rgb(*parse_color(self.layout[axis]["gridcolor"]))
        if axis.startswith("x"):
            x = self.layout[axis]["_tickvals"]
            y = anchor_range
            x_pos, y_pos = self._calc_pos(
                x, y, width, height, axis, anchor, ignore_log_y=True
            )

            for tick in x_pos:
                context.line_to(tick, y_pos[0])
                context.line_to(tick, y_pos[1])
                context.stroke()

        else:
            y = self.layout[axis]["_tickvals"]
            x = anchor_range
            x_pos, y_pos = self._calc_pos(
                x, y, width, height, anchor, axis, ignore_log_x=True
            )

            for tick in y_pos:
                context.line_to(x_pos[0], tick)
                context.line_to(x_pos[1], tick)
                context.stroke()

    def _draw_all_ticks(self, context, width, height):
        axes = [k for k in self.layout if "axis" in k]
        for axis in axes:
            self._draw_ticks(context, width, height, axis)

    def _draw_ticks(
        self, context, width, height, axis
    ):  # pylint:disable=too-many-locals
        if (
            "_tickvals" not in self.layout[axis]
            or "_ticktext" not in self.layout[axis]
            or "_ticksobject" not in self.layout[axis]
        ):
            return
        if (
            "showticklabels" in self.layout[axis]
            and not self.layout[axis]["showticklabels"]
        ):
            return
        tickvals = self.layout[axis]["_tickvals"]
        ticktext = self.layout[axis]["_ticktext"]

        font_dict = self.layout["font"]
        font_dict["color"] = "#444"

        if "font" in self.layout[axis]:
            font_dict = update_dict(font_dict, self.layout[axis]["font"])
        if "tickfont" in self.layout[axis]:
            font_dict = update_dict(font_dict, self.layout[axis]["tickfont"])

        context.set_source_rgb(*parse_color(font_dict["color"]))
        font = parse_font(font_dict)
        layout = PangoCairo.create_layout(context)
        layout.set_font_description(font)
        if axis.startswith("x"):
            x = tickvals
            if "anchor" in self.layout[axis] and self.layout[axis]["anchor"] != "free":
                yaxis = (
                    self.layout[axis]["anchor"][0]
                    + "axis"
                    + self.layout[axis]["anchor"][1:]
                )
                y = self.layout[yaxis]["_range"][0]
                x_pos, y_pos = self._calc_pos(
                    x, y, width, height, axis, yaxis, ignore_log_y=True
                )
            else:
                y_pos = self.layout["_margin"]["t"] + (
                    1 - self.layout[axis]["_position"]
                ) * (height - self.layout["_margin"]["t"] - self.layout["_margin"]["b"])
                x_pos, _ = self._calc_pos(x, [], width, height, axis, None)

            for tick, text in zip(x_pos, ticktext):
                context.move_to(tick, y_pos)
                layout.set_markup(text)
                layout_size = layout.get_pixel_size()
                context.rel_move_to(-layout_size[0] / 2, 0)
                PangoCairo.show_layout(context, layout)

        else:
            y = tickvals
            if "anchor" in self.layout[axis] and self.layout[axis]["anchor"] != "free":
                xaxis = (
                    self.layout[axis]["anchor"][0]
                    + "axis"
                    + self.layout[axis]["anchor"][1:]
                )
                x = (
                    self.layout[xaxis]["_range"][-1]
                    if "side" in self.layout[axis]
                    and self.layout[axis]["side"] == "right"
                    else self.layout[xaxis]["_range"][0]
                )
                x_pos, y_pos = self._calc_pos(
                    x, y, width, height, xaxis, axis, ignore_log_x=True
                )
                x_pos += self.layout[axis]["_shift"]
            else:
                x_pos = (
                    self.layout["_margin"]["l"]
                    + self.layout[axis]["_position"]
                    * (
                        width
                        - self.layout["_margin"]["l"]
                        - self.layout["_margin"]["r"]
                    )
                    + self.layout[axis]["_shift"]
                )
                _, y_pos = self._calc_pos([], y, width, height, None, axis)

            for tick, text in zip(y_pos, ticktext):
                context.move_to(x_pos, tick)
                layout.set_markup(text)
                layout_size = layout.get_pixel_size()
                if "side" in self.layout[axis] and self.layout[axis]["side"] == "right":
                    context.rel_move_to(0, -layout_size[1] / 2)
                else:
                    context.rel_move_to(-layout_size[0], -layout_size[1] / 2)
                PangoCairo.show_layout(context, layout)

    def _draw_axes(self, context, width, height):
        axes = [k for k in self.layout if "axis" in k]
        for axis in axes:
            self._draw_axis(context, width, height, axis)

    def _draw_axis(self, context, width, height, axis):
        if "linecolor" not in self.layout[axis]:
            return
        context.set_source_rgb(*parse_color(self.layout[axis]["linecolor"]))
        if DEBUG:
            context.set_source_rgb(*parse_color("green"))

        axis_letter = axis[0 : axis.find("axis")]
        domain = self.layout[axis]["_domain"]
        position = self.layout[axis]["_position"]

        if axis_letter == "x":
            context.move_to(
                self.layout["_margin"]["l"]
                + domain[0]
                * (width - self.layout["_margin"]["l"] - self.layout["_margin"]["r"]),
                self.layout["_margin"]["t"]
                + (1 - position)
                * (height - self.layout["_margin"]["t"] - self.layout["_margin"]["b"]),
            )
            context.line_to(
                self.layout["_margin"]["l"]
                + domain[-1]
                * (width - self.layout["_margin"]["l"] - self.layout["_margin"]["r"]),
                self.layout["_margin"]["t"]
                + (1 - position)
                * (height - self.layout["_margin"]["t"] - self.layout["_margin"]["b"]),
            )
        elif axis_letter == "y":
            context.move_to(
                self.layout["_margin"]["l"]
                + position
                * (width - self.layout["_margin"]["l"] - self.layout["_margin"]["r"])
                + self.layout[axis]["_shift"],
                self.layout["_margin"]["t"]
                + (1 - domain[0])
                * (height - self.layout["_margin"]["t"] - self.layout["_margin"]["b"]),
            )
            context.line_to(
                self.layout["_margin"]["l"]
                + position
                * (width - self.layout["_margin"]["l"] - self.layout["_margin"]["r"])
                + self.layout[axis]["_shift"],
                self.layout["_margin"]["t"]
                + (1 - domain[-1])
                * (height - self.layout["_margin"]["t"] - self.layout["_margin"]["b"]),
            )
        context.stroke()

    def _calc_pos(
        self,
        x,
        y,
        width,
        height,
        xaxis=None,
        yaxis=None,
        ignore_log_x=False,
        ignore_log_y=False,
    ):  # pylint: disable=too-many-arguments,too-many-locals
        if isinstance(xaxis, str):
            xaxis = self.layout[xaxis] if xaxis in self.layout else None
        if isinstance(yaxis, str):
            yaxis = self.layout[yaxis] if yaxis in self.layout else None
        log_x = (
            xaxis["type"] == "log" if xaxis is not None and "type" in xaxis else False
        )
        log_y = (
            yaxis["type"] == "log" if yaxis is not None and "type" in yaxis else False
        )

        if log_x and not ignore_log_x:
            x = np.log10(x)
        if log_y and not ignore_log_y:
            y = np.log10(y)

        x_pos = []
        y_pos = []

        if xaxis is not None:
            xdomain = xaxis["_domain"]
            xaxis_start = (
                xdomain[0]
                * (width - self.layout["_margin"]["l"] - self.layout["_margin"]["r"])
                + self.layout["_margin"]["l"]
            )
            xaxis_end = (
                xdomain[-1]
                * (width - self.layout["_margin"]["l"] - self.layout["_margin"]["r"])
                + self.layout["_margin"]["l"]
            )

            x_min = xaxis["_range"][0]
            x_max = xaxis["_range"][1]
            x_pos = (x - x_min) / (x_max - x_min) * (
                xaxis_end - xaxis_start
            ) + xaxis_start

        if yaxis is not None:
            ydomain = yaxis["_domain"]
            yaxis_start = (
                -ydomain[0]
                * (height - self.layout["_margin"]["t"] - self.layout["_margin"]["b"])
                + height
                - self.layout["_margin"]["b"]
            )
            yaxis_end = (
                -ydomain[-1]
                * (height - self.layout["_margin"]["t"] - self.layout["_margin"]["b"])
                + height
                - self.layout["_margin"]["b"]
            )

            y_min = yaxis["_range"][0]
            y_max = yaxis["_range"][1]
            y_pos = (y - y_min) / (y_max - y_min) * (
                yaxis_end - yaxis_start
            ) + yaxis_start

        return x_pos, y_pos

    def _set_trace_color(self, context, plot, index):
        if "marker" in plot and "color" in plot["marker"]:
            color = plot["marker"]["color"]
        else:
            color = self.layout["template"]["layout"]["colorway"][index]
        context.set_source_rgb(*parse_color(color))

    def _plot(self, context, width, height):
        index = 0
        for plot in self.data:
            plot_type = plot["type"]
            if not plot["visible"]:
                continue

            if "_visible" in plot and not plot["_visible"]:
                index += 1
                continue

            self._set_trace_color(context, plot, index)
            if plot_type in ["scatter", "scattergl"]:
                self._plot_scatter(context, width, height, plot, index)
            elif plot_type == "histogram":
                self._plot_histogram(context, width, height, plot, index)
            index += 1

    def _plot_histogram(
        self, context, width, height, plot, index
    ):  # pylint: disable=too-many-arguments,unused-argument
        for i in range(0, len(plot["y"])):
            x = [plot["x"][i], plot["x"][i], plot["x"][i + 1], plot["x"][i + 1]]
            y = [0, plot["y"][i], plot["y"][i], 0]

            xaxis, yaxis = self._get_axes(plot)

            x_pos, y_pos = self._calc_pos(x, y, width, height, xaxis, yaxis)
            context.new_path()

            for i in range(0, 4):
                context.line_to(x_pos[i], y_pos[i])

            context.close_path()
            context.fill()

    def _get_axes(self, plot):
        xaxis = plot["xaxis"] if "xaxis" in plot else "x"
        yaxis = plot["yaxis"] if "yaxis" in plot else "y"
        xaxis = xaxis.replace("x", "xaxis")
        yaxis = yaxis.replace("y", "yaxis")

        xaxis = self.layout[xaxis] if xaxis in self.layout else {}
        yaxis = self.layout[yaxis] if yaxis in self.layout else {}

        return xaxis, yaxis

    def _plot_scatter(
        self, context, width, height, plot, index
    ):  # pylint: disable=too-many-locals,too-many-arguments,unused-argument
        if "mode" in plot:
            mode = plot["mode"]
        elif len(plot["x"]) <= 20:
            mode = "lines+markers"
        else:
            mode = "lines"
        modes = mode.split("+")

        xaxis, yaxis = self._get_axes(plot)

        x_pos, y_pos = self._calc_pos(plot["x"], plot["y"], width, height, xaxis, yaxis)

        if "markers" in modes:
            context.new_path()
            if not isinstance(plot["marker"]["size"], (list, np.ndarray)):
                size = np.array([plot["marker"]["size"]] * len(plot["x"]))
            else:
                size = np.array(plot["marker"]["size"]) / plot["marker"]["sizeref"]
            radius = (
                size / 2
                if plot["marker"]["sizemode"] == "diameter"
                else np.sqrt(size / np.pi)
            )

            for x, y, r in zip(x_pos, y_pos, radius):
                if np.isnan(x) or np.isnan(y):
                    continue
                context.arc(x, y, r, 0, 2 * np.pi)
                context.fill()
        if "lines" in modes:
            context.set_line_width(plot["line"]["width"])
            for x, y in zip(x_pos, y_pos):
                if np.isnan(x) or np.isnan(y):
                    context.stroke()
                    continue
                context.line_to(x, y)
            context.stroke()
