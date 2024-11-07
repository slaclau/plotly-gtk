# pylint: disable=all
import gi
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
multiple_axes_demos = [
    "two_y_axes",
    "multiple_y_axes_subplots",
    "multiple_axes",
    "autoshift",
    "shift_by_pixels",
    #    "syncticks",
]

demos = {
    "Scatter": scatter_demos,
    "log": log_demos,
    "Multiple axes": multiple_axes_demos,
}


def get_test_figure(reference):
    if reference in scatter_demos:
        return _get_scatter_test_figure(reference)
    if reference in log_demos:
        return _get_log_test_figure(reference)
    if reference in multiple_axes_demos:
        return _get_multiple_axes_test_figure(reference)


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


def _get_multiple_axes_test_figure(reference):
    if reference == "two_y_axes":
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Scatter(x=[1, 2, 3], y=[40, 50, 60], name="yaxis data"),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=[2, 3, 4], y=[4, 5, 6], name="yaxis2 data"),
            secondary_y=True,
        )

        # Add figure title
        fig.update_layout(title_text="Double Y Axis Example")

        # Set x-axis title
        fig.update_xaxes(title_text="xaxis title")

        # Set y-axes titles
        fig.update_yaxes(title_text="<b>primary</b> yaxis title", secondary_y=False)
        fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)
    elif reference == "multiple_y_axes_subplots":
        fig = make_subplots(
            rows=2,
            cols=2,
            specs=[
                [{"secondary_y": True}, {"secondary_y": True}],
                [{"secondary_y": True}, {"secondary_y": True}],
            ],
        )

        # Top left
        fig.add_trace(
            go.Scatter(x=[1, 2, 3], y=[2, 52, 62], name="yaxis data"),
            row=1,
            col=1,
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=[1, 2, 3], y=[40, 50, 60], name="yaxis2 data"),
            row=1,
            col=1,
            secondary_y=True,
        )

        # Top right
        fig.add_trace(
            go.Scatter(x=[1, 2, 3], y=[2, 52, 62], name="yaxis3 data"),
            row=1,
            col=2,
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=[1, 2, 3], y=[40, 50, 60], name="yaxis4 data"),
            row=1,
            col=2,
            secondary_y=True,
        )

        # Bottom left
        fig.add_trace(
            go.Scatter(x=[1, 2, 3], y=[2, 52, 62], name="yaxis5 data"),
            row=2,
            col=1,
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=[1, 2, 3], y=[40, 50, 60], name="yaxis6 data"),
            row=2,
            col=1,
            secondary_y=True,
        )

        # Bottom right
        fig.add_trace(
            go.Scatter(x=[1, 2, 3], y=[2, 52, 62], name="yaxis7 data"),
            row=2,
            col=2,
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=[1, 2, 3], y=[40, 50, 60], name="yaxis8 data"),
            row=2,
            col=2,
            secondary_y=True,
        )
    elif reference == "multiple_axes":
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6], name="yaxis1 data"))

        fig.add_trace(
            go.Scatter(x=[2, 3, 4], y=[40, 50, 60], name="yaxis2 data", yaxis="y2")
        )

        fig.add_trace(
            go.Scatter(
                x=[4, 5, 6], y=[40000, 50000, 60000], name="yaxis3 data", yaxis="y3"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[5, 6, 7], y=[400000, 500000, 600000], name="yaxis4 data", yaxis="y4"
            )
        )

        # Create axis objects
        fig.update_layout(
            xaxis=dict(domain=[0.3, 0.7]),
            yaxis=dict(
                title=dict(text="yaxis title", font=dict(color="#1f77b4")),
                tickfont=dict(color="#1f77b4"),
            ),
            yaxis2=dict(
                title=dict(text="yaxis2 title", font=dict(color="#ff7f0e")),
                tickfont=dict(color="#ff7f0e"),
                anchor="free",
                overlaying="y",
                side="left",
                position=0.15,
            ),
            yaxis3=dict(
                title=dict(text="yaxis3 title", font=dict(color="#d62728")),
                tickfont=dict(color="#d62728"),
                anchor="x",
                overlaying="y",
                side="right",
            ),
            yaxis4=dict(
                title=dict(text="yaxis4 title", font=dict(color="#9467bd")),
                tickfont=dict(color="#9467bd"),
                anchor="free",
                overlaying="y",
                side="right",
                position=0.85,
            ),
        )

        # Update layout properties
        fig.update_layout(
            title_text="multiple y-axes example",
            width=800,
        )
    elif reference == "autoshift":
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6], name="yaxis data"))

        fig.add_trace(
            go.Scatter(x=[2, 3, 4], y=[40, 50, 60], name="yaxis2 data", yaxis="y2")
        )

        fig.add_trace(
            go.Scatter(
                x=[4, 5, 6], y=[1000, 2000, 3000], name="yaxis3 data", yaxis="y3"
            )
        )

        fig.add_trace(
            go.Scatter(x=[3, 4, 5], y=[400, 500, 600], name="yaxis4 data", yaxis="y4")
        )

        fig.update_layout(
            xaxis=dict(domain=[0.25, 0.75]),
            yaxis=dict(
                title="yaxis title",
            ),
            yaxis2=dict(
                title="yaxis2 title",
                overlaying="y",
                side="right",
            ),
            yaxis3=dict(
                title="yaxis3 title", anchor="free", overlaying="y", autoshift=True
            ),
            yaxis4=dict(
                title="yaxis4 title",
                anchor="free",
                overlaying="y",
                autoshift=True,
            ),
        )

        fig.update_layout(
            title_text="Shifting y-axes with autoshift",
        )
    elif reference == "shift_by_pixels":
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6], name="yaxis data"))

        fig.add_trace(
            go.Scatter(x=[2, 3, 4], y=[40, 50, 60], name="yaxis2 data", yaxis="y2")
        )

        fig.add_trace(
            go.Scatter(
                x=[4, 5, 6], y=[1000, 2000, 3000], name="yaxis3 data", yaxis="y3"
            )
        )

        fig.add_trace(
            go.Scatter(x=[3, 4, 5], y=[400, 500, 600], name="yaxis4 data", yaxis="y4")
        )

        fig.update_layout(
            xaxis=dict(domain=[0.25, 0.75]),
            yaxis=dict(
                title="yaxis title",
            ),
            yaxis2=dict(
                title="yaxis2 title",
                overlaying="y",
                side="right",
            ),
            yaxis3=dict(
                title="yaxis3 title", anchor="free", overlaying="y", autoshift=True
            ),
            yaxis4=dict(
                title="yaxis4 title",
                anchor="free",
                overlaying="y",
                autoshift=True,
                shift=-100,
            ),
        )

        fig.update_layout(
            title_text="Shifting y-axes by a specific number of pixels",
        )
    else:
        return
    return fig


def test(app):
    window = Adw.Window(title="Plotly GTK test", application=app)
    paned = Gtk.Paned()
    window.set_content(paned)

    fig = get_test_figure("multiple_y_axes_subplots")
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
