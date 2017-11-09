.. _Bottle: http://bottle.paws.org
.. _Python: http://www.python.org
.. _SQLite: http://www.sqlite.org
.. _Windows: http://www.sqlite.org/download.html
.. _PySQLite: http://pypi.python.org/pypi/pysqlite/
.. _`decorator statement`: http://docs.python.org/glossary.html#term-decorator
.. _`Python DB API`: http://www.python.org/dev/peps/pep-0249/
.. _`WSGI reference Server`: http://docs.python.org/library/wsgiref.html#module-wsgiref.simple_server
.. _Cherrypy: http://www.cherrypy.org/
.. _Fapws3: http://github.com/william-os4y/fapws3
.. _Flup: https://www.saddi.com/software/flup/
.. _Paste: http://pythonpaste.org/
.. _Apache: http://www.apache.org
.. _`Bottle documentation`: http://bottlepy.org/docs/dev/tutorial.html
.. _`mod_wsgi`: http://code.google.com/p/modwsgi/
.. _`json`: http://www.json.org

===============================
Tutorial: Todo-List Application
===============================

.. note::

   This tutorial is a work in progress and written by `noisefloor <http://github.com/noisefloor>`_.


This tutorial should give a brief introduction to the Bottle_ WSGI Framework. The main goal is to be able, after reading through this tutorial, to create a project using Bottle. Within this document, not all abilities will be shown, but at least the main and important ones like routing, utilizing the Bottle template abilities to format output and handling GET / POST parameters.

To understand the content here, it is not necessary to have a basic knowledge of WSGI, as Bottle tries to keep WSGI away from the user anyway. You should have a fair understanding of the Python_ programming language. Furthermore, the example used in the tutorial retrieves and stores data in a SQL database, so a basic idea about SQL helps, but is not a must to understand the concepts of Bottle. Right here, SQLite_ is used. The output of Bottle sent to the browser is formatted in some examples by the help of HTML. Thus, a basic idea about the common HTML tags does help as well.

For the sake of introducing Bottle, the Python code "in between" is kept short, in order to keep the focus. Also all code within the tutorial is working fine, but you may not necessarily use it "in the wild", e.g. on a public web server. In order to do so, you may add e.g. more error handling, protect the database with a password, test and escape the input etc.

.. contents:: Table of Contents

Goals
===========

At the end of this tutorial, we will have a simple, web-based ToDo list. The list contains a text (with max 100 characters) and a status (0 for closed, 1 for open) for each item. Through the web-based user interface, open items can be view and edited and new items can be added.

During development, all pages will be available on ``localhost`` only, but later on it will be shown how to adapt the application for a "real" server, including how to use with Apache's mod_wsgi.

Bottle will do the routing and format the output, with the help of templates. The items of the list will be stored inside a SQLite database. Reading and  writing the database will be done by Python code.

We will end up with an application with the following pages and functionality:

 * start page ``http://localhost:8080/todo``
 * adding new items to the list: ``http://localhost:8080/new``
 * page for editing items: ``http://localhost:8080/edit/<no:int>``
 * catching errors

Before We Start...
====================


.. rubric:: Install Bottle

Assuming that you have a fairly new installation of Python (version 2.5 or higher), you only need to install Bottle in addition to that. Bottle has no other dependencies than Python itself.

You can either manually install Bottle or use Python's easy_install: ``easy_install bottle``


.. rubric:: Further Software Necessities

As we use SQLite3 as a database, make sure it is installed. On Linux systems, most distributions have SQLite3 installed by default. SQLite is available for Windows and MacOS X as well and the `sqlite3` module is part of the python standard library.

.. rubric:: Create An SQL Database

First, we need to create the database we use later on. To do so, save the following script in your project directory and run it with python. You can use the interactive interpreter too::

    import sqlite3
    conn = sqlite3.connect('todo.db') # Warning: This file is created in the current directory
    conn.execute("CREATE TABLE todo (id INTEGER PRIMARY KEY, task char(100) NOT NULL, status bool NOT NULL)")
    conn.execute("INSERT INTO todo (task,status) VALUES ('Read A-byte-of-python to get a good introduction into Python',0)")
    conn.execute("INSERT INTO todo (task,status) VALUES ('Visit the Python website',1)")
    conn.execute("INSERT INTO todo (task,status) VALUES ('Test various editors for and check the syntax highlighting',1)")
    conn.execute("INSERT INTO todo (task,status) VALUES ('Choose your favorite WSGI-Framework',0)")
    conn.commit()

This generates a database-file `todo.db` with tables called ``todo`` and three columns ``id``, ``task``, and ``status``. ``id`` is a unique id for each row, which is used later on to reference the rows. The column ``task`` holds the text which describes the task, it can be max 100 characters long. Finally, the column ``status`` is used to mark a task as open (value 1) or closed (value 0).

Using Bottle for a Web-Based ToDo List
================================================

Now it is time to introduce Bottle in order to create a web-based application. But first, we need to look into a basic concept of Bottle: routes.


.. rubric:: Understanding routes

Basically, each page visible in the browser is dynamically generated when the page address is called. Thus, there is no static content. That is exactly what is called a "route" within Bottle: a certain address on the server. So, for example, when the page ``http://localhost:8080/todo`` is called from the browser, Bottle "grabs" the call and checks if there is any (Python) function defined for the route "todo". If so, Bottle will execute the corresponding Python code and return its result.


.. rubric:: First Step - Showing All Open Items

So, after understanding the concept of routes, let's create the first one. The goal is to see all open items from the ToDo list::

    import sqlite3
    from bottle import route, run

    @route('/todo')
    def todo_list():
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT id, task FROM todo WHERE status LIKE '1'")
        result = c.fetchall()
        return str(result)

    run()

Save the code a ``todo.py``, preferably in the same directory as the file ``todo.db``. Otherwise, you need to add the path to ``todo.db`` in the ``sqlite3.connect()`` statement.

Let's have a look what we just did: We imported the necessary module ``sqlite3`` to access to SQLite database and from Bottle we imported ``route`` and ``run``. The ``run()`` statement simply starts the web server included in Bottle. By default, the web server serves the pages on localhost and port 8080. Furthermore, we imported ``route``, which is the function responsible for Bottle's routing. As you can see, we defined one function, ``todo_list()``, with a few lines of code reading from the database. The important point is the `decorator statement`_ ``@route('/todo')`` right before the ``def todo_list()`` statement. By doing this, we bind this function to the route ``/todo``, so every time the browsers calls ``http://localhost:8080/todo``, Bottle returns the result of the function ``todo_list()``. That is how routing within bottle works.

Actually you can bind more than one route to a function. So the following code::

    @route('/todo')
    @route('/my_todo_list')
    def todo_list():
        ...

will work fine, too. What will not work is to bind one route to more than one function.

What you will see in the browser is what is returned, thus the value given by the ``return`` statement. In this example, we need to convert ``result`` in to a string by ``str()``, as Bottle expects a string or a list of strings from the return statement. But here, the result of the database query is a list of tuples, which is the standard defined by the `Python DB API`_.

Now, after understanding the little script above, it is time to execute it and watch the result yourself. Remember that on Linux- / Unix-based systems the file ``todo.py`` needs to be executable first. Then, just run ``python todo.py`` and call the page ``http://localhost:8080/todo`` in your browser. In case you made no mistake writing the script, the output should look like this::

    [(2, u'Visit the Python website'), (3, u'Test various editors for and check the syntax highlighting')]

If so - congratulations! You are now a successful user of Bottle. In case it did not work and you need to make some changes to the script, remember to stop Bottle serving the page, otherwise the revised version will not be loaded.

Actually, the output is not really exciting nor nice to read. It is the raw result returned from the SQL query.

So, in the next step we format the output in a nicer way. But before we do that, we make our life easier.


.. rubric:: Debugging and Auto-Reload

Maybe you already noticed that Bottle sends a short error message to the browser in case something within the script is wrong, e.g. the connection to the database is not working. For debugging purposes it is quite helpful to get more details. This can be easily achieved by adding the following statement to the script::

    from bottle import run, route, debug
    ...
    #add this at the very end:
    debug(True)
    run()

By enabling "debug", you will get a full stacktrace of the Python interpreter, which usually contains useful information for finding bugs. Furthermore, templates (see below) are not cached, thus changes to templates will take effect without stopping the server.

.. warning::

   That ``debug(True)`` is supposed to be used for development only, it should *not* be used in production environments.



Another quite nice feature is auto-reloading, which is enabled by modifying the ``run()`` statement to

::

    run(reloader=True)

This will automatically detect changes to the script and reload the new version once it is called again, without the need to stop and start the server.

Again, the feature is mainly supposed to be used while developing, not on production systems.


.. rubric:: Bottle Template To Format The Output

Now let's have a look at casting the output of the script into a proper format.

Actually Bottle expects to receive a string or a list of strings from a function and returns them by the help of the built-in server to the browser. Bottle does not bother about the content of the string itself, so it can be text formatted with HTML markup, too.

Bottle brings its own easy-to-use template engine with it. Templates are stored as separate files having a ``.tpl`` extension. The template can be called then from within a function. Templates can contain any type of text (which will be most likely HTML-markup mixed with Python statements). Furthermore, templates can take arguments, e.g. the result set of a database query, which will be then formatted nicely within the template.

Right here, we are going to cast the result of our query showing the open ToDo items into a simple table with two columns: the first column will contain the ID of the item, the second column the text. The result set is, as seen above, a list of tuples, each tuple contains one set of results.

To include the template in our example, just add the following lines::

    from bottle import route, run, debug, template
    ...
    result = c.fetchall()
    c.close()
    output = template('make_table', rows=result)
    return output
    ...

So we do here two things: first, we import ``template`` from Bottle in order to be able to use templates. Second, we assign the output of the template ``make_table`` to the variable ``output``, which is then returned. In addition to calling the template, we assign ``result``, which we received from the database query, to the variable ``rows``, which is later on used within the template. If necessary, you can assign more than one variable / value to a template.

Templates always return a list of strings, thus there is no need to convert anything. We can save one line of code by writing ``return template('make_table', rows=result)``, which gives exactly the same result as above.

Now it is time to write the corresponding template, which looks like this::

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

Save the code as ``make_table.tpl`` in the same directory where ``todo.py`` is stored.

Let's have a look at the code: every line starting with % is interpreted as Python code. Because it is effectively Python, only valid Python statements are allowed. The template will raise exceptions, just as any other Python code would. The other lines are plain HTML markup.

As you can see, we use Python's ``for`` statement two times, in order to go through ``rows``. As seen above, ``rows`` is a variable which holds the result of the database query, so it is a list of tuples. The first ``for`` statement accesses the tuples within the list, the second one the items within the tuple, which are put each into a cell of the table. It is important that you close all ``for``, ``if``, ``while`` etc. statements with ``%end``, otherwise the output may not be what you expect.

If you need to access a variable within a non-Python code line inside the template, you need to put it into double curly braces. This tells the template to insert the actual value of the variable right in place.

Run the script again and look at the output. Still not really nice, but at least more readable than the list of tuples. You can spice-up the very simple HTML markup above, e.g. by using in-line styles to get a better looking output.


.. rubric:: Using GET and POST Values

As we can review all open items properly, we move to the next step, which is adding new items to the ToDo list. The new item should be received from a regular HTML-based form, which sends its data by the GET method.

To do so, we first add a new route to our script and tell the route that it should get GET data::

    from bottle import route, run, debug, template, request
    ...
    return template('make_table', rows=result)
    ...

    @route('/new', method='GET')
    def new_item():

        new = request.GET.task.strip()

        conn = sqlite3.connect('todo.db')
        c = conn.cursor()

        c.execute("INSERT INTO todo (task,status) VALUES (?,?)", (new, 1))
        new_id = c.lastrowid

        conn.commit()
        c.close()

        return '<p>The new task was inserted into the database, the ID is %s</p>' % new_id

To access GET (or POST) data, we need to import ``request`` from Bottle. To assign the actual data to a variable, we use the statement ``request.GET.task.strip()`` statement, where ``task`` is the name of the GET data we want to access. That's all. If your GET data has more than one variable, multiple ``request.GET.get()`` statements can be used and assigned to other variables.

The rest of this piece of code is just processing of the gained data: writing to the database, retrieve the corresponding id from the database and generate the output.

But where do we get the GET data from? Well, we can use a static HTML page holding the form. Or, what we do right now, is to use a template which is output when the route ``/new`` is called without GET data.

The code needs to be extended to::

    ...
    @route('/new', method='GET')
    def new_item():

        if request.GET.save:

            new = request.GET.task.strip()
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()

            c.execute("INSERT INTO todo (task,status) VALUES (?,?)", (new,1))
            new_id = c.lastrowid

            conn.commit()
            c.close()

            return '<p>The new task was inserted into the database, the ID is %s</p>' % new_id
        else:
            return template('new_task.tpl')


``new_task.tpl`` looks like this::

    <p>Add a new task to the ToDo list:</p>
    <form action="/new" method="GET">
      <input type="text" size="100" maxlength="100" name="task">
      <input type="submit" name="save" value="save">
    </form>

That's all. As you can see, the template is plain HTML this time.

Now we are able to extend our to do list.

By the way, if you prefer to use POST data: this works exactly the same way, just use ``request.POST.get()`` instead.


.. rubric:: Editing Existing Items

The last point to do is to enable editing of existing items.

By using only the routes we know so far it is possible, but may be quite tricky. But Bottle knows something called "dynamic routes", which makes this task quite easy.

The basic statement for a dynamic route looks like this::

    @route('/myroute/<something>')

This tells Bottle to accept for ``<something>`` any string up to the next slash. Furthermore, the value of ``something`` will be passed to the function assigned to that route, so the data can be processed within the function, like this::

    @route('/edit/<no:int>', method='GET')
    def edit_item(no):

        if request.GET.save:
            edit = request.GET.task.strip()
            status = request.GET.status.strip()

            if status == 'open':
                status = 1
            else:
                status = 0

            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("UPDATE todo SET task = ?, status = ? WHERE id LIKE ?", (edit, status, no))
            conn.commit()

            return '<p>The item number %s was successfully updated</p>' % no
        else:
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("SELECT task FROM todo WHERE id LIKE ?", (str(no),))
            cur_data = c.fetchone()

            return template('edit_task', old=cur_data, no=no)

It is basically pretty much the same what we already did above when adding new items, like using ``GET`` data etc. The main addition here is using the dynamic route ``<no:int>``, which here passes the number to the corresponding function. As you can see, ``no`` is integer ID and used within the function to access the right row of data within the database.


The template ``edit_task.tpl`` called within the function looks like this::

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

Again, this template is a mix of Python statements and HTML, as already explained above.

A last word on dynamic routes: you can even use a regular expression for a dynamic route, as demonstrated later.


.. rubric:: Validating Dynamic Routes

Using dynamic routes is fine, but for many cases it makes sense to validate the dynamic part of the route. For example, we expect an integer number in our route for editing above. But if a float, characters or so are received, the Python interpreter throws an exception, which is not what we want.

For those cases, Bottle offers the ``<name:int>`` wildcard filter, which matches (signed) digits and converts the value to integer. In order to apply the wildcard filter, extend the code as follows::

    from bottle import route, run, debug, template, request
    ...
    @route('/edit/<no:int>', method='GET')
    def edit_item(no):
    ...

Save the code and call the page again using incorrect value for ``<no:int>``, e.g. a float. You will receive not an exception, but a "404 Not Found" error.


.. rubric:: Dynamic Routes Using Regular Expressions

Bottle can also handle dynamic routes, where the "dynamic part" of the route can be a regular expression.

So, just to demonstrate that, let's assume that all single items in our ToDo list should be accessible by their plain number, by a term like e.g. "item1". For obvious reasons, you do not want to create a route for every item. Furthermore, the simple dynamic routes do not work either, as part of the route, the term "item" is static.

As said above, the solution is a regular expression::

    @route('/item<item:re:[0-9]+>')
    def show_item(item):
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT task FROM todo WHERE id LIKE ?", (item,))
        result = c.fetchall()
        c.close()
        if not result:
            return 'This item number does not exist!'
        else:
            return 'Task: %s' % result[0]


The line ``@route(/item<item:re:[0-9]+>)`` starts like a normal route, but the third part of the wildcard is interpreted as a regular expression, which is the dynamic part of the route. So in this case, we want to match any digit between 0 and 9. The following function "show_item" just checks whether the given item is present in the database or not. In case it is present, the corresponding text of the task is returned. As you can see, only the regular expression part of the route is passed forward. Furthermore, it is always forwarded as a string, even if it is a plain integer number, like in this case.


.. rubric:: Returning Static Files

Sometimes it may become necessary to associate a route not to a Python function, but just return a static file. So if you have for example a help page for your application, you may want to return this page as plain HTML. This works as follows::

    from bottle import route, run, debug, template, request, static_file

    @route('/help')
    def help():
        return static_file('help.html', root='/path/to/file')

At first, we need to import the ``static_file`` function from Bottle. As you can see, the ``return static_file`` statement replaces the ``return`` statement. It takes at least two arguments: the name of the file to be returned and the path to the file. Even if the file is in the same directory as your application, the path needs to be stated. But in this case, you can use ``'.'`` as a path, too. Bottle guesses the MIME-type of the file automatically, but in case you like to state it explicitly, add a third argument to ``static_file``, which would be here ``mimetype='text/html'``. ``static_file`` works with any type of route, including the dynamic ones.


.. rubric:: Returning JSON Data

There may be cases where you do not want your application to generate the output directly, but return data to be processed further on, e.g. by JavaScript. For those cases, Bottle offers the possibility to return JSON objects, which is sort of standard for exchanging data between web applications. Furthermore, JSON can be processed by many programming languages, including Python

So, let's assume we want to return the data generated in the regular expression route example as a JSON object. The code looks like this::

    @route('/json<json:re:[0-9]+>')
    def show_json(json):
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT task FROM todo WHERE id LIKE ?", (json,))
        result = c.fetchall()
        c.close()

        if not result:
            return {'task': 'This item number does not exist!'}
        else:
            return {'task': result[0]}

As you can, that is fairly simple: just return a regular Python dictionary and Bottle will convert it automatically into a JSON object prior to sending. So if you e.g. call "http://localhost/json1" Bottle should in this case return the JSON object ``{"task": ["Read A-byte-of-python to get a good introduction into Python"]}``.



.. rubric:: Catching Errors

The next step may is to catch the error with Bottle itself, to keep away any type of error message from the user of your application. To do that, Bottle has an "error-route", which can be a assigned to a HTML-error.

In our case, we want to catch a 403 error. The code is as follows::

    from bottle import error

    @error(403)
    def mistake(code):
        return 'The parameter you passed has the wrong format!'

So, at first we need to import ``error`` from Bottle and define a route by ``error(403)``, which catches all "403 forbidden" errors. The function "mistake" is assigned to that. Please note that ``error()`` always passes the error-code to the function - even if you do not need it. Thus, the function always needs to accept one argument, otherwise it will not work.

Again, you can assign more than one error-route to a function, or catch various errors with one function each. So this code::

    @error(404)
    @error(403)
    def mistake(code):
        return 'There is something wrong!'

works fine, the following one as well::

    @error(403)
    def mistake403(code):
        return 'The parameter you passed has the wrong format!'

    @error(404)
    def mistake404(code):
        return 'Sorry, this page does not exist!'


.. rubric:: Summary

After going through all the sections above, you should have a brief understanding how the Bottle WSGI framework works. Furthermore you have all the knowledge necessary to use Bottle for your applications.

The following chapter give a short introduction how to adapt Bottle for larger projects. Furthermore, we will show how to operate Bottle with web servers which perform better on a higher load / more web traffic than the one we used so far.

Server Setup
================================

So far, we used the standard server used by Bottle, which is the `WSGI reference Server`_ shipped along with Python. Although this server is perfectly suitable for development purposes, it is not really suitable for larger applications. But before we have a look at the alternatives, let's have a look how to tweak the settings of the standard server first.


.. rubric:: Running Bottle on a different port and IP

As standard, Bottle serves the pages on the IP address 127.0.0.1, also known as ``localhost``, and on port ``8080``. To modify the setting is pretty simple, as additional parameters can be passed to Bottle's ``run()`` function to change the port and the address.

To change the port, just add ``port=portnumber`` to the run command. So, for example::

    run(port=80)

would make Bottle listen to port 80.

To change the IP address where Bottle is listening::

    run(host='123.45.67.89')

If needed, both parameters can be combined, like::

   run(port=80, host='123.45.67.89')

The ``port`` and ``host`` parameter can also be applied when Bottle is running with a different server, as shown in the following section.


.. rubric:: Running Bottle with a different server

As said above, the standard server is perfectly suitable for development, personal use or a small group of people only using your application based on Bottle. For larger tasks, the standard server may become a bottleneck, as it is single-threaded, thus it can only serve one request at a time.

But Bottle has already various adapters to multi-threaded servers on board, which perform better on higher load. Bottle supports Cherrypy_, Fapws3_, Flup_ and Paste_.

If you want to run for example Bottle with the Paste server, use the following code::

    from bottle import PasteServer
    ...
    run(server=PasteServer)

This works exactly the same way with ``FlupServer``, ``CherryPyServer`` and ``FapwsServer``.


.. rubric:: Running Bottle on Apache with mod_wsgi

Maybe you already have an Apache_ or you want to run a Bottle-based application large scale - then it is time to think about Apache with mod_wsgi_.

We assume that your Apache server is up and running and mod_wsgi is working fine as well. On a lot of Linux distributions, mod_wsgi can be easily installed via whatever package management system is in use.

Bottle brings an adapter for mod_wsgi with it, so serving your application is an easy task.

In the following example, we assume that you want to make your application "ToDo list" accessible through ``http://www.mypage.com/todo`` and your code, templates and SQLite database are stored in the path ``/var/www/todo``.

When you run your application via mod_wsgi, it is imperative to remove the ``run()`` statement from your code, otherwise it won't work here.

After that, create a file called ``adapter.wsgi`` with the following content::

    import sys, os, bottle

    sys.path = ['/var/www/todo/'] + sys.path
    os.chdir(os.path.dirname(__file__))

    import todo # This loads your application

    application = bottle.default_app()

and save it in the same path, ``/var/www/todo``. Actually the name of the file can be anything, as long as the extension is ``.wsgi``. The name is only used to reference the file from your virtual host.

Finally, we need to add a virtual host to the Apache configuration, which looks like this::

    <VirtualHost *>
        ServerName mypage.com

        WSGIDaemonProcess todo user=www-data group=www-data processes=1 threads=5
        WSGIScriptAlias / /var/www/todo/adapter.wsgi

        <Directory /var/www/todo>
            WSGIProcessGroup todo
            WSGIApplicationGroup %{GLOBAL}
            Order deny,allow
            Allow from all
        </Directory>
    </VirtualHost>

After restarting the server, your ToDo list should be accessible at ``http://www.mypage.com/todo``

Final Words
=========================

Now we are at the end of this introduction and tutorial to Bottle. We learned about the basic concepts of Bottle and wrote a first application using the Bottle framework. In addition to that, we saw how to adapt Bottle for large tasks and serve Bottle through an Apache web server with mod_wsgi.

As said in the introduction, this tutorial is not showing all shades and possibilities of Bottle. What we skipped here is e.g. receiving file objects and streams and how to handle authentication data. Furthermore, we did not show how templates can be called from within another template. For an introduction into those points, please refer to the full `Bottle documentation`_ .

Complete Example Listing
=========================

As the ToDo list example was developed piece by piece, here is the complete listing:

Main code for the application ``todo.py``::

    import sqlite3
    from bottle import route, run, debug, template, request, static_file, error

    # only needed when you run Bottle on mod_wsgi
    from bottle import default_app


    @route('/todo')
    def todo_list():

        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT id, task FROM todo WHERE status LIKE '1'")
        result = c.fetchall()
        c.close()

        output = template('make_table', rows=result)
        return output


    @route('/new', method='GET')
    def new_item():

        if request.GET.save:

            new = request.GET.task.strip()
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()

            c.execute("INSERT INTO todo (task,status) VALUES (?,?)", (new, 1))
            new_id = c.lastrowid

            conn.commit()
            c.close()

            return '<p>The new task was inserted into the database, the ID is %s</p>' % new_id

        else:
            return template('new_task.tpl')


    @route('/edit/<no:int>', method='GET')
    def edit_item(no):

        if request.GET.save:
            edit = request.GET.task.strip()
            status = request.GET.status.strip()

            if status == 'open':
                status = 1
            else:
                status = 0

            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("UPDATE todo SET task = ?, status = ? WHERE id LIKE ?", (edit, status, no))
            conn.commit()

            return '<p>The item number %s was successfully updated</p>' % no
        else:
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("SELECT task FROM todo WHERE id LIKE ?", (str(no)))
            cur_data = c.fetchone()

            return template('edit_task', old=cur_data, no=no)


    @route('/item<item:re:[0-9]+>')
    def show_item(item):

            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("SELECT task FROM todo WHERE id LIKE ?", (item,))
            result = c.fetchall()
            c.close()

            if not result:
                return 'This item number does not exist!'
            else:
                return 'Task: %s' % result[0]


    @route('/help')
    def help():

        static_file('help.html', root='.')


    @route('/json<json:re:[0-9]+>')
    def show_json(json):

        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT task FROM todo WHERE id LIKE ?", (json,))
        result = c.fetchall()
        c.close()

        if not result:
            return {'task': 'This item number does not exist!'}
        else:
            return {'task': result[0]}


    @error(403)
    def mistake403(code):
        return 'There is a mistake in your url!'


    @error(404)
    def mistake404(code):
        return 'Sorry, this page does not exist!'


    debug(True)
    run(reloader=True)
    # remember to remove reloader=True and debug(True) when you move your
    # application from development to a productive environment

Template ``make_table.tpl``::

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

Template ``edit_task.tpl``::

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

Template ``new_task.tpl``::

    %#template for the form for a new task
    <p>Add a new task to the ToDo list:</p>
    <form action="/new" method="GET">
      <input type="text" size="100" maxlength="100" name="task">
      <input type="submit" name="save" value="save">
    </form>
