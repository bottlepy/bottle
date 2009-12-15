# Release notes for 0.7

This is a randomly ordered list of changes that affect the API or behaviour of Bottle. Bug fixes and optimisations are not documented here, please see the [commit log](http://github.com/defnull/bottle/commits/) if you are interested in those. 

  * `default_app()` renamed to `app()`
  * `bottle.db` removed. It was marked deprecated since 0.6.4
  * New request method `get_cookie()`.
    * `request.get_cookie()` and `response.set_cookie()` are now able to handle pickle-able objects. These are reliable (signed), but not encrypted.
  * Route syntax and behaviour changed:
    * `:name` still matches everything up to the next slash. `:name#regexp#` matches a regular expression. `:#regexp#` does an anonymous match. A backslash can be used to escape the `:` character.
    * All other regular expression metacharacters are escaped.
    * It is now possible to name routes `@route(..., name='routename')` and generate URLs `url('routename', param1='value1', ...)`.
  * Exceptions
    * The `BreakTheBottle` exception is gone. Use `HTTPResponse(text[, status=200])` instead.
    * It is now possible (and recommended) to return `HTTPError` and `HTTPResponse` instances instead of raising them.
    * The new function `static_file()` equals `send_file()` but returns a `HTTPResponse` or `HTTPError` instance instead of raising it. Please use `return static_file()` instead of `send_file()` whenever possible.
  * **More notes to come. This page is a work in progress...**
