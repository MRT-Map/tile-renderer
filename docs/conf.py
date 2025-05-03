# noqa
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from tile_renderer.__about__ import __version__

project = "tile-renderer"
copyright = "2024, MRT Mapping Services"  # noqa: A001
author = "MRT Mapping Services"
version = __version__
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_rtd_theme",
    "sphinxcontrib.programoutput",
    "sphinx_codeautolink",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
    "sphinx-jsonschema",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "click": ("https://click.palletsprojects.com/en/stable/", None),
    "shapely": ("https://shapely.readthedocs.io/en/stable", None),
    "msgspec": ("https://jcristharif.com/msgspec/", None),
    "niquests": ("https://niquests.readthedocs.io/en/latest/", None),
    "rich": ("https://rich.readthedocs.io/en/stable/", None)
}
html_baseurl = "https://mrt-map.github.io/tile-renderer"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
