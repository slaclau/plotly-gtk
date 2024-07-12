import random

import gi
import numpy as np

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from typing import TYPE_CHECKING

from gi.repository import Gdk, Gtk, Pango  # noqa: E402

from plotly_gtk.utils import parse_font, update_dict
from plotly_gtk.widgets.base import Base

if TYPE_CHECKING:
    from plotly_gtk.chart import PlotlyGtk

Spec = None | list["Spec"] | dict[str, "Spec"]


class Annotation(Base):
    def __init__(self, plot: "PlotlyGtk", annotation: Spec):
        super().__init__()

        self.label = Gtk.Label(label=annotation["text"])
        self.append(self.label)

        self.spec = annotation

        font = annotation["font"]
        defaults = plot.layout["font"]
        font = update_dict(defaults, font)

        if "textangle" in annotation:
            angle = annotation["textangle"]
        else:
            angle = 0

        width = self.get_preferred_size()[-1].width
        height = self.get_preferred_size()[-1].height
        baseline_offset = height - self.measure(Gtk.Orientation.VERTICAL, -1)[-1]
        xoffset = (
            width * (1 - np.cos(np.deg2rad(angle))) / 2
            - (height + 2 * baseline_offset) * np.sin(np.deg2rad(angle)) / 2
        )
        if annotation["xanchor"] == "left":
            annotation["xoffset"] = -xoffset
        elif annotation["xanchor"] == "right":
            annotation["xoffset"] = xoffset

        custom_css = Gtk.CssProvider()
        index = random.random()
        custom_css.load_from_string(
            f"""
            .plotly-annotation label {{
                color: {font["color"]};
                font-family: {font["family"]};
                font-size: {font["size"]}px;
                font-style: {font["style"]};
                font-variant: {font["variant"]};
                font-weight: {font["weight"]};
            }}
            .rotated-{angle}-text {{
                transform: rotate({angle}deg);
            }}
            """
        )
        Gtk.StyleContext().add_provider_for_display(
            Gdk.Display().get_default(),
            custom_css,
            Gtk.STYLE_PROVIDER_PRIORITY_USER,
        )

        self.add_css_class(f"plotly-annotation")
        self.add_css_class(f"rotated-{angle}-text")
