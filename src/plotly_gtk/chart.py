"""This module contains a class for rendering a plotly
:class:`plotly.graph_objects.Figure` using GTK."""

import datetime
import numbers
from datetime import timezone
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from plotly_gtk._chart import _PlotlyGtk
from plotly_gtk.utils import *  # pylint: disable=wildcard-import, unused-wildcard-import
from plotly_gtk.utils.ticks import Ticks
from plotly_gtk.widgets import *  # pylint: disable=wildcard-import

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from gi.repository import (  # pylint: disable=wrong-import-order,wrong-import-position
    Gtk,
)

if TYPE_CHECKING:
    from plotly import graph_objects as go

try:
    from plotly import graph_objects as go
except NameError:
    print("plotly not available")


class PlotlyGtk(Gtk.Overlay):
    """Class for rendering plotly :class:`plotly.graph_objects.Figure`."""

    def __init__(self, fig: "go.Figure | dict"):
        super().__init__()
        self.pushmargin = {}
        try:
            fig = fig.to_dict() if isinstance(fig, go.Figure) else fig
        except NameError:
            pass

        self.data = fig["data"]

        self.layout = fig["layout"]
        if self.layout is None:
            self.layout = {}
        self._update_layout()
        fig["layout"] = self.layout
        fig["layout"]["_margin"] = dict(self.layout["margin"])

        self._prepare_data()
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

    def update(self, fig: dict[str, plotly_types.Data | plotly_types.Layout]):
        """Update the view.

        Parameters
        ----------
        fig: dict[str, plotly_types.Data | plotly_types.Layout]
            A dictionary representing a plotly figure
        """
        self._update_ranges()
        for overlay in self.overlays:
            self.remove_overlay(overlay)
        self.overlays = []
        self._draw_buttons()
        self._draw_legend()
        self._draw_titles()
        self._draw_annotations()
        self.set_child(_PlotlyGtk(fig))

    def _update_ranges(self):
        axes = [k for k in self.layout if "axis" in k]
        for axis in axes:
            if "autorange" in self.layout[axis]:
                autorange = self.layout[axis]["autorange"]
            if "range" in self.layout[axis] and len(self.layout[axis]["range"]) == 2:
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
            else:
                if self.layout[axis]["type"] == "log":
                    self.layout[axis]["_range"] = np.array(
                        [
                            10 ** self.layout[axis]["range"][0],
                            10 ** self.layout[axis]["range"][-1],
                        ]
                    )
                else:
                    self.layout[axis]["_range"] = np.array(self.layout[axis]["range"])

        # Do matching
        matched_to_axes = {
            self.layout[axis]["matches"]
            for axis in axes
            if "matches" in self.layout[axis]
        }
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
            if self.layout[axis]["_type"] == "log":
                self.layout[axis]["_range"] = np.log10(self.layout[axis]["_range"])
                range_length = (
                    self.layout[axis]["_range"][-1] - self.layout[axis]["_range"][0]
                )
                if (
                    "range" in self.layout[axis]
                    and len(self.layout[axis]["range"]) == 2
                ):
                    range_addon = range_length * 0.001
                else:
                    range_addon = range_length * 0.125 / 2
                self.layout[axis]["_range"] = [
                    self.layout[axis]["_range"][0] - range_addon,
                    self.layout[axis]["_range"][-1] + range_addon,
                ]
            else:
                range_length = (
                    self.layout[axis]["_range"][-1] - self.layout[axis]["_range"][0]
                )
                if (
                    "range" in self.layout[axis]
                    and len(self.layout[axis]["range"]) == 2
                ):
                    range_addon = range_length * 0.001
                else:
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
            else:
                self.layout[axis]["_ticksobject"].calculate()

    def _prepare_data(self):
        for plot in self.data:
            if self._detect_axis_type(plot["x"]) == "date":
                plot["x"] = np.array(plot["x"], dtype="datetime64")
                plot["x"] = pd.to_datetime(plot["x"])
                plot["x"] = [
                    x.replace(tzinfo=timezone.utc).timestamp() for x in plot["x"]
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
                self._bin_histogram(plot)
            else:
                raise NotImplementedError(f"{plot["type"]} not yet implemented")
            plots.append(plot)
        self.data = plots

    def _bin_histogram(self, plot):
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

    def automargin(self):
        """Calculate margin sizes.

        Raises
        ------
        NotImplementedError
            If unimplemented functionality is called for.
        """
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

            # TODO reimplement to search both margins together # pylint: disable=fixme
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

    def _update_layout(self):
        xaxes = {
            trace["xaxis"].replace("x", "xaxis")
            for trace in self.data
            if "xaxis" in trace
        }
        yaxes = {
            trace["yaxis"].replace("y", "yaxis")
            for trace in self.data
            if "yaxis" in trace
        }
        xaxes.add("xaxis")
        yaxes.add("yaxis")

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
            if xaxis not in self.layout:
                self.layout[xaxis] = {}
            if "type" not in self.layout[xaxis]:
                first_plot_on_axis = [
                    trace
                    for trace in self.data
                    if "xaxis" not in trace
                    or trace["xaxis"] == xaxis.replace("axis", "")
                ][0]
                self.layout[xaxis]["_type"] = (
                    self._detect_axis_type(first_plot_on_axis["x"])
                    if "x" in first_plot_on_axis
                    else "linear"
                )
            else:
                self.layout[xaxis]["_type"] = self.layout[xaxis]["type"]
            template[xaxis] = template["xaxis"]
            defaults[xaxis] = defaults["xaxis"]
        for yaxis in yaxes:
            if yaxis not in self.layout:
                self.layout[yaxis] = {}
            if "type" not in self.layout[yaxis]:
                first_plot_on_axis = [
                    trace
                    for trace in self.data
                    if "yaxis" not in trace
                    or trace["yaxis"] == yaxis.replace("axis", "")
                ][0]
                print(first_plot_on_axis)
                self.layout[yaxis]["_type"] = (
                    self._detect_axis_type(first_plot_on_axis["y"])
                    if "y" in first_plot_on_axis
                    else "linear"
                )
            else:
                self.layout[yaxis]["_type"] = self.layout[yaxis]["type"]
            template[yaxis] = template["yaxis"]
            defaults[yaxis] = defaults["yaxis"]
        self.layout = update_dict(template, self.layout)
        self.layout = update_dict(defaults, self.layout)

    @staticmethod
    def _detect_axis_type(data):
        if any(isinstance(i, list) or isinstance(i, np.ndarray) for i in data):
            return "multicategory"
        if not isinstance(data, np.ndarray):
            data = np.array(data)

        length = len(data)
        if length >= 1000:
            start = np.random.randint(0, length / 1000)
            index = np.arange(start, length, length / 1000).astype(np.int32)
            data = data[index]

        data = set(data)

        def to_type(d):
            try:
                d = np.datetime64(d)
                return "date"
            except ValueError:
                if isinstance(d, numbers.Number):
                    return "linear"
                else:
                    return "category"

        data_types = [to_type(d) for d in data]
        data_types = {d: data_types.count(d) for d in set(data_types)}
        if len(data_types) == 1:
            return list(data_types)[0]
        if "linear" not in data_types:
            if data_types["date"] > data_types["category"]:
                return "date"
            return "category"

        if "date" in data_types and data_types["date"] > 2 * data_types["linear"]:
            return "date"
        if (
            "category" in data_types
            and data_types["category"] > 2 * data_types["linear"]
        ):
            return "category"

        return "linear"

    def _draw_buttons(self):
        if "updatemenus" not in self.layout:
            return
        for updatemenu in self.layout["updatemenus"]:
            overlay = UpdateMenu(self, updatemenu)
            self.overlays.append(overlay)
            self.add_overlay(overlay)

    def _draw_legend(self):
        legend = self.layout["legend"]
        overlay = Legend(self, legend)
        self.overlays.append(overlay)
        self.add_overlay(overlay)

    def _draw_annotations(self):
        if "annotations" not in self.layout:
            return
        for annotation in self.layout["annotations"]:
            overlay = Annotation(self, annotation)
            self.overlays.append(overlay)
            self.add_overlay(overlay)

    def _draw_titles(self):
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
