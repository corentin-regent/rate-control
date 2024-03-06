import os
import sys
from importlib.metadata import version as get_version

from packaging.version import parse

sys.path.append(os.path.abspath('..'))

project = 'Rate Control'
author = 'Corentin Régent'
copyright = f'2024, {author}'

v = parse(get_version('rate-control'))
version = v.base_version
release = v.public

repository = 'https://github.com/corentin-regent/rate-control'

root_doc = 'index'
exclude_patterns = ['_build']
language = 'en'

html_theme = 'furo'
html_show_sourcelink = False
html_show_copyright = True
html_show_sphinx = True

html_theme_options = {
    'source_repository': repository,
    'source_branch': 'main',
    'source_directory': 'docs/',
    'footer_icons': [
        {
            'name': 'GitHub',
            'url': repository,
            'html': """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
                </svg>
            """,
        },
    ],
}

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
    'enum_tools.autoenum',
]

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_attr_annotations = True

autodoc_default_options = {
    'members': True,
    'inherited-members': True,
    'show-inheritance': True,
    'special-members': '__init__',
    'exclude-members': '__new__',
}
autodoc_class_signature = 'separated'
autodoc_member_order = 'alphabetical'
autodoc_typehints = 'signature'
autodoc_typehints_format = 'short'
autodoc_preserve_defaults = True
autodoc_warningiserror = True
autodoc_inherit_docstrings = True

typehints_document_rtype = False
typehints_use_signature = True
typehints_use_signature_return = True
