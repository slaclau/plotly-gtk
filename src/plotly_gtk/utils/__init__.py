"""This module provides utility classes and functions used by
:class:`plotly_gtk.chart.PlotlyGtk`."""

import collections
import typing

import gi
import numpy as np

from plotly_gtk.utils import plotly_types

if typing.TYPE_CHECKING:
    from plotly_gtk.utils.plotly_types import GenericType, get_type

gi.require_version("Gdk", "4.0")
from gi.repository import (  # pylint: disable=wrong-import-position, wrong-import-order
    Gdk,
    Pango,
    PangoCairo,
)


def update_dict(d: "GenericType", u: "GenericType") -> "GenericType":
    """Return a copy of :class:`dict` `d` recursively updated with values from :class:`dict` `u`.

    Parameters
    ------
    d: dict
        The dictionary to update
    u: dict
        The dictionary of new values

    Returns
    -------
    dict
        A copy of `d` updated with values from `u`

    """
    d = dict(d)
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def parse_color(color: str) -> tuple[float, float, float]:
    """
    Return the RGB components of a color provided as a string.

    Parameters
    ----------
    color: str

    Returns
    -------
    tuple[float,float, float]
        The red, green, and blue components

    Raises
    ------
    ValueError
        If Gdk cannot parse the color
    """
    rgba = Gdk.RGBA()
    if rgba.parse(color):
        return rgba.red, rgba.green, rgba.blue
    raise ValueError


def parse_font(
    font: dict[str, str | int], single_family: bool = False
) -> Pango.FontDescription:
    """
    Parse a dictionary of font parameters and return a :class:`gi.repository.Pango.FontDescription`.

    Parameters
    ----------
    font: dict[str, str|int]
        Must contain the following keys: family, style, variant, weight, and size

    single_family: bool
        If the returned :class:`gi.repository.Pango.FontDescription`
        should contain only one value for family

    Returns
    -------
    gi.repository.Pango.FontDescription
        The fields are set as provided in the input :class:`dict`.

    """
    font = f"{font["family"]} {font["style"]} {font["variant"]} {font["weight"]} {font["size"]}px"
    font_desc = Pango.FontDescription.from_string(font)
    if single_family:
        font_desc = (
            PangoCairo.FontMap.get_default()
            .load_font(PangoCairo.FontMap.get_default().create_context(), font_desc)
            .describe()
        )
    return font_desc


def get_cartesian_subplots(data: list[dict]) -> list[tuple[str, str]]:
    """
    Get the list of cartesian axes pairings with data plotted on them.

    Parameters
    ----------
    data: list[dict]
        A list of traces

    Returns
    -------
    list[tuple[str, str]]
        A list of tuples of the form ("xaxis([0-9]+)?", "yaxis([0-9]+)?")

    """
    return list(
        {
            (
                trace["xaxis"][0] + "axis" + trace["xaxis"][1:],
                trace["yaxis"][0] + "axis" + trace["yaxis"][1:],
            )
            for trace in data
        }
    )


def get_base_fig() -> dict:
    """
    Avoid importing plotly by creating a base figure dictionary.

    Returns
    -------
    dict
        The dictionary returned by plotly.graph_object.Figure().to_dict()
    """
    return {
        "data": [],
        "layout": {
            "template": {
                "data": {
                    "histogram2dcontour": [
                        {
                            "type": "histogram2dcontour",
                            "colorbar": {"outlinewidth": 0, "ticks": ""},
                            "colorscale": [
                                [0.0, "#0d0887"],
                                [0.1111111111111111, "#46039f"],
                                [0.2222222222222222, "#7201a8"],
                                [0.3333333333333333, "#9c179e"],
                                [0.4444444444444444, "#bd3786"],
                                [0.5555555555555556, "#d8576b"],
                                [0.6666666666666666, "#ed7953"],
                                [0.7777777777777778, "#fb9f3a"],
                                [0.8888888888888888, "#fdca26"],
                                [1.0, "#f0f921"],
                            ],
                        }
                    ],
                    "choropleth": [
                        {
                            "type": "choropleth",
                            "colorbar": {"outlinewidth": 0, "ticks": ""},
                        }
                    ],
                    "histogram2d": [
                        {
                            "type": "histogram2d",
                            "colorbar": {"outlinewidth": 0, "ticks": ""},
                            "colorscale": [
                                [0.0, "#0d0887"],
                                [0.1111111111111111, "#46039f"],
                                [0.2222222222222222, "#7201a8"],
                                [0.3333333333333333, "#9c179e"],
                                [0.4444444444444444, "#bd3786"],
                                [0.5555555555555556, "#d8576b"],
                                [0.6666666666666666, "#ed7953"],
                                [0.7777777777777778, "#fb9f3a"],
                                [0.8888888888888888, "#fdca26"],
                                [1.0, "#f0f921"],
                            ],
                        }
                    ],
                    "heatmap": [
                        {
                            "type": "heatmap",
                            "colorbar": {"outlinewidth": 0, "ticks": ""},
                            "colorscale": [
                                [0.0, "#0d0887"],
                                [0.1111111111111111, "#46039f"],
                                [0.2222222222222222, "#7201a8"],
                                [0.3333333333333333, "#9c179e"],
                                [0.4444444444444444, "#bd3786"],
                                [0.5555555555555556, "#d8576b"],
                                [0.6666666666666666, "#ed7953"],
                                [0.7777777777777778, "#fb9f3a"],
                                [0.8888888888888888, "#fdca26"],
                                [1.0, "#f0f921"],
                            ],
                        }
                    ],
                    "heatmapgl": [
                        {
                            "type": "heatmapgl",
                            "colorbar": {"outlinewidth": 0, "ticks": ""},
                            "colorscale": [
                                [0.0, "#0d0887"],
                                [0.1111111111111111, "#46039f"],
                                [0.2222222222222222, "#7201a8"],
                                [0.3333333333333333, "#9c179e"],
                                [0.4444444444444444, "#bd3786"],
                                [0.5555555555555556, "#d8576b"],
                                [0.6666666666666666, "#ed7953"],
                                [0.7777777777777778, "#fb9f3a"],
                                [0.8888888888888888, "#fdca26"],
                                [1.0, "#f0f921"],
                            ],
                        }
                    ],
                    "contourcarpet": [
                        {
                            "type": "contourcarpet",
                            "colorbar": {"outlinewidth": 0, "ticks": ""},
                        }
                    ],
                    "contour": [
                        {
                            "type": "contour",
                            "colorbar": {"outlinewidth": 0, "ticks": ""},
                            "colorscale": [
                                [0.0, "#0d0887"],
                                [0.1111111111111111, "#46039f"],
                                [0.2222222222222222, "#7201a8"],
                                [0.3333333333333333, "#9c179e"],
                                [0.4444444444444444, "#bd3786"],
                                [0.5555555555555556, "#d8576b"],
                                [0.6666666666666666, "#ed7953"],
                                [0.7777777777777778, "#fb9f3a"],
                                [0.8888888888888888, "#fdca26"],
                                [1.0, "#f0f921"],
                            ],
                        }
                    ],
                    "surface": [
                        {
                            "type": "surface",
                            "colorbar": {"outlinewidth": 0, "ticks": ""},
                            "colorscale": [
                                [0.0, "#0d0887"],
                                [0.1111111111111111, "#46039f"],
                                [0.2222222222222222, "#7201a8"],
                                [0.3333333333333333, "#9c179e"],
                                [0.4444444444444444, "#bd3786"],
                                [0.5555555555555556, "#d8576b"],
                                [0.6666666666666666, "#ed7953"],
                                [0.7777777777777778, "#fb9f3a"],
                                [0.8888888888888888, "#fdca26"],
                                [1.0, "#f0f921"],
                            ],
                        }
                    ],
                    "mesh3d": [
                        {"type": "mesh3d", "colorbar": {"outlinewidth": 0, "ticks": ""}}
                    ],
                    "scatter": [
                        {
                            "fillpattern": {
                                "fillmode": "overlay",
                                "size": 10,
                                "solidity": 0.2,
                            },
                            "type": "scatter",
                        }
                    ],
                    "parcoords": [
                        {
                            "type": "parcoords",
                            "line": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        }
                    ],
                    "scatterpolargl": [
                        {
                            "type": "scatterpolargl",
                            "marker": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        }
                    ],
                    "bar": [
                        {
                            "error_x": {"color": "#2a3f5f"},
                            "error_y": {"color": "#2a3f5f"},
                            "marker": {
                                "line": {"color": "#E5ECF6", "width": 0.5},
                                "pattern": {
                                    "fillmode": "overlay",
                                    "size": 10,
                                    "solidity": 0.2,
                                },
                            },
                            "type": "bar",
                        }
                    ],
                    "scattergeo": [
                        {
                            "type": "scattergeo",
                            "marker": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        }
                    ],
                    "scatterpolar": [
                        {
                            "type": "scatterpolar",
                            "marker": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        }
                    ],
                    "histogram": [
                        {
                            "marker": {
                                "pattern": {
                                    "fillmode": "overlay",
                                    "size": 10,
                                    "solidity": 0.2,
                                }
                            },
                            "type": "histogram",
                        }
                    ],
                    "scattergl": [
                        {
                            "type": "scattergl",
                            "marker": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        }
                    ],
                    "scatter3d": [
                        {
                            "type": "scatter3d",
                            "line": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                            "marker": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        }
                    ],
                    "scattermapbox": [
                        {
                            "type": "scattermapbox",
                            "marker": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        }
                    ],
                    "scatterternary": [
                        {
                            "type": "scatterternary",
                            "marker": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        }
                    ],
                    "scattercarpet": [
                        {
                            "type": "scattercarpet",
                            "marker": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                        }
                    ],
                    "carpet": [
                        {
                            "aaxis": {
                                "endlinecolor": "#2a3f5f",
                                "gridcolor": "white",
                                "linecolor": "white",
                                "minorgridcolor": "white",
                                "startlinecolor": "#2a3f5f",
                            },
                            "baxis": {
                                "endlinecolor": "#2a3f5f",
                                "gridcolor": "white",
                                "linecolor": "white",
                                "minorgridcolor": "white",
                                "startlinecolor": "#2a3f5f",
                            },
                            "type": "carpet",
                        }
                    ],
                    "table": [
                        {
                            "cells": {
                                "fill": {"color": "#EBF0F8"},
                                "line": {"color": "white"},
                            },
                            "header": {
                                "fill": {"color": "#C8D4E3"},
                                "line": {"color": "white"},
                            },
                            "type": "table",
                        }
                    ],
                    "barpolar": [
                        {
                            "marker": {
                                "line": {"color": "#E5ECF6", "width": 0.5},
                                "pattern": {
                                    "fillmode": "overlay",
                                    "size": 10,
                                    "solidity": 0.2,
                                },
                            },
                            "type": "barpolar",
                        }
                    ],
                    "pie": [{"automargin": True, "type": "pie"}],
                },
                "layout": {
                    "autotypenumbers": "strict",
                    "colorway": [
                        "#636efa",
                        "#EF553B",
                        "#00cc96",
                        "#ab63fa",
                        "#FFA15A",
                        "#19d3f3",
                        "#FF6692",
                        "#B6E880",
                        "#FF97FF",
                        "#FECB52",
                    ],
                    "font": {"color": "#2a3f5f"},
                    "hovermode": "closest",
                    "hoverlabel": {"align": "left"},
                    "paper_bgcolor": "white",
                    "plot_bgcolor": "#E5ECF6",
                    "polar": {
                        "bgcolor": "#E5ECF6",
                        "angularaxis": {
                            "gridcolor": "white",
                            "linecolor": "white",
                            "ticks": "",
                        },
                        "radialaxis": {
                            "gridcolor": "white",
                            "linecolor": "white",
                            "ticks": "",
                        },
                    },
                    "ternary": {
                        "bgcolor": "#E5ECF6",
                        "aaxis": {
                            "gridcolor": "white",
                            "linecolor": "white",
                            "ticks": "",
                        },
                        "baxis": {
                            "gridcolor": "white",
                            "linecolor": "white",
                            "ticks": "",
                        },
                        "caxis": {
                            "gridcolor": "white",
                            "linecolor": "white",
                            "ticks": "",
                        },
                    },
                    "coloraxis": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
                    "colorscale": {
                        "sequential": [
                            [0.0, "#0d0887"],
                            [0.1111111111111111, "#46039f"],
                            [0.2222222222222222, "#7201a8"],
                            [0.3333333333333333, "#9c179e"],
                            [0.4444444444444444, "#bd3786"],
                            [0.5555555555555556, "#d8576b"],
                            [0.6666666666666666, "#ed7953"],
                            [0.7777777777777778, "#fb9f3a"],
                            [0.8888888888888888, "#fdca26"],
                            [1.0, "#f0f921"],
                        ],
                        "sequentialminus": [
                            [0.0, "#0d0887"],
                            [0.1111111111111111, "#46039f"],
                            [0.2222222222222222, "#7201a8"],
                            [0.3333333333333333, "#9c179e"],
                            [0.4444444444444444, "#bd3786"],
                            [0.5555555555555556, "#d8576b"],
                            [0.6666666666666666, "#ed7953"],
                            [0.7777777777777778, "#fb9f3a"],
                            [0.8888888888888888, "#fdca26"],
                            [1.0, "#f0f921"],
                        ],
                        "diverging": [
                            [0, "#8e0152"],
                            [0.1, "#c51b7d"],
                            [0.2, "#de77ae"],
                            [0.3, "#f1b6da"],
                            [0.4, "#fde0ef"],
                            [0.5, "#f7f7f7"],
                            [0.6, "#e6f5d0"],
                            [0.7, "#b8e186"],
                            [0.8, "#7fbc41"],
                            [0.9, "#4d9221"],
                            [1, "#276419"],
                        ],
                    },
                    "xaxis": {
                        "gridcolor": "white",
                        "linecolor": "white",
                        "ticks": "",
                        "title": {"standoff": 15},
                        "zerolinecolor": "white",
                        "automargin": True,
                        "zerolinewidth": 2,
                    },
                    "yaxis": {
                        "gridcolor": "white",
                        "linecolor": "white",
                        "ticks": "",
                        "title": {"standoff": 15},
                        "zerolinecolor": "white",
                        "automargin": True,
                        "zerolinewidth": 2,
                    },
                    "scene": {
                        "xaxis": {
                            "backgroundcolor": "#E5ECF6",
                            "gridcolor": "white",
                            "linecolor": "white",
                            "showbackground": True,
                            "ticks": "",
                            "zerolinecolor": "white",
                            "gridwidth": 2,
                        },
                        "yaxis": {
                            "backgroundcolor": "#E5ECF6",
                            "gridcolor": "white",
                            "linecolor": "white",
                            "showbackground": True,
                            "ticks": "",
                            "zerolinecolor": "white",
                            "gridwidth": 2,
                        },
                        "zaxis": {
                            "backgroundcolor": "#E5ECF6",
                            "gridcolor": "white",
                            "linecolor": "white",
                            "showbackground": True,
                            "ticks": "",
                            "zerolinecolor": "white",
                            "gridwidth": 2,
                        },
                    },
                    "shapedefaults": {"line": {"color": "#2a3f5f"}},
                    "annotationdefaults": {
                        "arrowcolor": "#2a3f5f",
                        "arrowhead": 0,
                        "arrowwidth": 1,
                    },
                    "geo": {
                        "bgcolor": "white",
                        "landcolor": "#E5ECF6",
                        "subunitcolor": "white",
                        "showland": True,
                        "showlakes": True,
                        "lakecolor": "white",
                    },
                    "title": {"x": 0.05},
                    "mapbox": {"style": "light"},
                },
            }
        },
    }


def round_sf(val: float | int, sf: int = 1) -> float:
    """
    Round to specified significant figures.

    Parameters
    ----------
    val: float | int
        The value to be rounded
    sf:
        The number of significant figures

    Returns
    -------
    float
        The rounded value
    """
    return np.round(val, sf - 1 - int(np.floor(np.log10(np.abs(val)))))
