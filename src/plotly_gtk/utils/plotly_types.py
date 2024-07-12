"""Utilities to type plotly dicts."""

import importlib.resources
import json
import typing

import numpy as np

file = importlib.resources.files(anchor="plotly_gtk.utils.plotly_types").joinpath(
    "plot-schema.json"
)

with open(file, encoding="utf-8") as f:
    schema = json.load(f)

layout_attributes = schema["layout"]["layoutAttributes"]
data_attributes = schema["traces"]

if typing.TYPE_CHECKING:
    SchemaType = dict[str, "SchemaType" | str]
    GenericType = dict[str, "GenericType" | float | str | bool]


def build_type(attribute: "GenericType") -> type:
    """
    Build a type variable for part of the plotly schema.

    Parameters
    ----------
    attribute: GenericType
        A part of the plotly schema

    Returns
    -------
    type
        A type variable defining the type for this part of the schema.

    """

    if "valType" in attribute:
        val_type = attribute["valType"]
        if val_type == "number":
            OUT_TYPE = float
        elif val_type == "integer":
            OUT_TYPE = int
        elif val_type == "boolean":
            OUT_TYPE = bool
        elif val_type == "data_array":
            OUT_TYPE = np.ndarray | list
        elif val_type == "angle":
            OUT_TYPE = float
        else:
            OUT_TYPE = str
        return OUT_TYPE
    OUT_TYPES = []
    for v in attribute.values():
        if isinstance(v, dict):
            OUT_TYPE = build_type(v)
            if OUT_TYPE is not None:
                OUT_TYPES.append(OUT_TYPE)
    if not OUT_TYPES:
        return None
    return dict[str, typing.Union[*OUT_TYPES]]


Layout = build_type(layout_attributes)
Data = typing.Union[
    *[build_type(trace["attributes"]) for trace in data_attributes.values()]
]

prebuilt_types = {"layout": Layout, "data": Data}


def get_schema(*args: list[str]) -> "SchemaType":
    """
    Get part of the plotly schema.

    Parameters
    ----------
    args: list[str]
        A list of keys for indexing the plotly schema

    Returns
    -------
    SchemaType
        The relevant part of the ploty schema
    """
    if args[0] == "layout":
        schema_dict = layout_attributes
        for key in args[1:]:
            schema_dict = schema_dict[key]
    elif args[0] == "data":
        schema_dict = data_attributes[args[1]]["attributes"]
        for key in args[2:]:
            schema_dict = schema_dict[key]
    return schema_dict


def get_type(*args: list[str]) -> type:
    """
    Get a type variable for part of the plotly schema.

    Parameters
    ----------
    args: list[str]
        A list of keys for indexing the plotly schema

    Returns
    -------
    type
        A type defining part of the plotly schema

    """
    if "_".join(args) not in prebuilt_types:
        schema_dict = get_schema(*args)
        prebuilt_types["_".join(args)] = build_type(schema_dict)
    return prebuilt_types["_".join(args)]


def get_keys(*args: list[str]) -> type({}.keys()):
    """
    Get the keys from the plotly schema.

    Parameters
    ----------
    args: list[str]
        A list of keys for indexing the plotly schema

    Returns
    -------
    dict_keys
        The keys available

    Raises
    ------
    ValueError
        If the path specified is a single value not a dictionary
    """
    schema_dict = get_schema(*args)
    if "valType" in schema_dict:
        raise ValueError("This path is not a dictionary")
    return schema_dict.keys()


def get_description(*args: list[str]) -> str:
    """
    Get a description from the plotly schema.

    Parameters
    ----------
    args: list[str]
        A list of keys for indexing the plotly schema

    Returns
    -------
    str
        The description of the relevant key.
    """
    schema_dict = get_schema(*args)
    return schema_dict["description"]
