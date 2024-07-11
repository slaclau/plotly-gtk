import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from typing import TYPE_CHECKING

from gi.repository import Gdk, Gtk  # noqa: E402

if TYPE_CHECKING:
    from plotly_gtk.chart import PlotlyGtk


class Base(Gtk.Box):
    def __init__(self):
        super().__init__(
            vexpand=False,
            hexpand=False,
            valign=Gtk.Align.CENTER,
            halign=Gtk.Align.CENTER,
            margin_start=0,
            margin_end=0,
            margin_top=0,
            margin_bottom=0,
        )

    def get_position(self, plot: "PlotlyGtk", allocation: Gdk.Rectangle) -> bool:
        content_width = plot.get_width()
        content_height = plot.get_height()

        margin = plot.layout["margin"]
        _margin = plot.layout["_margin"]
        preferred_size = self.get_preferred_size()[-1]
        width = preferred_size.width
        height = preferred_size.height

        _x = _margin["l"] + self.spec["x"] * (
            content_width - _margin["l"] - _margin["r"]
        )
        _y = _margin["t"] + (1 - self.spec["y"]) * (
            content_height - _margin["t"] - _margin["b"]
        )

        if "xref" in self.spec:
            if self.spec["xref"] == "container":
                _x = self.spec["x"] * content_width
            elif self.spec["xref"] == "paper":
                pass
            else:
                raise ValueError(f"Unknown xref: {self.spec["xref"]}")
        if "yref" in self.spec:
            if self.spec["yref"] == "container":
                _y = self.spec["y"] * content_width
            elif self.spec["yref"] == "paper":
                pass
            else:
                raise ValueError(f"Unknown yref: {self.spec["yref"]}")

        if "xoffset" in self.spec:
            _x = _x + self.spec["xoffset"]
        if "yoffset" in self.spec:
            _y = _y + self.spec["yoffset"]

        if self.spec["xanchor"] == "center":
            _x = _x - width / 2
        elif self.spec["xanchor"] == "right":
            _x = _x - width

        if self.spec["yanchor"] == "middle":
            _y = _y - height / 2
        elif self.spec["yanchor"] == "bottom":
            _y = _y - height

        x = margin["l"] + self.spec["x"] * (content_width - margin["l"] - margin["r"])
        y = margin["t"] + (1 - self.spec["y"]) * (
            content_height - margin["t"] - margin["b"]
        )
        if "xoffset" in self.spec:
            x = x + self.spec["xoffset"]
        if "yoffset" in self.spec:
            y = y + self.spec["yoffset"]

        if self.spec["xanchor"] == "center":
            x = x - width / 2
        elif self.spec["xanchor"] == "right":
            x = x - width

        if self.spec["yanchor"] == "middle":
            y = y - height / 2
        elif self.spec["yanchor"] == "bottom":
            y = y - height

        allocation.x = _x
        allocation.y = _y

        allocation.width = width
        allocation.height = height

        plot.pushmargin[self] = dict(
            l=(x - margin["l"]) / (content_width - margin["l"] - margin["r"]),
            r=(x + width - margin["l"]) / (content_width - margin["l"] - margin["r"]),
            t=(y - margin["t"]) / (content_height - margin["t"] - margin["b"]),
            b=(y + height - margin["t"]) / (content_height - margin["t"] - margin["b"]),
        )
        if not "xref" in self.spec or self.spec["xref"] == "paper":
            plot.pushmargin[self]["x"] = self.spec["x"]
            plot.pushmargin[self]["xl"] = (
                0
                if self.spec["xanchor"] == "left"
                else width if self.spec["xanchor"] == "right" else width / 2
            )
            plot.pushmargin[self]["xr"] = (
                0
                if self.spec["xanchor"] == "right"
                else width if self.spec["xanchor"] == "left" else width / 2
            )
        if not "yref" in self.spec or self.spec["yref"] == "paper":
            plot.pushmargin[self]["y"] = self.spec["y"]
            plot.pushmargin[self]["yt"] = (
                0
                if self.spec["yanchor"] == "top"
                else height if self.spec["yanchor"] == "bottom" else height / 2
            )
            plot.pushmargin[self]["yb"] = (
                0
                if self.spec["yanchor"] == "bottom"
                else height if self.spec["yanchor"] == "top" else height / 2
            )
        if (
            "xoffset" in self.spec
            and "xl" in plot.pushmargin[self]
            and "xr" in plot.pushmargin[self]
        ):
            plot.pushmargin[self]["xl"] = (
                plot.pushmargin[self]["xl"] - self.spec["xoffset"]
            )
            plot.pushmargin[self]["xr"] = (
                plot.pushmargin[self]["xr"] + self.spec["xoffset"]
            )
        if (
            "yoffset" in self.spec
            and "yt" in plot.pushmargin[self]
            and "yb" in plot.pushmargin[self]
        ):
            plot.pushmargin[self]["yt"] = (
                plot.pushmargin[self]["yt"] + self.spec["yoffset"]
            )
            plot.pushmargin[self]["yb"] = (
                plot.pushmargin[self]["yb"] - self.spec["yoffset"]
            )
        return True
