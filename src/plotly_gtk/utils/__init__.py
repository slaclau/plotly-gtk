"""This module provides utility classes and functions used by
:class:`plotly_gtk.chart.PlotlyGtk`."""

import collections
import importlib
import json
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
    """Return a copy of :class:`dict` `d` recursively updated with values from
    :class:`dict` `u`.

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
    """Return the RGB components of a color provided as a string.

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
    """Parse a dictionary of font parameters and return a
    :class:`gi.repository.Pango.FontDescription`.

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
    """Get the list of cartesian axes pairings with data plotted on them.

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
    """Avoid importing plotly by creating a base figure dictionary.

    Returns
    -------
    dict
        The dictionary returned by plotly.graph_object.Figure().to_dict()
    """
    template = "plotly"
    file = (
        importlib.resources.files(anchor="plotly_gtk.utils")
        / "templates"
        / f"{template}.json"
    )
    with open(file, encoding="utf-8") as f:
        template_dict = json.load(f)
    return {
        "data": [],
        "layout": {"template": template_dict},
    }


def round_sf(val: float | int, sf: int = 1) -> float:
    """Round to specified significant figures.

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
