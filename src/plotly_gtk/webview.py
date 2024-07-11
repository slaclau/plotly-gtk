from tempfile import NamedTemporaryFile

import gi
from plotly import graph_objects as go

gi.require_version("WebKit", "6.0")
from gi.repository import WebKit  # noqa: E402


class FigureWebView(WebKit.WebView):
    def __init__(self, fig, conf=None):
        super().__init__()
        self.fig = fig if isinstance(fig, go.Figure) else go.Figure(fig)
        self.conf = conf
        self.connect("realize", lambda _: self.refresh())

    def refresh(self, fig=None):
        if fig is not None:
            self.fig = fig
        file = NamedTemporaryFile(mode="a")
        config = {"scrollZoom": True, "displaylogo": False}
        if self.conf is not None:
            for key in self.conf:
                config[key] = self.conf[key]
        with open(file.name, "w") as f:
            self.fig.write_html(f, config=config)
        with open(file.name, "r") as f:
            self.load_html(f.read())
