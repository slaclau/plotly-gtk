import os
import pathlib
import sys

from plotly_gtk.demo import demos

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Plotly GTK"
copyright = "2024, Sebastien Laclau"
author = "Sebastien Laclau"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.graphviz",
    "sphinx_pyreverse",
    #    "numpydoc",
]

autosummary_generate = True


autodoc_default_options = {
    "undoc-members": True,
}
autoclass_content = "class"
# autodoc_class_signature = "separated"
autodoc_member_order = "bysource"
autodoc_docstring_signature = True
autodoc_mock_imports = []
autodoc_typehints = "description"

templates_path = ["_templates"]
exclude_patterns = []

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "gi.repository": ("https://amolenaar.pages.gitlab.gnome.org/pygobject-docs", None),
    "pandas": ("https://pandas.pydata.org/docs", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "plotly": ("https://plotly.com/python-api-reference/", None),
}

inheritance_graph_attrs = dict(rankdir="TB", size='""')

graphviz_output_format = "svg"

sys.path.insert(0, os.path.abspath("../"))

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'default'
# html_theme = "pydata_sphinx_theme"
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_extra_path = ["prebuilt"]

html_theme_options = {
    "logo": {
        "image_light": "icon.png",
        "image_dark": "icon.png",
    }
}
# -- Custom build scripts -------------------------------------------------
file = (pathlib.Path(__file__).parent / "examples.rst").resolve()
with open(file, "a+", encoding="utf-8") as f:
    title = "Examples\n"
    f.write(title)
    f.write("="*len(title)+"\n")
    for category, demos_list in demos.items():
        f.write(category+"\n")
        f.write("^"*len(category)+"\n\n")
        for demo in demos_list:
            f.write(f"{demo.capitalize().replace("_", " ")}\n")
            f.write("-"*len(demo)+"\n\n")
            f.write(".. literalinclude:: ../../src/plotly_gtk/demo.py\n")
            f.write(f"   :start-after: = \"{demo}\n")
            if demo == demos_list[-1]:
                f.write("   :end-before: return fig\n\n")
            else: 
                f.write("   :end-before: elif\n\n")

            f.write(f".. image:: examples/{demo}.png\n\n")
            
        
