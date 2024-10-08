# Configuration file for the Sphinx documentation builder.

# -- Project information

project = "Cladetime"
copyright = "2024, Reich Lab @ The University of Massachusetts Amherst"
author = "Reich Lab"

release = "0.1"
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

# These folders are copied to the documentation's HTML output
html_static_path = ["_static"]
html_theme_options = {
    "announcement": """
        <a style=\"text-decoration: none; color: white;\"
           href=\"https://reichlab.io">
           <img src=\"/en/latest/_static/reichlab.png\"/> This is an announcement!
        </a>
    """,
    "sidebar_hide_name": True,
    "light_logo": "banner.svg",
    "dark_logo": "dark-logo.svg",
}

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

# -- Options for HTML output

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "furo"
html_favicon = "images/reichlab.png"
html_title = "Cladetime"
html_theme_options = {}

# html_js_files = [
#     "js/custom.js",
# ]

# -- Options for EPUB output
epub_show_urls = "footnote"
