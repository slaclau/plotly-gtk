import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from typing import TYPE_CHECKING

from gi.repository import Gdk, Gtk, Pango  # noqa: E402

from plotly_gtk.utils import parse_font, update_dict
from plotly_gtk.widgets.base import Base

if TYPE_CHECKING:
    from plotly_gtk.chart import PlotlyGtk

Spec = None | list["Spec"] | dict[str, "Spec"]


class AxisTitle(Base):
    def __init__(self, plot: "PlotlyGtk", axis: Spec, axis_name: str):
        super().__init__()
        axis_letter = axis_name[0 : axis_name.find("axis")]
        standoff = axis["title"]["standoff"]
        ticklen = axis["ticklen"] if axis["ticks"] == "outside" else 0
        context = self.get_pango_context()
        tickfont = update_dict(plot.layout["font"], axis["tickfont"])
        tickfont = parse_font(tickfont)
        metrics = context.get_metrics(tickfont)

        self.label = Gtk.Label(label=axis["title"]["text"])
        self.append(self.label)

        if axis_letter == "x":
            font_extra = (metrics.get_ascent() + metrics.get_descent()) / Pango.SCALE

            orientation = "h"
            x = (axis["domain"][0] + axis["domain"][-1]) / 2
            y = axis["position"]
            xanchor = "center"
            yanchor = "top" if axis["side"] == "bottom" else "bottom"
            xoffset = 0
            yoffset = (
                standoff + ticklen + font_extra
                if axis["side"] == "bottom"
                else -standoff - ticklen - font_extra
            )
            angle = 0
        elif axis_letter == "y":
            font_extra = 0
            layout = Pango.Layout(context)
            layout.set_font_description(tickfont)
            for tick in axis["_ticktext"]:
                layout.set_text(tick)
                font_extra = max(layout.get_pixel_size()[0], font_extra)

            orientation = "v"
            x = axis["position"]
            y = (axis["domain"][0] + axis["domain"][-1]) / 2
            xanchor = "right" if axis["side"] == "left" else "left"
            yanchor = "middle"
            _width = self.get_preferred_size()[-1].width
            _height = self.get_preferred_size()[-1].height

            x_size_error = (_height - _width) / 2
            xoffset = (
                -standoff - ticklen - font_extra - x_size_error
                if axis["side"] == "left"
                else standoff + ticklen + font_extra + x_size_error
            )
            yoffset = 0
            angle = 270 if axis["side"] == "left" else 90
            self.set_orientation(Gtk.Orientation.VERTICAL)
        else:
            return

        self.spec = dict(
            x=x, xanchor=xanchor, xoffset=xoffset, y=y, yanchor=yanchor, yoffset=yoffset
        )
        self.angle = angle

        font = axis["title"]["font"]
        defaults = plot.layout["font"]
        font = update_dict(defaults, font)
        font_description = parse_font(font, single_family=True).to_string()

        custom_css = Gtk.CssProvider()
        custom_css.load_from_string(
            f"""
            .plotly-{axis_name}-title label {{
                color: {font["color"]};
                font-family: {font["family"]};
                font-size: {font["size"]}px;
                font-style: {font["style"]};
                font-variant: {font["variant"]};
                font-weight: {font["weight"]};
            }}
            .vertical-90-text {{
                transform: rotate(90deg);
            }}
            .vertical-270-text {{
                transform: rotate(270deg);
            }}
            """
        )
        Gtk.StyleContext().add_provider_for_display(
            Gdk.Display().get_default(),
            custom_css,
            Gtk.STYLE_PROVIDER_PRIORITY_USER,
        )

        self.add_css_class(f"plotly-{axis_name}-title")
        if angle in [90, 270]:
            self.add_css_class(f"vertical-{angle}-text")
