Simple Template Engine
======================

.. currentmodule:: bottle

Bottle implements its own little template engine. The :func:`view` decorator and :func:`template` function use it by default.

.. warning::

    The :class:`SimpleTemplate` Syntax compiles directly to python bytecode and is executed on each :meth:`SimpleTemplate.render` call. Do not render untrusted templates! They may contain and execute harmfull python code. 


:class:`SimpleTemplate` Syntax
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The template syntax is a very thin layer around the Python language. It's main purpose is to ensure correct indention of blocks, so you can format your template without worrying about indentions.

.. rubric:: Code lines

Lines starting with ``%`` are interpreted as python code. The only difference between this and normal python code is that you have to explicitly close blocks with an ``%end`` statement. This way it is possible to align the code to the surrounding template without worrying about correct indentions. Whitespace in front of a code line is compleately ignored.

Here is an example::

  %if name == 'Marc':
    Hi Marc!
  %else:
    Hello stranger!
  %end

.. rubric:: Inline Statements

Lines *not* starting with ``%`` are printed as text. Any occurrence of ``{{stmt}}`` in text-lines is replaced by the return value of the included python statement. In most cases this is just the name of a local variable, but any python statement returning a string is allowed.

::

  %if name:
    Hello {{name}} :)
    Your last login was: {{lastlogin.strftime("%A %d. %B %Y") if lastlogin else 'Never'}}
  %else:
    Please login.
  %end

HTML special characters are escaped by default to prevent `XSS <http://en.wikipedia.org/wiki/Cross-Site_Scripting>`_ attacks. Use the ``{{!stmt}}`` syntax to suppress escaping for that statement.

.. rubric:: The ``%include`` Statement

You can include other templates using the ``%include sub_template [kwargs]`` statement. The ``sub_template`` parameter specifies the name or path of the template to be included. The rest of the line is interpreted as a comma-separated list of ``key=statement`` pairs similar to keyword arguments in function calls. They are passed to the sub-template analogous to a :func:`render` call. The ``**kwargs`` syntax for passing a dict is allowed too.

.. rubric:: The ``%rebase`` Statement

Base-templates are templates that contain an empty ``%include`` statement. Any other template can use the ``%rebase base_template [kwargs]`` statement to inject itself into  a base-template. The ``%include`` statement of the base-template is then replaced by the rendered result of the rebasing template. The arguments specified in ``kwargs`` are accessible from within the base-template as normal template variables. This feature simulates the inheritance support of most other template engines and can be seen as a *reverse include*. It is best described by example:

.. highlight:: html

A base template named ``html.tpl``::

  <html>
  <head>
    <title>{{title or 'No title'}}</title>
  </head>
  <body>
    %include
  </body>
  </html>

A rebasing template named ``content.tpl``::

  This is the page content.
  %rebase html title='Content Title'

You can now render content.tpl and will get::

  <html>
  <head>
    <title>Content Title</title>
  </head>
  <body>
    This is the page content.
  </body>
  </html>

If you need to fill more than one block in the base template, you can define functions and pass them to the base template.

``columns.tpl``::

  <div style="width: 50%; float:left">
    %left()
  </div>
  <div style="width: 50%; float:right">
    %right()
  </div>

``content.tpl``::

  %def leftblock():
    Left block content.
  %end
  %def rightblock():
    Right block content.
  %end
  %rebase columns left=leftblock, right=rightblock

.. rubric:: Suppressing line breaks

You can suppress the line break after the line preceding a code-line by adding a double backslash at the end of the line::

  <span>\\
  %if True:
  nobreak\\
  %end
  </span>

This template produces the following output::

  <span>nobreak</span>


