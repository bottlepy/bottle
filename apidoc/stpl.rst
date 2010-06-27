======================
SimpleTemplate Engine
======================

.. currentmodule:: bottle

Bottle comes with a fast, powerful and easy to learn build-in template engine called *SimpleTemplate* or *stpl* for short. It is the default engine used by the :func:`view` and :func:`template` helpers but can be used as a stand-alone general purpose template engine, too. This document explains the template syntax and shows examples for common use cases.

.. rubric:: Basic API Usage:

:class:`SimpleTemplate` implements the :class:`BaseTemplate` API::

   >>> from bottle import SimpleTemplate
   >>> tpl = SimpleTemplate('Hello {{name}}!')
   >>> tpl.render(name='World')
   u'Hello World!'

In this document we use the :func:`template` helper in examples for the sake of simplicity::

   >>> from bottle import template
   >>> template('Hello {{name}}!', name='World')
   u'Hello World!'

Just keep in mind that compiling and rendering templates are two different actions, even if the :func:`template` helper hides this fact. Templates are usually compiled only once and cached internally, but rendered many times with differend keyword arguments.

:class:`SimpleTemplate` Syntax
==============================

Python is a very powerful language but its whitespace-aware syntax makes it difficult to use as a templates language. SimpleTemplate removes some of these restrictions and allows you to write clean, readable and maintainable templates while preserving full access to the features, libraries and speed of the Python language.

.. warning::

   The :class:`SimpleTemplate` Syntax compiles directly to python bytecode and is executed on each :meth:`SimpleTemplate.render` call. Do not render untrusted templates! They may contain and execute harmfull python code.

.. rubric:: Inline Statements

You already learned the use of the ``{{...}}`` statement from the "Hello World!" example above, but there is more: Any python statement is allowed within the curly brackets as long as it returns a string or something that has a string representation::

  >>> template('Hello {{name}}!', name='World')
  u'Hello World!'
  >>> template('Hello {{name.title() if name else "stranger"}}!', name=None)
  u'Hello stranger!'
  >>> template('Hello {{name.title() if name else "stranger"}}!', name='mArC')
  u'Hello Marc!'

The contained python statement is executed at render-time and has access to all keyword arguments passed to the :meth:`SimpleTemplate.render` method. HTML special characters are escaped automatically to prevent `XSS <http://en.wikipedia.org/wiki/Cross-Site_Scripting>`_ attacks. You can start the statement with an exclamation mark to disable escaping for that statement::

  >>> template('Hello {{name}}!', name='<b>World</b>')
  u'Hello &lt;b&gt;World&lt;/b&gt;!'
  >>> template('Hello {{!name}}!', name='<b>World</b>')
  u'Hello <b>World</b>!'

.. highlight:: html+django

.. rubric:: Embedded python code

The ``%`` character marks a line of python code. The only difference between this and real python code is that you have to explicitly close blocks with an ``%end`` statement. In return you can align the code with the surrounding template and don't have to worry about correct indention of blocks. The *SimpleTemplate* parser handles that for you. Lines *not* starting with a ``%`` are rendered as text as usual::

  %if name:
    Hi <b>{{name}}</b>
  %else:
    <i>Hello stranger</i>
  %end

The ``%`` character is only recognised if it is the first non-whitespace character in a line. To escape a heading ``%`` you can add a second one. ``%%`` is replaced by a single ``%`` in the resulting template::

  This line contains a % but no python code.
  %% This text-line starts with '%'
  %%% This text-line starts with '%%'

.. rubric:: Suppressing line breaks

You can suppress the line break in front of a code-line by adding a double backslash at the end of the line::

  <span>\\
  %if True:
  nobreak\\
  %end
  </span>

This template produces the following output::

  <span>nobreak</span>

.. rubric:: The ``%include`` Statement

You can include other templates using the ``%include sub_template [kwargs]`` statement. The ``sub_template`` parameter specifies the name or path of the template to be included. The rest of the line is interpreted as a comma-separated list of ``key=statement`` pairs similar to keyword arguments in function calls. They are passed to the sub-template analogous to a :meth:`SimpleTemplate.render` call. The ``**kwargs`` syntax for passing a dict is allowed too::

  %include header_template title='Hello World'
  <p>Hello World</p>
  %include foother_template

.. rubric:: The ``%rebase`` Statement

The ``%rebase base_template [kwargs]`` statement causes ``base_template`` to be rendered instead of the original template. The base-template then includes the original template using an empty ``%include`` statement and has access to all variables specified by ``kwargs``. This way it is possible to wrap a template with another template or to simulate the inheritance feature found in some other template engines.

Lets say you have a content-templates and want to wrap it with a common HTML layout frame. Instead of including several header and foother templates, you can use a single base-template to render the layout frame.

Base-template named ``layout.tpl``::

  <html>
  <head>
    <title>{{title or 'No title'}}</title>
  </head>
  <body>
    %include
  </body>
  </html>

Main-template named ``content.tpl``::

  This is the page content: {{content}}
  %rebase layout title='Content Title'

Now you can render ``content.tpl``:

.. code-block:: python

  >>> print template('content', content='Hello World!')

.. code-block:: html

  <html>
  <head>
    <title>Content Title</title>
  </head>
  <body>
    This is the page content: Hello World!
  </body>
  </html>

A more complex scenario involves chained rebases and multiple content blocks. The ``block_content.tpl`` template defines two functions and passes them to a ``colums.tpl`` base template::

  %def leftblock():
    Left block content.
  %end
  %def rightblock():
    Right block content.
  %end
  %rebase columns left=leftblock, right=rightblock, title=title

The ``columns.tpl`` base-template uses the two callables to render the content of the left and right column. It then wraps itself with the ``layout.tpl`` template defined earlier::

  %rebase layout title=title
  <div style="width: 50%; float:left">
    %left()
  </div>
  <div style="width: 50%; float:right">
    %right()
  </div>

Lets see how ``block_content.tpl`` renders:

.. code-block:: python

  >>> print template('block_content', title='Hello World!')

.. code-block:: html

  <html>
  <head>
    <title>Hello World</title>
  </head>
  <body>
  <div style="width: 50%; float:left">
    Left block content.
  </div>
  <div style="width: 50%; float:right">
    Right block content.
  </div>
  </body>
  </html>



:class:`SimpleTemplate` API
==============================

.. autoclass:: SimpleTemplate
   :members:

Known bugs
==============================

Some syntax construcs allowed in python are problematic within a template. The following syntaxes won't work with SimpleTemplate:

  * Multi-line statements must end with a backslash (``\``) and a comment, if presend, must not contain any additional ``#`` characters.
  * Multi-line strings are not supported yet.
