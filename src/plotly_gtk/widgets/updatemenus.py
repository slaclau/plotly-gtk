import gi

gi.require_version("Gdk", "4.0")
gi.require_version("Gtk", "4.0")
from typing import TYPE_CHECKING

import numpy as np
from gi.repository import Gdk, Gtk  # noqa: E402

from plotly_gtk.utils import update_dict
from plotly_gtk.widgets.base import Base

if TYPE_CHECKING:
    from plotly_gtk.chart import PlotlyGtk


class UpdateMenu(Base):
    def __init__(self, plot: "PlotlyGtk", _updatemenu: dict):
        super().__init__()
        default = dict(
            active=0,
            bgcolor="transparent",
            bordercolor="#BEC8D9",
            borderwidth=1,
            direction="down",
            font=plot.layout["font"],
            showactive=True,
            type="dropdown",
            x=-0.05,
            xanchor="right",
            y=1,
            yanchor="top",
        )
        updatemenu = update_dict(default, _updatemenu)
        self.spec = updatemenu

        if updatemenu["direction"] in ["up", "down"]:
            self.set_orientation(Gtk.Orientation.VERTICAL)

        buttons = updatemenu["buttons"]

        font = updatemenu["font"]
        custom_css = Gtk.CssProvider()
        custom_css.load_from_string(
            f"""
            .plotly-button button {{
                background-color: {updatemenu["bgcolor"]};
                border: {updatemenu["borderwidth"]}px solid {updatemenu["bordercolor"]};
                box-shadow: none;
            }}
            .plotly-button label {{
                color: {updatemenu["font"]["color"]};
                font-family: {font["family"]};
                font-size: {font["size"]}px;
                font-style: {font["style"]};
                font-variant: {font["variant"]};
                font-weight: {font["weight"]};
            }}
            """
        )
        Gtk.StyleContext().add_provider_for_display(
            Gdk.Display().get_default(),
            custom_css,
            Gtk.STYLE_PROVIDER_PRIORITY_USER,
        )

        self.add_css_class("plotly-button")

        def on_button_selected(button):
            args = button.button["args"]
            if button.button["method"] == "update":
                for arg in args:
                    plot.layout.update(arg)
                    for k, v in arg.items():
                        if isinstance(v, list | np.ndarray) and len(v) == len(
                            plot.data
                        ):
                            for trace, val in zip(plot.data, v):
                                trace[k] = val
                _updatemenu["active"] = buttons.index(button.button)
                plot.update(dict(data=plot.data, layout=plot.layout))

        if updatemenu["type"] == "dropdown":
            _buttons = []

            def top_button_clicked(button):
                if button == top_button:
                    top_button.open = not top_button.open
                for _button in _buttons:
                    _button.set_visible(button == top_button and top_button.open)

            top_button = Gtk.Button(label=buttons[updatemenu["active"]]["label"])
            top_button.get_child().set_halign(Gtk.Align.START)
            top_button.open = False
            top_button.connect("clicked", top_button_clicked)
            self.append(top_button)

            width = 0

            for button in buttons:
                _button = Gtk.Button(label=button["label"], visible=True)
                _buttons.append(_button)
                _button.get_child().set_halign(Gtk.Align.START)
                _button.button = button
                _button.connect("clicked", on_button_selected)
                _button.connect("clicked", top_button_clicked)
                width = max(
                    width,
                    _button.measure(Gtk.Orientation.HORIZONTAL, -1)[0],
                )
                _button.set_visible(False)
                self.append(_button)
            top_button.set_size_request(width, -1)

        elif updatemenu["type"] == "buttons":
            for button in buttons:
                _button = Gtk.Button(label=button["label"])
                _button.get_child().set_halign(Gtk.Align.START)
                _button.button = button
                _button.connect("clicked", on_button_selected)
                self.append(_button)
        else:
            raise ValueError(f"Unknown updatemenu.type: {updatemenu["type"]}")
