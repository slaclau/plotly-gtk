import os
import pathlib
import subprocess
import sys
import threading
import time
from itertools import chain

import gi
import numpy as np
from PIL import Image
from selenium import webdriver

import pytest

os.environ["BROADWAY_DISPLAY"] = ":5"
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk

Gdk.set_allowed_backends("broadway,*")
gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
from gi.repository import Adw, GLib, Gtk

from plotly_gtk.chart import PlotlyGtk
from plotly_gtk.demo import demos, get_test_figure
from plotly_gtk.webview import FigureWebView


@pytest.fixture
def browser():
    optionset = webdriver.ChromeOptions()
    optionset.add_argument("headless")
    browser = webdriver.Chrome(options=optionset)
    browser.set_window_size(800, 600)
    yield browser
    browser.close()


class DemoWindow(Adw.ApplicationWindow):
    def __init__(self, fig: dict, **kwargs):
        super().__init__(**kwargs)
        plot = PlotlyGtk(fig)
        self.set_content(plot)
        self.set_size_request(800, 600)


class DemoApplication(Adw.Application):
    def __init__(self, demo: str, browser=None, **kwargs):
        super().__init__(**kwargs)
        self.demo = demo
        self.browser = browser
        self.window = None
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        if app.window is not None:
            app.window.close()
        app.window = DemoWindow(get_test_figure(app.demo), application=app)
        app.window.maximize()
        app.window.present()

        def screenshot():
            def end():
                app.window.destroy()

            if app.browser is None:
                time.sleep(10)
            else:
                directory = (pathlib.Path(__file__).parent / "results").resolve()

                app.browser.get("http://127.0.0.1:8085/")
                time.sleep(2)
                app.browser.save_screenshot(directory / f"{app.demo}.png")
            GLib.idle_add(end)
            return False

        thread = threading.Thread(target=screenshot, daemon=True)
        thread.start()


@pytest.mark.parametrize("demo", chain(*demos.values()))
def test_demo(demo, browser, capsys):
    app = DemoApplication(
        demo, browser, application_id=f"io.github.slaclau.plotly_gtk.{demo}"
    )

    app.run()
    directory = (pathlib.Path(__file__).parent / "results").resolve()
    img = Image.open(directory / f"{demo}.png")
    assert np.mean(img.convert("RGB").getdata()) < 0xFF
    out, err = capsys.readouterr()
    print(out)
    assert not err


if __name__ == "__main__":
    if len(sys.argv) > 1:
        demos = [sys.argv[1]]
    for demo in demos:
        app = DemoApplication(
            demo, browser=None, application_id="io.github.slaclau.plotly_gtk.test"
        )

        app.run()
