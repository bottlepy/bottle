======================
SimpleTemplate Engine
======================

.. currentmodule:: bottle

Bottle comes with a fast, powerful and easy to learn built-in template engine called *SimpleTemplate* or *stpl* for short. It is the default engine used by the :func:`view` and :func:`template` helpers but can be used as a stand-alone general purpose template engine too. This document explains the template syntax and shows examples for common use cases.

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

Just keep in mind that compiling and rendering templates are two different actions, even if the :func:`template` helper hides this fact. Templates are usually compiled only once and cached internally, but rendered many times with different keyword arguments.

:class:`SimpleTemplate` Syntax
==============================

Python is a very powerful language but its whitespace-aware syntax makes it difficult to use as a template language. SimpleTemplate removes some of these restrictions and allows you to write clean, readable and maintainable templates while preserving full access to the features, libraries and speed of the Python language.

.. warning::

   The :class:`SimpleTemplate` syntax compiles directly to python bytecode and is executed on each :meth:`SimpleTemplate.render` call. Do not render untrusted templates! They may contain and execute harmful python code.

Inline Expressions
------------------

You already learned the use of the ``{{...}}`` syntax from the "Hello World!" example above, but there is more: any python expression is allowed within the curly brackets as long as it evaluates to a string or something that has a string representation::

  >>> template('Hello {{name}}!', name='World')
  u'Hello World!'
  >>> template('Hello {{name.title() if name else "stranger"}}!', name=None)
  u'Hello stranger!'
  >>> template('Hello {{name.title() if name else "stranger"}}!', name='mArC')
  u'Hello Marc!'

The contained python expression is executed at render-time and has access to all keyword arguments passed to the :meth:`SimpleTemplate.render` method. HTML special characters are escaped automatically to prevent `XSS <http://en.wikipedia.org/wiki/Cross-Site_Scripting>`_ attacks. You can start the expression with an exclamation mark to disable escaping for that expression::

  >>> template('Hello {{name}}!', name='<b>World</b>')
  u'Hello &lt;b&gt;World&lt;/b&gt;!'
  >>> template('Hello {{!name}}!', name='<b>World</b>')
  u'Hello <b>World</b>!'

Embedded python code
--------------------

.. highlight:: html+django

The template engine allows you to embed lines or blocks of python code within your template. Code lines start with ``%`` and code blocks are surrounded by ``<%`` and ``%>`` tokens::

  % name = "Bob"  # a line of python code
  <p>Some plain text in between</p>
  <%
    # A block of python code
    name = name.title().strip()
  %>
  <p>More plain text</p>

Embedded python code follows regular python syntax, but with two additional syntax rules:

* **Indentation is ignored.** You can put as much whitespace in front of statements as you want. This allows you to align your code with the surrounding markup and can greatly improve readability.
* Blocks that are normally indented now have to be closed explicitly with an ``end`` keyword.

::

  <ul>
    % for item in basket:
      <li>{{item}}</li>
    % end
  </ul>

Both the ``%`` and the ``<%`` tokens are only recognized if they are the first non-whitespace characters in a line. You don't have to escape them if they appear mid-text in your template markup. Only if a line of text starts with one of these tokens, you have to escape it with a backslash. In the rare case where the backslash + token combination appears in your markup at the beginning of a line, you can always help yourself with a string literal in an inline expression:: 

  This line contains % and <% but no python code.
  \% This text-line starts with the '%' token.
  \<% Another line that starts with a token but is rendered as text.
  {{'\\%'}} this line starts with an escaped token.

If you find yourself to escape a lot, consider using :ref:`custom tokens <stpl-custom-tokens>`.

Whitespace Control
-----------------------

Code blocks and code lines always span the whole line. Whitespace in front of after a code segment is stripped away. You won't see empty lines or dangling whitespace in your template because of embedded code::

  <div>
   % if True:
    <span>content</span>
   % end
  </div>

This snippet renders to clean and compact html::

  <div>
    <span>content</span>
  </div>

But embedding code still requires you to start a new line, which may not what you want to see in your rendered template. To skip the newline in front of a code segment, end the text line with a double-backslash::

  <div>\\
   %if True:
  <span>content</span>\\
   %end
  </div>

THis time the rendered template looks like this::

  <div><span>content</span></div>

This only works directly in front of code segments. In all other places you can control the whitespace yourself and don't need any special syntax.

Template Functions
==================

Each template is preloaded with a bunch of functions that help with the most common use cases. These functions are always available. You don't have to import or provide them yourself. For everything not covered here there are probably good python libraries available. Remember that you can ``import`` anything you want within your templates. They are python programs after all.

.. currentmodule:: stpl

.. versionchanged:: 0.12
   Prior to this release, :func:`include` and :func:`rebase` were sytnax keywords, not functions.

.. function:: include(sub_template, **variables)

  Render a sub-template with the specified variables and insert the resulting text into the current template. The function returns a dictionary containing the local variables passed to or defined within the sub-template::

    % include('header.tpl', title='Page Title')
    Page Content
    % include('foother.tpl')

.. function:: rebase(name, **variables)

  Mark the current template to be later included into a different template. After the current template is rendered, its resulting text is stored in a variable named ``base`` and passed to the base-template, which is then rendered. This can be used to `wrap` a template with surrounding text, or simulate the inheritance feature found in other template engines::

    % rebase('base.tpl', title='Page Title')
    <p>Page Content ...</p>

  This can be combined with the following ``base.tpl``::

    <html>
    <head>
      <title>{{title or 'No title'}}</title>
    </head>
    <body>
      {{base}}
    </body>
    </html>


Accessing undefined variables in a template raises :exc:`NameError` and
stops rendering immediately. This is standard python behavior and nothing new,
but vanilla python lacks an easy way to check the availability of a variable.
This quickly gets annoying if you want to support flexible inputs or use the
same template in different situations. These functions may help:

.. function:: defined(name)

    Return True if the variable is defined in the current template namespace,
    False otherwise.

.. function:: get(name, default=None)

    Return the variable, or a default value.

.. function:: setdefault(name, default)

    If the variable is not defined, create it with the given default value.
    Return the variable.

Here is an example that uses all three functions to implement optional template
variables in different ways::

    % setdefault('text', 'No Text')
    <h1>{{get('title', 'No Title')}}</h1>
    <p> {{ text }} </p>
    % if defined('author'):
      <p>By {{ author }}</p>
    % end

.. currentmodule:: bottle


:class:`SimpleTemplate` API
==============================

.. autoclass:: SimpleTemplate
   :members:

