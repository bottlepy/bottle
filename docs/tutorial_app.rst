.. _Bottle: http://bottlepy.org
.. _WSGI: https://peps.python.org/pep-3333/
.. _Python: http://www.python.org
.. _SQLite: http://www.sqlite.org
.. _`SQLite module`: https://docs.python.org/3/library/sqlite3.html#module-sqlite3
.. _`HTML tutorial`: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content
.. _venv: https://docs.python.org/3/library/venv.html
.. _`decorator function`: http://docs.python.org/glossary.html#term-decorator
.. _`Python DB API`: http://www.python.org/dev/peps/pep-0249/
.. _`WSGI reference Server`: http://docs.python.org/library/wsgiref.html#module-wsgiref.simple_server
.. _`Bottle documentation`: http://bottlepy.org/docs/dev/tutorial.html
.. _JSON: http://www.json.org
.. _`match statement`: https://peps.python.org/pep-0634/
.. _f-strings: https://docs.python.org/3/library/string.html#format-string-syntax
.. _`Bottle class`: https://bottlepy.org/docs/dev/api.html#the-bottle-class
.. _`Zen of Python`: https://peps.python.org/pep-0020/
.. _`dynamic routes`: https://bottlepy.org/docs/dev/tutorial.html#dynamic-routes
.. _`RegEx module`: https://docs.python.org/3/library/re.html
.. _pathlib: https://docs.python.org/3/library/pathlib.html
.. _`static_file documentation`: https://bottlepy.org/docs/dev/api.html#bottle.static_file
.. _`server adapters`: https://bottlepy.org/docs/dev/deployment.html#server-adapters
.. _`Waitress`: https://docs.pylonsproject.org/projects/waitress/en/latest/


=========================
ToDo Application Example
=========================

This tutorial gives a brief introduction to the Bottle_ WSGI_ Framework. The main goal this tutorial is, after finishing working yourself through, to be able to create a project using Bottle. Within this document, by far not all features are shown, but at least the main and important ones like request routing, utilizing the Bottle template engine to format output as well as handling GET and POST request are featured. The last section gives a brief introduction how to serve a Bottle application by a WSGI application server.

To understand the content of this tutorial, it is not really necessary to have a basic knowledge of WSGI, as Bottle tries to keep WSGI away from the user anyway as much as possible. A fair bit of understanding of the Python_ programming language is of course required. Furthermore, the example application created in this tutorial retrieves and stores data in a SQL database, so (very) basic knowledge on SQL helps, but is not a must to understand the concepts of Bottle. Right here, SQLite_ is used. As Bottle is a framework for web-based application, most of output send to the Browser is HTML. Thus, a basic idea about the common HTML tags certainly helps as well. In case HTML basic still need to be learned, a good starting point is the `HTML tutorial`_ on the Mozilla Developer Network website.

For the sake of introducing Bottle, the Python code "in between" is kept short, in order to keep the focus. Although all code within the tutorial works fine, it may not necessarily be used as-is "in the wild", e.g. on a publically accessible server. To do so, e.g. input validtion, better database protection, better error handling and other things need to be added.

.. contents:: Table of Contents

Goals
======

At the end of this tutorial, a ready-to-use, simple, web-based ToDo application is going to be programmed. The app takes tasks, each one consisting of a text (with max 100 characters) and a status (0 for closed, 1 for open). Through the web-based user interface, open task can be view and edited and new tasks can be added.

During development, all pages will be available under the address ``127.0.0.1`` (aka: ``localhost``) in a web browser running on the same machine as the Bottle application code. Later on it will be shown how to adapt the application for a "real" server.

Bottle will do the routing and format the output with the help of templates. The tasks will be stored inside a SQLite database. Reading and writing the database will be done by Python code.

The result of this tutorial is going to be an application with the following pages and functionality:

 * start page ``http://127.0.0.1:8080/todo``
 * adding a new task to the list: ``http://127.0.0.1:8080/new``
 * page for editing a task: ``http://127.0.0.1:8080/edit/<number:int>``
 * show details about a task: ``http://127.0.0.1:8080/details/<number:int>``
 * show a task formated as JSON: ``http://127.0.0.1:8080/as_json/<number:int>``
 * redirect ``http://127.0.0.1:8080/`` to ``http://127.0.0.1:8080/todo``
 * catching errors


Prior to Starting ...
======================

.. rubric:: A Note on Python Versions

Bottle supports a wide range of Python version. Bottle 0.13 supports Python 3.8 and newer as well as Python 2 starting with 2.7.3, although Python 2 support will be dropped with Bottle 0.14. As Python 2 support was dropped by the Python core developers on Jan 1st 2020 already, it is highly encourage to use a recent Python 3 release.

This tutorial requires at least Python 3.10, as at one point the `match statement`_ is going to be used, which was introduced with Python 3.10. In case Python 3.8 or 3.9 is going to be used, the match statement needs to be replaced with an if-elif-else cascade, all other sections will work just fine. If really Python 2.7.x must be used, additionally the f-strings_ used at some places needs to be replaced with the string formatting methods available in Python 2.7.x.

And, finally, ``python`` will be used in this tutorial to run Python 3.10 and newer. On some platforms it may be necessary to type ``python3`` instead to run the installed Python 3 interpreter.


.. rubric:: Install Bottle

Assuming that a fairly new installation of Python (version 3.10 or higher) is used, only Bottle needs to be installed in addition to that. Bottle has no other dependencies than Python itself. Following the recommended best-practice for Python and installing Python modules, let's create a venv_ first and install Bottle inside the venv. Open the directory of choice where the venv should be created and execute the following commands:

.. code::

    python -m venv bottle_venv
    cd bottle_venv
    #for Linux & macOS
    source bin/activate
    #for Windows
    .\Scripts\activate
    pip3 install bottle


.. rubric:: SQLite

This tutorial uses _SQLite as the database. The standard release of Python has SQlite already on board and have `SQLite module`_ included to interact with the database. So no further installation is required here.

.. rubric:: Create An SQL Database

Prior to starting to work on the ToDo application, the database to be used later on needs to be created. To do so, save the following script in the project directory and run it with python. Alternatively, the lines of code can be executed in the interactive Python interpreter, too::

    import sqlite3
    connection = sqlite3.connect('todo.db') # Warning: This file is created in the current directory
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE todo (id INTEGER PRIMARY KEY, task char(100) NOT NULL, status bool NOT NULL)")
    cursor.execute("INSERT INTO todo (task,status) VALUES ('Read the Python tutorial to get a good introduction into Python',0)")
    cursor.execute("INSERT INTO todo (task,status) VALUES ('Visit the Python website',1)")
    cursor.execute("INSERT INTO todo (task,status) VALUES ('Test various editors for and check the syntax highlighting',1)")
    cursor.execute("INSERT INTO todo (task,status) VALUES ('Choose your favorite WSGI-Framework',0)")
    conn.commit()

These commands generate a database-file named `todo.db` with a table called ``todo``. The table has three columns ``id``, ``task``, and ``status``. ``id`` is a unique id for each row, which is used later to reference rows of data. The column ``task`` holds the text which describes the task, it is limited to max 100 characters. Finally, the column ``status`` is used to mark a task as open (represented by the value 1) or closed (represented by the value 0).


Writing a Web-Based ToDo Application with Bottle
=================================================

Let's dive into Bottle and create the web-based ToDo application. But first, let's look into a basic concept of Bottle: routes.


.. rubric:: Understanding routes

Basically, each page visible in the browser is dynamically generated when the page address is called. Thus, there is no static content. That is exactly what is called a "route" within Bottle: a certain address on the server. So, for example, opening the URL ``http://127.0.0.1:8080/todo`` from the browser, Bottle "grabs" the call on the server-side and checks if there is any (Python) function defined for the route "todo". If so, Bottle executes the corresponding Python code and returns its result. So, what Bottle (as well as other Python WSGI frameworks) does: it binds an URL to a function.


.. rubric:: Bottle basic by a "Hello World" example

Before finally starting the ToDo app, let's create a very basic "Hello World" example:

.. code-block:: python

    from bottle import Bottle


    app = Bottle()

    @app.route('/')
    def index():
        return 'Hello from Bottle'

    if __name__ == '__main__':
        app.run(host='127.0.0.1', port=8080)


Save the file under a name of choice, e.g. ``hello_bottle.py`` and execute the file ``python hello_bottle.py``. Then open the browser and enter ``http://127.0.0.1:8080`` in the address bar. The browser window should now show the text "Hello from Bottle".

So, what happens here? Let's dissect line by line:

- ``from bottle import Bottle`` imports the ``Bottle`` class from the Bottle module. Each instance derived from the class
  represents a single, distinct web application.
- ``app = Bottle()`` creates an instance of ``Bottle``. ``app`` is the web application object.
- ``@app.route('/')``  creates a new route bond to ``/`` for the app.
- ``def index()`` defines a function which is "linked" to the route ``/``, as the ``index`` function is decorated with
  the ``app.route`` decorator (more on that below).
- ``return 'Hello from Bottle'`` "Hello from Bottle" is the plain text send to the browser when the route is called.
- ``if __name__ == '__main__':``: The following code is only execute when the file holding the code is directly executed
  by the Python interpreter. In case e.g. a WSGI server is serving the code (more on that later), the following code
  is not executed.
- ``app.run(host='127.0.0.1', port=8080)`` starts the build-in development server, listing on the address ``127.0.0.1``
  and port ``8080``.


.. rubric:: First Step - Showing All Open Items

So, after understanding the concept of routes and the basics of Bottle, let's create the first real route for the ToDo application. The goal is to see all open items from the ToDo list:

.. code-block:: python

    import sqlite3
    from bottle import Bottle


    app = Bottle()

    @app.route('/todo')
    def todo_list():
        with sqlite3.connect('todo.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, task, status FROM todo WHERE status LIKE '1'")
            result = cursor.fetchall()
            return str(result)

    if __name__ == '__main__':
        app.run(host='127.0.0.1', port=8080)


Save the code as ``todo.py``, preferably in the same directory as the database file ``todo.db``. Otherwise, the path to ``todo.db`` must be added in the ``sqlite3.connect()`` statement.

Let's have a look what happens here: the required module ``sqlite3`` is imported to access to SQLite database, and from Bottle the ``Bottle`` class is imported. One function is defined, ``todo_list()``, with a few lines of code reading from the database. The important point here is the `decorator function`_ ``@route('/todo')`` right before the ``def todo_list()`` statement. By doing this, this function is bound to the route ``/todo``, so every time the browsers calls ``http://127.0.0.1:8080/todo``, Bottle returns the result of the function ``todo_list()``. That is how routing within bottle works.

Actually, more than one route can be bound to a function. The following code:

.. code-block:: python

    @route('/todo')
    @route('/my_todo_list')
    def todo_list():
        ...

works fine, too. What will not work is to bind one route to more than one function.

What the browser displays is what is returned, thus the value given by the ``return`` statement. In this example, it is necessary to convert ``result`` into a string by ``str()``, as Bottle expects a string or a list of strings from the return statement. But here, the result of the database query is a list of tuples, which is the standard defined by the `Python DB API`_.

Now, after understanding the little script above, it is time to execute it and watch the result. Just run ``python todo.py`` and open the URL ``http://127.0.0.1:8080/todo`` in the browser. In case no mistake was made writing the code, the output should look like this::

    [(2, 'Visit the Python website', 1), (3, 'Test various editors for and check the syntax highlighting', 1)]

If so - congratulations! Bottle is successful used. In case it did not work, and changes need to be made, remember to stop Bottle serving the page, otherwise the revised version will not be loaded.

The output is not really exciting nor nice to read. It is the raw result returned from the SQL query. In the next step the output is formated in a nicer way. But before that, let's make life a bit easier while developing the app.


.. rubric:: Debugging and Auto-Reloading

Maybe it was already noticed that Bottle sends a short error message to the browser in case something within the script went wrong, e.g. the connection to the database is not working. For debugging purposes, it is quite helpful to get more details. This can be easily achieved by adding the following to the script:

.. code-block:: python

    from bottle import Bottle
    ...
    if __name__ == '__main__':
        app.run(host='127.0.0.1', port=8080, debug=True)


By enabling "debug", a full stacktrace of the Python interpreter will be received in case of an error, which usually contains useful information, helping to find the error. Furthermore, templates (see below) are not cached, thus changes to templates will take effect without stopping and restarting the server.

.. warning::

    ``debug=True`` is supposed to be used for development only, it should *not* be used in production environments.


Another nice feature while developing is auto-reloading, which is enabled by modifying the ``app.run()`` statement to

.. code:: python

    app.run(host='127.0.0.1', port=8080, reloader=True)


This will automatically detect changes to the script and reload the new version once it is called again, without the need to stop and start the server.

Again, the feature is mainly supposed to be used while developing, not on production systems.


.. rubric:: Bottle's SimpleTemplate To Format The Output

Now let's have a look at casting the output of the script into a proper format. Actually, Bottle expects to receive a string or a list of strings from a function and returns them to the browser. Bottle does not bother about the content of the string itself, so it can be e.g. text formatted with HTML markup.

Bottle has its own easy-to-use, build-in template engine called "SimpleTemplate". Templates are stored as separate files having a ``.tpl`` extension. And by default, they are expected to be in a directory called ``views`` below the directory where the Python code of the application is located. A template can be called from within a function. Templates can contain any type of text (which will be most likely HTML-markup mixed with Python statements). Furthermore, templates can take arguments, e.g. the result set of a database query, which will be then formatted nicely within the template.

Right here, the result of the query showing the open ToDo tasks is cast into a simple HTML table with two columns: the first column will contain the ID of the item, the second column the text. The result is, as seen above, a list of tuples, each tuple contains one set of results.

To include the template in the example, just add the following lines:

.. code-block:: python

    from bottle import Bottle, template
    ...
        result = cursor.fetchall()
    output = template('show_tasks', rows=result)
    return output
    ...


Two things are done here: first, ``template`` additionally imported from bottle in order to be able to use templates. Second, the output of the template ``show_tasks`` is assigned to the variable ``output``, which then is returned. In addition to calling the template, ``result`` is assigned, which is received from the database query, to the variable ``rows``, which passed to the template to be used within the template later on. If necessary, more than one variable / value can be passed to a template.

Templates always return a list of strings, thus there is no need to convert anything. One line of code can be saved by writing ``return template('show_tasks', rows=result)``, which gives exactly the same result as above.

Now it is time to write the corresponding template, which looks like this:

.. code-block:: html

    %#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
    <p>The open items are as follows:</p>
    <table border="1">
    %for row in rows:
      <tr>
      %for col in row:
        <td>{{col}}</td>
      %end
      </tr>
    %end
    </table>

Save the code as ``show_tasks.tpl`` in the ``views`` directory.

Let's have a look at the code: every line starting with % is interpreted as Python code. Because it is effectively Python, only valid Python statements are allowed. The template will raise exceptions, just as any other Python code would, in case of wrong code. The other lines are plain HTML markup.

As can be seen, Python's ``for`` statement is used two times, to go through ``rows``. As seen above, ``rows`` is a variable which holds the result of the database query, so it is a list of tuples. The first ``for`` statement accesses the tuples within the list, the second one the items within the tuple, which are put each into a cell of the table. It is important that all ``for``, ``if``, ``while`` etc. statements are closed with ``%end``, otherwise the output will not be as expected.

If a variable within a non-Python code line needs to be accessed inside the template, put it into double curly braces, like ``{{ col  }}`` in the example above. This tells the template to insert the actual value of the variable right at this place.

Run the script again and look at the output. Still not really nice and not complete HTML, but at least more readable than the list of tuples.


.. rubric:: Adding a Base Template

Bottle's SimpleTempate allows, like other template engines, nesting templates. This is pretty handy, as it allows to define a base template holding e.g. the HTML doctype definition, the head and the body section, which is then used as the base for all other templates generating the actual output. The base template looks like this:

.. code-block:: html

    <!doctype html>
    <html lang="en-US">
    <head>
    <meta charset="utf-8" />
    <title>ToDo App powered by Bottle</title>
    </head>
    <body>
    {{!base}}
    </body>
    </html>


Save this template with the name ``base.tpl`` in the ``views`` folder.

As can be seen, the template holds a basic HTML skeleton for a typically website. The ``{{!base}}`` inserts the content of the other template using the base template.

To use the base template from another template like e.g. ``shows_task.tpl``, just add the following line at the beginning of this template:

.. code::

    % rebase('base.tpl')
    ...


This tells the template to rebase its content into the template ``base.tpl``.

Reload ``http://127.0.0.1:8000/todo`` and the output is now valid HTML. Of course, the base template can extended as required, e.g. by loading a CSS style sheet or defining own styles in a ``<style>...</style>`` section in the header.


.. rubric:: Using GET Parameters

The app has its first route showing task, but so far it only shows the open tasks. Let's modify this functionality and add an (optional) GET parameter to the route which lets the user choose whether to show open tasks only (which is at the same time the default), only closed tasks or all tasks stored in the database. This should be achieved by checking for a key named ``show``, which can have one of the following three values: ``open``, ``closed``  or ``all``. So e.g. opening the URL ``http://127.0.0.1:8080?show=all`` should make the application show all tasks from the database.

The updated route and corresponding function look like this:

.. code-block:: python

    ...
    from bottle import request
    ...
    @app.get('/todo')
    def todo_list():
        show  = request.query.show or 'open'
        match show:
            case 'open':
                db_query = "SELECT id, task FROM todo WHERE status LIKE '1'"
            case 'closed':
                db_query = "SELECT id, task FROM todo WHERE status LIKE '0'"
            case 'all':
                db_query = "SELECT id, task FROM todo"
            case _:
                return template('message.tpl',
                    message = 'Wrong query parameter: show must be either open, closed or all.')
        with sqlite3.connect('todo.db') as connection:
            cursor = connection.cursor()
            cursor.execute(db_query)
            result = cursor.fetchall()
        output = template('show_tasks.tpl', rows=result)
        return output
    ...


At first, ``request`` is added to the imports from Bottle. The ``request`` object of Bottle holds all data from a request sent to the application. Additionally, the route is change to ``@app.get(...)`` to explicitly state that this route only excepts GET requests only.

.. note::

    This change is not strictly necessary, as ``app.route()`` accepts implicitly GET request only, too. However, following the `Zen of Python`_ : "Explicit is better than implicit."

The line ``show_all  = request.query.show or 'open'`` does the following: ``query`` is the attribute of the ``request`` object holding the data from a GET request. So ``request.query.show`` returns the value of the key ``show`` from the request. If ``show`` is not present, the value ``open`` is assigned to the ``show`` variable. This also implies that any other key in the GET request is ignored.

The following ``match`` statement assigns a SQL query to the variable ``db_query`` depending on the value of ``show``, respectively shows an error message if ``show`` is neither ``open`` nor ``closed`` nor ``all``. The remaining code of the ``todo_list()`` function remains unchanged.

While working on this route, let's make one addition to the ``show_tasks`` template. Add the line

.. code-block:: html

    <p><a href="/new">Add a new task</a></p>


at the end of the template to add a link for adding a new task to the database. The corresponding route and function will be created in the following section.

And, finally, the new template ``message.tpl`` used in the code about, looks like this:

.. code-block:: html

    % rebase('base.tpl')
    <p>{{ message }}</p>
    <p><a href="/todo">Back to main page</p>


.. rubric:: Using Forms and POST Data

As all tasks now can be viewed properly, let's move to the next step and add the functionality to add a new task to the ToDo list. The new task should be received from a regular HTML form, sending its data by a POST request.

To do so, first a new route is added to the code. The route should accept GET and POST requests:

.. code-block:: python

    @app.route('/new', method=['GET', 'POST'])
    def new_task():
        if request.POST:
            new_task = request.forms.task.strip()
            with sqlite3.connect('todo.db') as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO todo (task,status) VALUES (?,?)", (new_task, 1))
                new_id = cursor.lastrowid
            return template('message.tpl',
                message=f'The new task was inserted into the database, the ID is {new_id}')
        else:
            return template('new_task.tpl')


A new route is created, assigned to ``/new``, which accepts GET as well as POST requests. Inside the function ``new_task`` assigned to this route, the ``request`` object introduced in the previous section is checked to see whether a GET or a POST request was received:

.. code-block:: python

    ...
    if request.POST:
        #The code here is only executed if POST data, e.g. from a
        #HTML form, is inside the request.
    else:
        #the code here is only executed if no POST data was received.
    ...


``request.forms`` is the attribute which holds data submitted by an HTML from. ``request.forms.task`` holds the data from the field ``task`` of the form. As ``task`` is a string, the ``strip`` method is additionally applied to remove any white spaces before or after the string.

Then the new task is written to the database, and the ID of the new task is return. If no POST data was received, the template ``new_task`` is send. This template holds the HTML form to enter a new task. The template looks like this:

.. code-block:: html

    %#template of the form for a new task
    % rebase('base.tpl')
    <p>Add a new task to the ToDo list:</p>
    <form action="/new" method="post">
      <p><input type="text" size="100" maxlength="100" name="task"></p>
      <p><input type="submit" name="save" value="save"></p>
    </form>


.. rubric:: Editing Existing Items

The last piece missing to complete the simple ToDo app is the functionality to edit existing tasks in the database. Either to change their status or to update the text of a task.

By using only the routes introduced so far it is possible, but will be quite tricky. To make things easier, let's use Bottle's feature called `dynamic routes`_ , which makes this coding task quite easy.

The basic statement for a dynamic route looks like this::

.. code-block:: python

    @app.route('some_route/<something>')

``<something>`` is called a "wildcard". Furthermore, the value of the wildcard ``something`` is be passed to the function assigned to this route, so the data can be processed within the function. Optionally, a filter can be applied to the wildcard. The filter does one thing: it checks whether the wildcard matches a certain type of data, e.g. an integer value or a regular expression. If not, an error is raised.

The ``int`` filter is used for this route, which checks at first if the wildcard matches an integer value and. If yes, the wildcard string is converted to a Python integer object.

The complete route for editing a task looks like this:

.. code-block:: python

    @app.route('/edit/<number:int>', method=['GET', 'POST'])
    def edit_task(number):
        if request.POST:
            new_data = request.forms.task.strip()
            status = request.forms.status.strip()
            if status == 'open':
                status = 1
            else:
                status = 0
            with sqlite3.connect('todo.db') as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE todo SET task = ?, status = ? WHERE id LIKE ?", (new_data, status, number))
            return template('message.tpl',
                message=f'The task number {number} was successfully updated')
        else:
            with sqlite3.connect('todo.db') as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT task FROM todo WHERE id LIKE ?", (number,))
                current_data = cursor.fetchone()
            return template('edit_task', current_data=current_data, number=number)


A lot of the code's logic is pretty similar to the ``/new`` route and the corresponding ``new_task`` function: the route accepts GET and POST requests and, depending on the request, either sends the template ``edit_task`` or updates a task in the database according to the form data received.

What's new here is the dynamic routing ``@app.route('/edit/<number:int>' ...)`` which accepts one wildcard, supposed to be an integer value. The wildcard is assigned to the variable ``number``, which is also expected by the function ``edit_task``. So e.g. opening the URL ``http:/127.0.0.1:8080/edit/2`` would open the task with the ID for editing. In case no number is passed, either because of omitting the parameter or passing a string which is not an integer only, an error will be raised.

The template ``edit_task.tpl`` called within the function looks like this:

.. code-block:: html

    %#template for editing a task
    %#the template expects to receive a value for "number" as well a "old", the text of the selected ToDo item
    % rebase('base.tpl')
    <p>Edit the task with ID = {{number}}</p>
    <form action="/edit/{{number}}" method="post">
      <p>
      <input type="text" name="task" value="{{current_data[0]}}" size="100" maxlength="100">
      <select name="status">
        <option>open</option>
        <option>closed</option>
      </select>
      </p>
      <p><input type="submit" name="save" value="save"></p>
    </form>


The next section "Returning JSON Data" shows another example of a dynamic route using a filter.


.. rubric:: Returning JSON Data

A nice feature of Bottle is that it automatically generates a response with content type JSON_ is a Python dictionary is passed to the return statement of a route. Which makes it very easy to build web-based APIs with Bottle. Let's build a route for the ToDo app application which returns a task from the database as JSON. This is pretty straight forward; the code looks like this:

.. code-block:: python

    @app.route('/as_json/<number:re:[0-9]+>')
    def task_as_json(number):
        with sqlite3.connect('todo.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, task, status FROM todo WHERE id LIKE ?", (number,))
            result = cursor.fetchone()
        if not result:
            return {'task': 'This task ID number does not exist!'}
        else:
            return {'id': result[0], 'task': result[1], 'status': result[2]}


As can be seen, the only difference is the dictionary returned. Either resulting in a JSON object with the three keys "id", "task" and "status" or with one key named "task" only, having the error message as the value.

Additionally, the ``re`` filter applying a RegEx is used for the wildcard ``number`` of this route. Of course the ``int`` filter as used for the `/edit`` route could be used here, too (and would be probably more appropriate), but the RegEx filter is used just to showcase it here. The filter can basically handle any regular expression Python's `RegEx module`_ can handle.


.. rubric:: Returning Static Files

Sometimes it may become necessary to associate a route not to a Python function but just return a static file. A static file could be e.g. a JPG or PNG graphics, a PDF file or a static HTML file instead of a template. In any case, another import needs to be added first

.. code:: python

    from bottle import static_file


to the code to import Bottle's function ``static_file``, which handles sending static files. Let's assume all the static files are located in a subdirectory named ``static`` relative to the application. The code to serve static files from there looks as follows:

.. code-block:: python

    ...
    from pathlib import Path

    ABSOLUTE_APPLICATION_PATH = Path(__file__).parent[0]
    ...

    @app.route('/static/<filepath:path>')
    def send_static_file(filepath):
        ROOT_PATH = ABSOLUTE_APPLICATION_PATH / 'static'
        return static_file(filepath,
                           root=ROOT_PATH)


The ``Path`` class of Python's pathlib_ module is imported and then used to determine the absolute path where the application is located. This is necessary, as the ``static_file`` method requires an absolute path to the static content. Of course, the path could be hard coded into the code, but using pathlib is more elegant.

The route ``/static/<filepath:path>`` makes use of Bottle's build-in ``path`` filter and the wildcard holding the name of the file to be served is assigned to the ``filepath``. As can be seen from the code, the ``static_file`` function requires the name of the file to be served as well as the root path to the directory where the file is located.

Bottle guesses the MIME-type of the file automatically. But it can also be stated explicitly by adding a third argument to ``static_file``, e.g. ``mimetype='text/html'`` for serving a static HTML file. More information on ``static_file`` can be found in the `static_file documentation`_ .


.. rubric:: Catching Errors

When trying to open a webpage which doesn't exist, a "404 Not Found" error message is displayed in the browser. Bottle offers an option to catch these errors and return a customized error message instead. This works as follows:

.. code-block:: python

    @app.error(404)
    def error_404(error):
        return 'Sorry, this page does not exist!'


In the event a 404 Not Found error occurs, the function decorated with ``app.error(404)`` is run and returns the customized error message of choice. The ``error`` argument passed to the function holds a tuple with two elements: the first element is the actual error code and the second element the actual error message. This tuple can be used within the function but does not have to. Of course, if is also possible, like for all routes, to assign more than one error / route to a function, like e.g.:

.. code-block:: python

    @app.error(404)
    @error(403)
    def something_went_wrong(error):
        return f'{error}: There is something wrong!'


.. rubric:: Create a Redirect (Bonus Section)

Although the ToDo application works just fine, it still has one little flaw: When trying to open ``127.0.01:8080`` in the browser, the root route, a 404 error will occur, as no route is established for ```/``.  Which is not too much of a problem, but at least a little bit unexpected. Of course this could be changed by modifying the route ``app.route('/todo')`` to ``app.route('/')``. Or, if the /todo route should be kept, a redirect can be added to the code. Again, this is pretty straight forward:

.. code-block:: python

    ...
    from bottle import redirect
    ...

    @app.route('/')
    def index():
        redirect('/todo')


At first, the (so far) missing route ``app.route('/')`` is added, decorating the ``index()`` function. It has only one line of code, redirecting the browser to the todo route. When opening the URL ``127.0.0.1:8080``, the browser will be automatically redirect to ``http://127.0.0.1:8080/todo``.


.. rubric:: Summary

After going through all the sections above, a brief understanding on how Bottle works is hopefully achieved so new Bottle-based web applications can be written.

The following chapter will be show how to serve Bottle with web servers with perform better on a higher load / more web traffic than the one used so far.


Deployment
===========

So far, the built-in development server of Bottle was used, which based on the `WSGI reference Server`_ included in Python. Although this server is perfectly fine and very handy for development purposes, it is not really suitable to serve "real world" applications. But before looking at the alternatives, let's have a look how to tweak the settings of the build-in server first.


.. rubric:: Running Bottle on a different port and IP

As a standard, Bottle serves on the IP address 127.0.0.1, also known as ``localhost``, and on port ``8080``. To modify the setting is pretty simple, as additional parameters can be passed to Bottle's ``run()`` function to change the port and the address.

In the very first "Hello World" example, the server is started with ``app.run(host='127.0.0.1', port=8080)``. To change the port, just pass a different port number to the ``port`` argument. To change the IP address which Bottle is listening on, just pass a different IP address to the ``host`` argument.

.. warning::

    It is highly recommended *not* to run an application based on Bottle - or any web application - with Root / administrator rights! The whole code is executed with elevated rights, which gives a (much) higher risk to harm the system in case of programming mistakes. Plus, in case an outside person can capture the application, e.g. by utilizes a bug in the code, this person may be able to work with elevated rights on the server. It is highly recommended to run Bottle with user rights, probably in case of a real application, by a dedicated user specifically set-up for this. In case the application should listen on a privileged port like 80 and / or 443, it is a common and a well-established practice to serve Bottle - or any WSGI-based application - with an WSGI application server with user rights on an unprivileged port locally and use a reverse proxy web server in front of the WSGI application server. More on this below.


.. rubric:: Running Bottle with a different server

As said above, the build-in server is perfectly suitable for local development, personal use or a very small group of people within an internal network. For everything else, the development server may become a bottleneck, as it is single-threaded, thus it can only serve one request at a time. Plus, it may not be robust enough in general.

Bottle comes with a range of `server adapters`_ . To run the Bottle application with a different server than the build-in development server, simple pass the ``server`` argument to the run function. For the following example, the Waitress_ WSGI application server from the Pylons project is used. Waitress works equally good on Linux, macOS and Windows.

.. note::

    Although Bottle comes with a variety of server adapters, each server except the build-in server must be installed separately. The servers are *not* installed as a dependency of Bottle!

To install Waitress, go the venv in which Bottle is installed and run:

.. code:: shell

    pip3 install waitress


To server the application via Waitress, just use Bottle's server adapter for Waitress by changing the ``app.run`` to:

.. code:: python

    app.run(host='127.0.0.1', port=8080, server='waitress')


After starting the application with ``python todo.py``, a line in the output like ``Bottle v0.13.2 server starting up (using WaitressServer())...`` should be printed. Which confirms that the Waitress server instead of the WSGIRefServer is used.

This works exactly the same way with other servers supported by Bottle. However, there is one potential downside with this: it is not possible to pass any extra arguments to the server. Which may be necessary in many "real world" scenarios. A solution to that is shown in the next section.


.. rubric:: Serving a Bottle App with a WSGI Application Server

Like any other Python WSGI framework, an application written with a Bottle has a so-called entry point, which can be passed to a WSGI Application server, which then serves the web application. In case of Bottle, the entry points is the ``app`` instance created with the code line ``app = Bottle()``.

Sticking to Waitress (as used already in the previous section), serving the application works as follows:

.. code:: shell

    waitress-serve todo:app


whereas ``todo`` is the name of the file holding the Bottle application and ``app`` is the entry point, the instance of Bottle. Calling the WSGI application server directly allows to pass as many arguments to the server as need, e.g.

.. code:: shell

    waitress-serve --listen:127.0.0.1:8080 --threads=2 todo:app


Final Words
============

This is the end of this tutorial for Bottle. The basic concepts of Bottle are shown and a first application utilizin the Bottle WSGI framework was written. Additionally, it was shown how to serve a Bottle application for real applications with a WSGI application server.

As said in the introduction, this tutorial is not showing all possibilities Bottle offers. What was skipped here is e.g. receiving file objects and streams and how to handle authentication data. For a complete overview of all features of Bottle, please refer to the full `Bottle documentation`_ .


Complete Example Listing
=========================

As the ToDo list example was developed piece by piece, here is the complete listing and the templates:

Main code for the application ``todo.py``:

.. code-block:: python

    import sqlite3
    from pathlib import Path
    from bottle import Bottle, template, request, redirect


    ABSOLUTE_APPLICATION_PATH = Path(__file__).parents[0]
    app = Bottle()

    @app.route('/')
    def index():
        redirect('/todo')


    @app.get('/todo')
    def todo_list():
        show  = request.query.show or 'open'
        match show:
            case 'open':
                db_query = "SELECT id, task, status FROM todo WHERE status LIKE '1'"
            case 'closed':
                db_query = "SELECT id, task, status FROM todo WHERE status LIKE '0'"
            case 'all':
                db_query = "SELECT id, task, status FROM todo"
            case _:
                return template('message.tpl',
                    message = 'Wrong query parameter: show must be either open, closed or all.')
        with sqlite3.connect('todo.db') as connection:
            cursor = connection.cursor()
            cursor.execute(db_query)
            result = cursor.fetchall()
        output = template('show_tasks.tpl', rows=result)
        return output


    @app.route('/new', method=['GET', 'POST'])
    def new_task():
        if request.POST:
            new_task = request.forms.task.strip()
            with sqlite3.connect('todo.db') as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO todo (task,status) VALUES (?,?)", (new_task, 1))
                new_id = cursor.lastrowid
            return template('message.tpl',
                message=f'The new task was inserted into the database, the ID is {new_id}')
        else:
            return template('new_task.tpl')


    @app.route('/edit/<number:int>', method=['GET', 'POST'])
    def edit_task(number):
        if request.POST:
            new_data = request.forms.task.strip()
            status = request.forms.status.strip()
            if status == 'open':
                status = 1
            else:
                status = 0
            with sqlite3.connect('todo.db') as connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE todo SET task = ?, status = ? WHERE id LIKE ?", (new_data, status, number))
            return template('message.tpl',
                message=f'The task number {number} was successfully updated')
        else:
            with sqlite3.connect('todo.db') as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT task FROM todo WHERE id LIKE ?", (number,))
                current_data = cursor.fetchone()
            return template('edit_task', current_data=current_data, number=number)


    @app.route('/details/<task:re:[0-9]+>')
    def show_item(task):
            with sqlite3.connect('todo.db') as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT task, status FROM todo WHERE id LIKE ?", (task,))
                result = cursor.fetchone()
            if not result:
                return template('message.tpl',
                message = f'The task number {item} does not exist!')
            else:
                return template('message.tpl',
                message = f'Task: {result[0]}, status: {result[1]}')


    @app.route('/as_json/<number:re:[0-9]+>')
    def task_as_json(number):
        with sqlite3.connect('todo.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, task, status FROM todo WHERE id LIKE ?", (number,))
            result = cursor.fetchone()
        if not result:
            return {'task': 'This task IF number does not exist!'}
        else:
            return {'id': result[0], 'task': result[1], 'status': result[2]}


    @app.route('/static/<filepath:path>')
    def send_static_file(filepath):
        ROOT_PATH = ABSOLUTE_APPLICATION_PATH / 'static'
        return static_file(filepath, root= ROOT_PATH)


    @app.error(404)
    def mistake404(error):
        return 'Sorry, this page does not exist!'


    if __name__ == '__main__':
        app.run(host='127.0.0.1', port=8080, debug=True, reloader=True)
        # remember to remove reloader=True and debug=True when moving
        # the application from development to a productive environment


Template ``base.tpl``:

.. code-block:: html

    <!doctype html>
    <html lang="en-US">
      <head>
        <meta charset="utf-8" />
        <title>ToDo App powered by Bottle</title>
      </head>
      <body>
        {{!base}}
      </body>
    </html>


Template ``show_tasks.tpl``:

.. code-block:: html

    %#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
    % rebase('base.tpl')
    <p>The open ToDo tasks are as follows:</p>
    <table border="1">
    %for row in rows:
      <tr>
      %for col in row:
        <td>{{col}}</td>
      %end
      </tr>
    %end
    </table>
    <p><a href="/new">Add a new task</a></p>


Template ``message.tpl``:

.. code-block:: html

    % rebase('base.tpl')
    <p>{{ message }}</p>
    <p><a href="/todo">Back to main page</p>


Template ``new_task.tpl``:

.. code-block:: html

    %#template of the form for a new task
    % rebase('base.tpl')
    <p>Add a new task to the ToDo list:</p>
    <form action="/new" method="post">
      <p><input type="text" size="100" maxlength="100" name="task"></p>
      <p><input type="submit" name="save" value="save"></p>
    </form>


Template ``edit_task.tpl``:

.. code-block:: html

    %#template for editing a task
    %#the template expects to receive a value for "no" as well a "old", the text of the selected ToDo item
    <p>Edit the task with ID = {{no}}</p>
    <form action="/edit/{{no}}" method="get">
      <input type="text" name="task" value="{{old[0]}}" size="100" maxlength="100">
      <select name="status">
        <option>open</option>
        <option>closed</option>
      </select>
      <br>
      <input type="submit" name="save" value="save">
    </form>
