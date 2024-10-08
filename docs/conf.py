# Configuration file for the Sphinx documentation builder.

# -- Project information

project = "Cladetime"
copyright = "2024, Reich Lab @ The University of Massachusetts, Amherst"
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
html_static_path = ["../_static"]

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

# -- Options for HTML output

html_theme = "sphinx_book_theme"
# html_logo = "images/LOGO-hubverse-withtext.png"
html_favicon = "images/reichlab.png"
html_title = "Cladetime"
html_theme_options = {
    "home_page_in_toc": True,
    "repository_url": "https://github.com/reichlab/cladetime",
    "repository_branch": "main",
    "path_to_docs": "docs",
    "use_repository_button": True,
    # "use_edit_page_button": True,
    "use_issues_button": True,
    # "use_sidenotes": True,
    # "navbar_persistent": ["theme-switcher", "navbar-icon-links"],
}

# html_js_files = [
#     "js/custom.js",
# ]

# -- Options for EPUB output
epub_show_urls = "footnote"
