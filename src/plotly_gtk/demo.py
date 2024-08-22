# pylint: disable=all
import gi
import numpy as np
import plotly.express as px

from plotly_gtk.chart import PlotlyGtk
from plotly_gtk.webview import FigureWebView

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gtk

scatter_demos = [
    "scatter_1",
    "scatter_2",
    "scatter_size_color_column",
    "scatter_facetting",
    "line_1",
    "line_2",
]
log_demos = ["log_1", "log_2"]

demos = {"Scatter": scatter_demos, "log": log_demos}


def get_test_figure(reference):
    if reference in scatter_demos:
        return _get_scatter_test_figure(reference)
    if reference in log_demos:
        return _get_log_test_figure(reference)


def _get_log_test_figure(reference):
    if reference == "log_1":
        df = px.data.gapminder().query("year == 2007")
        fig = px.scatter(
            df, x="gdpPercap", y="lifeExp", hover_name="country", log_x=True
        )
    elif reference == "log_2":
        df = px.data.gapminder().query("year == 2007")
        fig = px.scatter(
            df,
            x="gdpPercap",
            y="lifeExp",
            hover_name="country",
            log_x=True,
            range_x=[1, 100000],
            range_y=[0, 100],
        )
    return fig


def _get_scatter_test_figure(reference):
    if reference == "scatter_1":
        fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
    elif reference == "scatter_2":
        df = px.data.iris()
        fig = px.scatter(df, x="sepal_width", y="sepal_length")
    elif reference == "scatter_size_color_column":
        df = px.data.iris()
        fig = px.scatter(
            df,
            x="sepal_width",
            y="sepal_length",
            color="species",
            size="petal_length",
            hover_data=["petal_width"],
        )
    elif reference == "scatter_facetting":
        df = px.data.tips()
        fig = px.scatter(
            df,
            x="total_bill",
            y="tip",
            color="smoker",
            facet_col="sex",
            facet_row="time",
        )
    elif reference == "line_1":
        t = np.linspace(0, 2 * np.pi, 100)
        fig = px.line(x=t, y=np.cos(t), labels={"x": "t", "y": "cos(t)"})
    elif reference == "line_2":
        df = px.data.gapminder().query("continent == 'Oceania'")
        fig = px.line(df, x="year", y="lifeExp", color="country")
    return fig


def test(app):
    window = Adw.Window(title="Plotly GTK test", application=app)
    paned = Gtk.Paned()
    window.set_content(paned)

    fig = get_test_figure("log_2")
    print(fig)
    # print(fig["layout"]["template"])

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
