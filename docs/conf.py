# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# pylint: disable=invalid-name
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
import os
import sys


class mockDtls:
    @staticmethod
    def do_patch():
        pass


# Mock dtls module since it may segfault
sys.modules["dtls"] = mockDtls

sys.path.insert(0, os.path.abspath(".."))
sys.path.append(os.path.abspath("./_ext"))


# -- Project information -----------------------------------------------------

project = "pyzwave"
copyright = "2020, Micke Prag"  # pylint: disable=redefined-builtin
author = "Micke Prag"

# The full version, including alpha/beta/rc tags
release = "0.1.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinxcontrib.apidoc", "attributesMixin"]

autodoc_default_options = {"show-inheritance": True, "members": True}

apidoc_module_dir = "../pyzwave"
apidoc_output_dir = "reference"
apidoc_separate_modules = True
apidoc_toc_file = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The master toctree document.
master_doc = "index"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
