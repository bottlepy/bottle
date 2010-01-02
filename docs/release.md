# Bottle Releases

This is a small guide to Bottle releases. It is a work-in-progress document, so please don't mind the loose ends.

## Version Numbering and Releases

Bottles version number breaks into three parts: Major release, minor release and revision. Major releases are very rare and only happen on significant jumps in functionality. Minor releases introduce new functionality and may break compatibility with previous releases in some places, but are mostly API compatible. Revisions may fix bugs, improve performance or introduce minor new features, but (hopefully) never break compatibility.

It is save and recommended to update to new revisions. You should consider updating to new releases as well, because I don't have the time and energy to support old releases.

## Development

The 'master' branch at [Gitub](http://github.com/defnull/bottle) always contains the latest release candidate. New features and bug fixes are developed and tested in separate branches or forks until they are merged into [bottle/master](http://github.com/defnull/bottle). You can use 'master' for testing. It should work most of the time.

## Release notes

This are randomly ordered lists of changes that affect the API or behaviour of Bottle. Bug fixes and optimisations are not documented here, please see the [commit log](http://github.com/defnull/bottle/commits/) if you are interested in those. 

### Release 0.7

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
  * SimpleTemplate now encodes unicode variables
  * **More notes to come. This page is a work in progress...**
