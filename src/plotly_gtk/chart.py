import datetime
from datetime import timezone

import gi
import numpy as np
import pandas as pd
from plotly import graph_objects as go

from plotly_gtk.utils import parse_color, parse_font, round_sf, update_dict
from plotly_gtk.utils.ticks import Ticks
from plotly_gtk.widgets import *

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, PangoCairo  # noqa: E402

DEBUG = False


class _PlotlyGtk(Gtk.DrawingArea):
    def __init__(self, fig: dict):
        super().__init__()
        self.data = fig["data"]
        self.layout = fig["layout"]

        self.set_draw_func(self.on_draw)

    def update(self, fig):
        self.data = fig["data"]
        self.layout = fig["layout"]
        self.queue_draw()

    def on_draw(self, area, context, x, y):
        self.get_parent().automargin()

        width = area.get_size(Gtk.Orientation.HORIZONTAL)
        height = area.get_size(Gtk.Orientation.VERTICAL)

        self.draw_bg(context, width, height)
        self.draw_grid(context, width, height)
        self.plot(context, width, height)
        self.draw_axes(context, width, height)
        self.draw_all_ticks(context, width, height)

    def draw_bg(self, context, width, height):
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

        xaxes = [k for k in self.layout if "xaxis" in k]
        yaxes = [k for k in self.layout if "yaxis" in k]

        context.set_source_rgb(*parse_color(self.layout["plot_bgcolor"]))
        cartesian_subplots = {
            (
                xaxis,
                self.layout[xaxis]["anchor"][0]
                + "axis"
                + self.layout[xaxis]["anchor"][1:],
            )
            for xaxis in xaxes
        } | {
            (
                self.layout[yaxis]["anchor"][0]
                + "axis"
                + self.layout[yaxis]["anchor"][1:],
                yaxis,
            )
            for yaxis in yaxes
        }
        paper_width = width - self.layout["_margin"]["l"] - self.layout["_margin"]["r"]
        paper_height = (
            height - self.layout["_margin"]["t"] - self.layout["_margin"]["b"]
        )
        for xaxis, yaxis in cartesian_subplots:
            x = self.layout[xaxis]["_range"]
            y = self.layout[yaxis]["_range"]
            x_pos, y_pos = self.calc_pos(x, y, width, height, xaxis, yaxis)
            context.rectangle(
                x_pos[0], y_pos[0], x_pos[-1] - x_pos[0], y_pos[-1] - y_pos[0]
            )
            context.fill()

    def draw_grid(self, context, width, height):
        axes = [k for k in self.layout if "axis" in k]
        for axis in axes:
            self.draw_gridlines(context, width, height, axis)

    def draw_gridlines(self, context, width, height, axis):
        if "_range" not in self.layout[axis]:
            return
        if axis.startswith("x"):
            self.layout[axis]["_ticksobject"].update_length(
                (width - self.layout["_margin"]["l"] - self.layout["_margin"]["r"])
                * (self.layout[axis]["domain"][-1] - self.layout[axis]["domain"][0])
            )
            self.layout[axis]["_ticksobject"].calculate()
        else:
            self.layout[axis]["_ticksobject"].update_length(
                (height - self.layout["_margin"]["t"] - self.layout["_margin"]["b"])
                * (self.layout[axis]["domain"][-1] - self.layout[axis]["domain"][0])
            )
            self.layout[axis]["_ticksobject"].calculate()
        anchor = (
            self.layout[axis]["anchor"][0] + "axis" + self.layout[axis]["anchor"][1:]
        )
        anchor_range = self.layout[anchor]["_range"]
        context.set_source_rgb(*parse_color(self.layout[axis]["gridcolor"]))
        if axis.startswith("x"):
            x = self.layout[axis]["_tickvals"]
            y = anchor_range
            x_pos, y_pos = self.calc_pos(x, y, width, height, axis, anchor)

            for tick in x_pos:
                context.line_to(tick, y_pos[0])
                context.line_to(tick, y_pos[1])
                context.stroke()

        else:
            y = self.layout[axis]["_tickvals"]
            x = anchor_range
            x_pos, y_pos = self.calc_pos(x, y, width, height, anchor, axis)

            for tick in y_pos:
                context.line_to(x_pos[0], tick)
                context.line_to(x_pos[1], tick)
                context.stroke()

    def draw_all_ticks(self, context, width, height):
        axes = [k for k in self.layout if "axis" in k]
        for axis in axes:
            self.draw_ticks(context, width, height, axis)

    def draw_ticks(self, context, width, height, axis):
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

        if "font" in self.layout[axis]:
            font_dict = update_dict(self.layout["font"], self.layout[axis]["font"])
        else:
            font_dict = self.layout["font"]
            font_dict["color"] = "#444"

        context.set_source_rgb(*parse_color(font_dict["color"]))
        font = parse_font(font_dict)
        layout = PangoCairo.create_layout(context)
        layout.set_font_description(font)
        if axis.startswith("x"):
            x = tickvals
            yaxis = (
                self.layout[axis]["anchor"][0]
                + "axis"
                + self.layout[axis]["anchor"][1:]
            )
            y = self.layout[yaxis]["_range"][0]
            x_pos, y_pos = self.calc_pos(x, y, width, height, axis, yaxis)

            for tick, text in zip(x_pos, ticktext):
                context.move_to(tick, y_pos)
                layout.set_text(text)
                layout_size = layout.get_pixel_size()
                context.rel_move_to(-layout_size[0] / 2, 0)
                PangoCairo.show_layout(context, layout)

        else:
            y = tickvals
            xaxis = (
                self.layout[axis]["anchor"][0]
                + "axis"
                + self.layout[axis]["anchor"][1:]
            )
            x = self.layout[xaxis]["_range"][0]
            x_pos, y_pos = self.calc_pos(x, y, width, height, xaxis, axis)

            for tick, text in zip(y_pos, ticktext):
                context.move_to(x_pos, tick)
                layout.set_text(text)
                layout_size = layout.get_pixel_size()
                context.rel_move_to(-layout_size[0], -layout_size[1] / 2)
                PangoCairo.show_layout(context, layout)

    def draw_axes(self, context, width, height):
        axes = [k for k in self.layout if "axis" in k]
        for axis in axes:
            self.draw_axis(context, width, height, axis)

    def draw_axis(self, context, width, height, axis):
        if "linecolor" not in self.layout[axis]:
            return
        context.set_source_rgb(*parse_color(self.layout[axis]["linecolor"]))
        axis_letter = axis[0 : axis.find("axis")]
        domain = self.layout[axis]["domain"]
        position = self.layout[axis]["position"]

        context.line_to(
            self.layout["_margin"]["l"], height - self.layout["_margin"]["b"]
        )
        context.line_to(
            width - self.layout["_margin"]["r"],
            height - self.layout["_margin"]["b"],
        )
        context.stroke()

    def calc_pos(self, x, y, width, height, xaxis=None, yaxis=None):
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

        if log_x:
            x = np.log(x)
        if log_y:
            y = np.log(y)

        x_pos = []
        y_pos = []

        if xaxis is not None:
            xaxis_start = (
                xaxis["domain"][0]
                * (width - self.layout["_margin"]["l"] - self.layout["_margin"]["r"])
                + self.layout["_margin"]["l"]
            )
            xaxis_end = (
                xaxis["domain"][-1]
                * (width - self.layout["_margin"]["l"] - self.layout["_margin"]["r"])
                + self.layout["_margin"]["l"]
            )

            x_min = xaxis["_range"][0]
            x_max = xaxis["_range"][1]
            x_pos = (x - x_min) / (x_max - x_min) * (
                xaxis_end - xaxis_start
            ) + xaxis_start

        if yaxis is not None:
            yaxis_start = (
                -(yaxis["domain"][0])
                * (height - self.layout["_margin"]["t"] - self.layout["_margin"]["b"])
                + height
                - self.layout["_margin"]["b"]
            )
            yaxis_end = (
                -(yaxis["domain"][-1])
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

    def set_trace_color(self, context, plot, index):
        if "marker" in plot and "color" in plot["marker"]:
            color = plot["marker"]["color"]
        else:
            color = self.layout["template"]["layout"]["colorway"][index]
        context.set_source_rgb(*parse_color(color))

    def plot(self, context, width, height):
        index = 0
        for plot in self.data:
            type = plot["type"]
            if not plot["visible"]:
                continue

            if "_visible" in plot and not plot["_visible"]:
                index += 1
                continue

            self.set_trace_color(context, plot, index)
            if type in ["scatter", "scattergl"]:
                self.plot_scatter(context, width, height, plot, index)
            elif type == "histogram":
                self.plot_histogram(context, width, height, plot, index)
            index += 1

    def plot_histogram(self, context, width, height, plot, index):
        for i in range(0, len(plot["y"])):
            x = [plot["x"][i], plot["x"][i], plot["x"][i + 1], plot["x"][i + 1]]
            y = [0, plot["y"][i], plot["y"][i], 0]

            xaxis, yaxis = self.get_axes(plot)

            x_pos, y_pos = self.calc_pos(x, y, width, height, xaxis, yaxis)
            context.new_path()

            for i in range(0, 4):
                context.line_to(x_pos[i], y_pos[i])

            context.close_path()
            context.fill()

    def get_axes(self, plot):
        xaxis = plot["xaxis"] if "xaxis" in plot else "x"
        yaxis = plot["yaxis"] if "yaxis" in plot else "y"
        xaxis = xaxis.replace("x", "xaxis")
        yaxis = yaxis.replace("y", "yaxis")

        xaxis = self.layout[xaxis] if xaxis in self.layout else {}
        yaxis = self.layout[yaxis] if yaxis in self.layout else {}

        return xaxis, yaxis

    def plot_scatter(self, context, width, height, plot, index):
        if "mode" in plot:
            mode = plot["mode"]
        elif len(plot["x"]) <= 20:
            mode = "lines+markers"
        else:
            mode = "lines"
        modes = mode.split("+")

        xaxis, yaxis = self.get_axes(plot)

        x_pos, y_pos = self.calc_pos(plot["x"], plot["y"], width, height, xaxis, yaxis)

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


class PlotlyGtk(Gtk.Overlay):
    def __init__(self, fig: go.Figure | dict):
        super().__init__()
        self.pushmargin = {}
        fig = fig.to_dict() if isinstance(fig, go.Figure) else fig

        self.data = fig["data"]

        self.layout = fig["layout"]
        if self.layout is None:
            self.layout = {}
        self.update_layout()
        fig["layout"] = self.layout
        fig["layout"]["_margin"] = dict(self.layout["margin"])

        self.prepare_data()
        fig["data"] = self.data
        self.fig = fig

        self.overlays = []

        self.connect(
            "get_child_position",
            lambda overlay, widget, allocation: widget.get_position(
                overlay, allocation
            ),
        )

        self.connect("realize", lambda _: self.update(self.fig))

    def update(self, fig):
        self.update_ranges()
        for overlay in self.overlays:
            self.remove_overlay(overlay)
        self.overlays = []
        self.draw_buttons()
        self.draw_legend()
        self.draw_titles()
        self.draw_annotations()
        self.set_child(_PlotlyGtk(fig))

    def update_ranges(self):
        axes = [k for k in self.layout if "axis" in k]
        for axis in axes:
            if "autorange" in self.layout[axis]:
                autorange = self.layout[axis]["autorange"]
            elif "range" in self.layout[axis] and len(self.layout[axis]["range"] == 2):
                autorange = False
            else:
                autorange = True

            axis_letter = axis[0 : axis.find("axis")]

            plots_on_axis = [
                plot
                for plot in self.data
                if f"{axis_letter}axis" in plot
                and plot[f"{axis_letter}axis"] == axis.replace("axis", "")
                and ("visible" not in plot or plot["visible"])
                and ("_visible" not in plot or plot["_visible"])
            ]
            if plots_on_axis == []:
                continue

            if autorange:
                _range = [
                    np.nanmin(
                        [
                            (
                                np.nanmin(plot[axis_letter])
                                if axis_letter in plot
                                else np.nan
                            )
                            for plot in plots_on_axis
                        ]
                    ),
                    np.nanmax(
                        [
                            (
                                np.nanmax(plot[axis_letter])
                                if axis_letter in plot
                                else np.nan
                            )
                            for plot in plots_on_axis
                        ]
                    ),
                ]
                if _range[0] == _range[-1]:
                    _range[0] = _range[0] - 1
                    _range[-1] = _range[1] + 1
                self.layout[axis]["_range"] = _range

        # Do matching
        matched_to_axes = set(
            [
                self.layout[axis]["matches"]
                for axis in axes
                if "matches" in self.layout[axis]
            ]
        )
        match_groups = {
            axis: [
                ax
                for ax in axes
                if ax == axis[0] + "axis" + axis[1:]
                or ("matches" in self.layout[ax] and self.layout[ax]["matches"] == axis)
            ]
            for axis in matched_to_axes
        }
        for match_group in match_groups.values():
            _ranges = [self.layout[axis]["_range"] for axis in match_group]
            _range = [min(r[0] for r in _ranges), max(r[-1] for r in _ranges)]
            for axis in match_group:
                self.layout[axis]["_range"] = _range

        for axis in axes:
            if "_range" not in self.layout[axis]:
                continue
            if "type" in self.layout[axis] and self.layout[axis]["type"] == "log":
                self.layout[axis]["_range"] = np.log(self.layout[axis]["_range"])
            else:
                range_length = (
                    self.layout[axis]["_range"][-1] - self.layout[axis]["_range"][0]
                )
                range_addon = range_length * 0.125 / 2
                self.layout[axis]["_range"] = [
                    self.layout[axis]["_range"][0] - range_addon,
                    self.layout[axis]["_range"][-1] + range_addon,
                ]
            if "_ticksobject" not in self.layout[axis]:
                self.layout[axis]["_ticksobject"] = Ticks(
                    self.layout,
                    axis,
                    0,
                )
                self.layout[axis]["_ticksobject"].calculate()

    def prepare_data(self):
        for plot in self.data:
            plot["x"] = [
                (
                    x.replace(tzinfo=timezone.utc).timestamp()
                    if isinstance(x, datetime.datetime)
                    else x
                )
                for x in plot["x"]
            ]
        plots = []
        for plot in self.data:
            if plot["type"] in ["scatter", "scattergl"]:
                defaults = dict(
                    visible=True,
                    showlegend=True,
                    legend="legend",
                    legendrank=1000,
                    legendgroup="",
                    legendgrouptitle=dict(),
                    opacity=1,
                    zorder=0,
                    text="",
                    textposition="middle center",
                    texttemplate="",
                    hovertext="",
                    hoverinfo="all",
                    hovertemplate="",
                    xhoverformat="",
                    yhoverformat="",
                    xaxis="x",
                    yaxis="y",
                    marker=dict(
                        angle=0,
                        angleref="up",
                        autocolorscale=True,
                        cauto=True,
                        colorbar=dict(),
                        line=dict(
                            autocolorscale=True,
                            cauto=True,
                        ),
                        size=6,
                        sizemin=0,
                        sizemode="diameter",
                        sizeref=1,
                        standoff=0,
                        symbol="circle",
                    ),
                    line=dict(
                        backoff="auto",
                        dash="solid",
                        shape="linear",
                        simplify=True,
                        smoothing=1,
                        width=2,
                    ),
                    textfont=dict(),
                )
                plot = update_dict(defaults, plot)
            elif plot["type"] == "histogram":
                defaults = dict(xaxis="x", yaxis="y", visible=True)
                plot = update_dict(defaults, plot)
                self.bin_histogram(plot)
            else:
                raise NotImplementedError(f"{plot["type"]} not yet implemented")
            plots.append(plot)
        self.data = plots

    def bin_histogram(self, plot):
        if "binned" not in plot or not plot["binned"]:
            n_samples = len(plot["x"])
            n_bins = np.sqrt(n_samples)
            bin_width = (np.nanmax(plot["x"]) - np.nanmin(plot["x"])) / n_bins
            bin_width = round_sf(bin_width, 1)
            bin_start = bin_width * np.floor(np.nanmin(plot["x"]) / bin_width)
            bins = np.arange(bin_start, np.nanmax(plot["x"]) + bin_width, bin_width)

            counts = pd.cut(plot["x"], bins, right=False).value_counts().to_list()
            plot["x"] = bins
            plot["y"] = counts
            plot["binned"] = True

    def automargin(self, *args):
        for pushmargin in self.pushmargin.values():
            left = False
            right = False
            top = False
            bottom = False

            padding = 12
            approximate_padding = 30
            width = self.get_width()
            height = self.get_height()

            if pushmargin["l"] < 0:
                left = True
            if pushmargin["r"] > 1:
                right = True
            if pushmargin["t"] < 0:
                top = True
            if pushmargin["b"] > 1:
                bottom = True

            # TODO reimplement to search both margins together
            # >> m.ml
            # ans = (sym)
            #
            #   -pad⋅x₁ - pad⋅x₂ + width⋅x₁ - x₁⋅xr - x₂⋅xl
            #   ───────────────────────────────────────────
            #                     x₁ - x₂
            #
            # >> m.mr
            # ans = (sym)
            #
            #   pad⋅x₁ + pad⋅x₂ - 2⋅pad - width⋅x₂ + width + x₁⋅xr + x₂⋅xl - xl - xr
            #   ────────────────────────────────────────────────────────────────────
            #                                 x₁ - x₂

            if left:
                if "x" in pushmargin and "xl" in pushmargin:
                    new = (
                        pushmargin["x"] * (width - self.layout["margin"]["r"])
                        - padding
                        - pushmargin["xl"]
                    ) / (pushmargin["x"] - 1)
                else:
                    new = (
                        approximate_padding
                        - (width - self.layout["margin"]["r"]) * pushmargin["l"]
                    ) / (1 - pushmargin["l"])
                self.layout["_margin"]["l"] = max(self.layout["_margin"]["l"], new)
            if right:
                if "x" in pushmargin and "xr" in pushmargin:
                    new = (
                        (pushmargin["x"] - 1) * (width - self.layout["margin"]["l"])
                        + padding
                        + pushmargin["xr"]
                    ) / pushmargin["x"]
                else:
                    new = (
                        approximate_padding
                        + (width - self.layout["margin"]["l"]) * (pushmargin["r"] - 1)
                    ) / pushmargin["r"]
                self.layout["_margin"]["r"] = max(self.layout["_margin"]["r"], new)
            if top:
                if "y" in pushmargin and "yt" in pushmargin:
                    new = (
                        (pushmargin["y"] - 1) * (height - self.layout["margin"]["b"])
                        + padding
                        + pushmargin["yt"]
                    ) / pushmargin["y"]
                else:
                    raise NotImplementedError
            if bottom:
                if "y" in pushmargin and "yb" in pushmargin:
                    new = (
                        pushmargin["y"] * (height - self.layout["margin"]["t"])
                        - padding
                        - pushmargin["yb"]
                    ) / (pushmargin["y"] - 1)
                else:
                    raise NotImplementedError
        self.queue_allocate()

    def update_layout(self):
        xaxes = [
            trace["xaxis"].replace("x", "xaxis")
            for trace in self.data
            if "xaxis" in trace
        ]
        yaxes = [
            trace["yaxis"].replace("y", "yaxis")
            for trace in self.data
            if "yaxis" in trace
        ]
        xaxes.append("xaxis")
        yaxes.append("yaxis")
        xaxes = set(xaxes)
        yaxes = set(yaxes)

        template = self.layout["template"]["layout"]
        defaults = dict(
            font=dict(
                color="#444",
                family='"Open Sans", verdana, arial, sans-serif',
                size=12,
                style="normal",
                variant="normal",
                weight="normal",
            ),
            legend=dict(
                bordercolor="#444",
                borderwidth=0,
                entrywidth=0,
                entrywidthmode="pixels",
                font=dict(
                    color="#444",
                    family='"Open Sans", verdana, arial, sans-serif',
                    size=12,
                    style="normal",
                    variant="normal",
                    weight="normal",
                ),
                groupclick="togglegroup",
                grouptitlefont=dict(
                    color="#444",
                    family='"Open Sans", verdana, arial, sans-serif',
                    size=12,
                    style="normal",
                    variant="normal",
                    weight="normal",
                ),
                indentation=0,
                itemclick="toggle",
                itemdoubleclick="toggleothers",
                itemsizing="trace",
                itemwidth=30,
                orientation="v",
                title=dict(
                    font=dict(
                        color="#444",
                        family='"Open Sans", verdana, arial, sans-serif',
                        size=12,
                        style="normal",
                        variant="normal",
                        weight="normal",
                    ),
                    text="",
                ),
                tracegroupgap=10,
                traceorder="",
                valign="middle",
                visible=True,
                xanchor="left",
                xref="paper",
                yanchor="auto",
                yref="paper",
            ),
            margin=dict(autoexpand=True, t=100, l=80, r=80, b=80),
            xaxis=dict(
                automargin=True,
                autorange=True,
                autotickangles=[0, 30, 90],
                color="#444",
                domain=[0, 1],
                gridcolor="#eee",
                griddash="solid",
                gridwidth=1,
                hoverformt="",
                layer="above traces",
                linecolor="#444",
                linewidth=1,
                minexponent=3,
                minor=dict(),
                mirror=False,
                nticks=0,
                position=0,
                rangemode="normal",
                showgrid=True,
                showline=True,
                showticklabels=True,
                showtickprefix="all",
                showticksuffix="all",
                side="bottom",
                tickangle="auto",
                tickfont=dict(style="normal", variant="normal", weight="normal"),
                tickformat="",
                ticklabelmode="instant",
                ticklabelposition="outside",
                ticklabelstep=1,
                ticklen=5,
                tickprefix="",
                ticks="",
                tickson="labels",
                ticksuffix="",
                tickwidth=1,
                title=dict(
                    font=dict(style="normal", variant="normal", weight="normal")
                ),
                type="-",
                zerolinecolor="#444",
                zerolinewidth=1,
            ),
            yaxis=dict(
                automargin=True,
                autorange=True,
                autotickangles=[0, 30, 90],
                color="#444",
                domain=[0, 1],
                gridcolor="#eee",
                griddash="solid",
                gridwidth=1,
                hoverformt="",
                layer="above traces",
                linecolor="#444",
                linewidth=1,
                minexponent=3,
                minor=dict(),
                mirror=False,
                nticks=0,
                position=0,
                rangemode="normal",
                showgrid=True,
                showline=True,
                showticklabels=True,
                showtickprefix="all",
                showticksuffix="all",
                side="left",
                tickangle="auto",
                tickfont=dict(style="normal", variant="normal", weight="normal"),
                tickformat="",
                ticklabelmode="instant",
                ticklabelposition="outside",
                ticklabelstep=1,
                ticklen=5,
                tickprefix="",
                ticks="",
                tickson="labels",
                ticksuffix="",
                tickwidth=1,
                title=dict(
                    font=dict(style="normal", variant="normal", weight="normal")
                ),
                type="-",
                zerolinecolor="#444",
                zerolinewidth=1,
            ),
        )
        for xaxis in xaxes:
            template[xaxis] = template["xaxis"]
            defaults[xaxis] = defaults["xaxis"]
        for yaxis in yaxes:
            template[yaxis] = template["yaxis"]
            defaults[yaxis] = defaults["yaxis"]
        self.layout = update_dict(template, self.layout)
        self.layout = update_dict(defaults, self.layout)

    def draw_buttons(self):
        if "updatemenus" not in self.layout:
            return
        for updatemenu in self.layout["updatemenus"]:
            overlay = UpdateMenu(self, updatemenu)
            self.overlays.append(overlay)
            self.add_overlay(overlay)

    def draw_legend(self):
        legend = self.layout["legend"]
        overlay = Legend(self, legend)
        self.overlays.append(overlay)
        self.add_overlay(overlay)

    def draw_annotations(self):
        if "annotations" not in self.layout:
            return
        for annotation in self.layout["annotations"]:
            overlay = Annotation(self, annotation)
            self.overlays.append(overlay)
            self.add_overlay(overlay)

    def draw_titles(self):
        axes = [k for k in self.layout if "axis" in k]
        for axis in axes:
            if (
                "title" not in self.layout[axis]
                or self.layout[axis]["title"] is False
                or "text" not in self.layout[axis]["title"]
            ):
                continue
            overlay = AxisTitle(self, self.layout[axis], axis_name=axis)
            self.overlays.append(overlay)
            self.add_overlay(overlay)
