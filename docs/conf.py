import os
import sys
from datetime import date

# Configuration file for the Sphinx documentation builder.

# -- Project information

project = "Cladetime"
copyright = f"{date.today().year}, Reich Lab @ The University of Massachusetts Amherst"
author = "Reich Lab"

# Add cladetime location to the path, so we can use autodoc to
# generate API documentation from docstrings.
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_path)

release = "0.1"
# FIXME: get the version dynamically
version = "0.1.0"


# -- General configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_copybutton",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "myst_parser",  # markdown (NOTE: this is NOT mystmd)
    "sphinxext.opengraph",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_static_path = ["_static"]
html_theme = "furo"
html_favicon = "images/reichlab.png"
html_title = "Cladetime"

# These folders are copied to the documentation's HTML output
html_theme_options = {
    "announcement": """
        <a style=\"text-decoration: none; color: white;\"
           href=\"https://reichlab.io">
           This is an announcement!
        </a>
    """,
    "light_logo": "reichlab.png",
    "dark_logo": "reichlab.png",
    "navigation_with_keys": True,
}

# Order sidebar content, placing ads in the left sidebar
# html_sidebars = {
#     "**": [
#         "sidebar/brand.html",
#         "sidebar/search.html",
#         "sidebar/scroll-start.html",
#         "sidebar/navigation.html",
#         "sidebar/scroll-end.html",
#         "sidebar/ethical-ads.html",
#     ]
# }


# from https://myst-parser.readthedocs.io/en/latest/syntax/optional.html
myst_enable_extensions = [
    "amsmath",
    "deflist",
    "dollarmath",
    "fieldlist",
    "substitution",
    "tasklist",
    "colon_fence",
    "attrs_inline",
]

# Open Graph metadata
ogp_title = "cladetime documentation"
ogp_type = "website"
ogp_social_cards = {"image": "images/reichlab.png", "line_color": "#F09837"}
ogp_description = "cladetime is a user-friendly library for accessing Sars-Cov-2 clade data from Nextstrain."

# Test code blocks only when explicitly specified
doctest_test_doctest_blocks = ""


# -- Options for EPUB output
epub_show_urls = "footnote"
