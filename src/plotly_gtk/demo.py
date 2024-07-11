import gi
import plotly.express as px

from plotly_gtk.chart import PlotlyGtk
from plotly_gtk.webview import FigureWebView

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gtk  # noqa: E402


def get_test_figure(index):
    if index == 1:
        df = px.data.iris()
        fig = px.scatter(df, x="sepal_width", y="sepal_length")
        return fig


def test(app):
    window = Adw.Window(title="Plotly GTK test", application=app)
    paned = Gtk.Paned()
    window.set_content(paned)

    fig = get_test_figure(1)

    webview = FigureWebView(fig)
    webview.set_hexpand(True)
    webview.set_vexpand(True)

    paned.set_start_child(webview)
    paned.set_end_child(PlotlyGtk(fig))
    window.present()
    webview.refresh()


def standalone():
    app = Adw.Application(application_id="io.github.slaclau.plotly_gtk.test")
    app.connect("activate", test)
    app.run()


if __name__ == "__main__":
    standalone()
