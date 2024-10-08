# -*- coding: utf-8 -*-
import sys
import os
import time

# Use the matching bottle version, not a globally installed one.
bottle_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.insert(0, bottle_dir)
import bottle

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx',
              'sphinx.ext.viewcode']
master_doc = 'index'
project = u'Bottle'
copyright = u'2009-%s, %s' % (time.strftime('%Y'), bottle.__author__)
version = ".".join(bottle.__version__.split(".")[:2])
release = bottle.__version__
add_function_parentheses = True
add_module_names = False
autodoc_member_order = 'bysource'
autodoc_class_signature = 'separated'
pygments_style = 'sphinx'
intersphinx_mapping = {'python': ('https://docs.python.org/3', None),
                       'werkzeug': ('https://werkzeug.palletsprojects.com/en/3.0.x', None)}

locale_dirs = ['_locale/']
gettext_compact = False


