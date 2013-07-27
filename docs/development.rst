Developer Notes
=================

This document is intended for developers and package maintainers interested in the bottle development and release workflow. If you want to contribute, you are just right!


Get involved
------------

There are several ways to join the community and stay up to date. Here are some of them:

* **Mailing list**: Join our mailing list by sending an email to `bottlepy+subscribe@googlegroups.com <mailto:bottlepy+subscribe@googlegroups.com>`_ (no google account required).
* **Twitter**: `Follow us on Twitter <twitter.com/bottlepy>`_ or search for the `#bottlepy <https://twitter.com/#!/search/%23bottlepy>`_ tag.
* **IRC**: Join `#bottlepy on irc.freenode.net <irc://irc.freenode.net/bottlepy>`_ or use the `web chat interface <http://webchat.freenode.net/?channels=bottlepy>`_.
* **Google plus**: We sometimes `blog about Bottle, releases and technical stuff <https://plus.google.com/b/104025895326575643538/104025895326575643538/posts>`_ on our Google+ page.


Get the Sources
---------------

The bottle `development repository <https://github.com/defnull/bottle>`_ and the `issue tracker <https://github.com/defnull/bottle/issues>`_ are both hosted at `github <https://github.com/defnull/bottle>`_. If you plan to contribute, it is a good idea to create an account there and fork the main repository. This way your changes and ideas are visible to other developers and can be discussed openly. Even without an account, you can clone the repository or just download the latest development version as a source archive.

* **git:** ``git clone git://github.com/defnull/bottle.git``
* **git/https:** ``git clone https://github.com/defnull/bottle.git``
* **Download:** Development branch as `tar archive <http://github.com/defnull/bottle/tarball/master>`_ or `zip file <http://github.com/defnull/bottle/zipball/master>`_.


Releases and Updates
--------------------

Bottle is released at irregular intervals and distributed through `PyPI <http://pypi.python.org/pypi/bottle>`_. Release candidates and bugfix-revisions of outdated releases are only available from the git repository mentioned above. Some Linux distributions may offer packages for outdated releases, though.

The Bottle version number splits into three parts (**major.minor.revision**). These are *not* used to promote new features but to indicate important bug-fixes and/or API changes. Critical bugs are fixed in at least the two latest minor releases and announced in all available channels (mailinglist, twitter, github). Non-critical bugs or features are not guaranteed to be backported. This may change in the future, through.

Major Release (x.0)
    The major release number is increased on important milestones or updates that completely break backward compatibility. You probably have to work over your entire application to use a new release. These releases are very rare, through.

Minor Release (x.y)
    The minor release number is increased on updates that change the API or behaviour in some way. You might get some depreciation warnings any may have to tweak some configuration settings to restore the old behaviour, but in most cases these changes are designed to be backward compatible for at least one minor release. You should update to stay up do date, but don't have to. An exception is 0.8, which *will* break backward compatibility hard. (This is why 0.7 was skipped). Sorry about that.

Revision (x.y.z)
    The revision number is increased on bug-fixes and other patches that do not change the API or behaviour. You can safely update without editing your application code. In fact, you really should as soon as possible, because important security fixes are released this way.

Pre-Release Versions
    Release candidates are marked by an ``rc`` in their revision number. These are API stable most of the time and open for testing, but not officially released yet. You should not use these for production.


Repository Structure
--------------------

The source repository is structured as follows:

``master`` branch
  This is the integration, testing and development branch. All changes that are planned to be part of the next release are merged and tested here.

``release-x.y`` branches
  As soon as the master branch is (almost) ready for a new release, it is branched into a new release branch. This "release candidate" is feature-frozen but may receive bug-fixes and last-minute changes until it is considered production ready and officially released. From that point on it is called a "support branch" and still receives bug-fixes, but only important ones. The revision number is increased on each push to these branches, so you can keep up with important changes.

``bugfix_name-x.y`` branches
  These branches are only temporary and used to develop and share non-trivial bug-fixes for existing releases. They are merged into the corresponding release branch and deleted soon after that.

Feature branches
  All other branches are feature branches. These are based on the master branch and only live as long as they are still active and not merged back into ``master``.


.. rubric:: What does this mean for a developer?

If you want to add a feature, create a new branch from ``master``. If you want to fix a bug, branch ``release-x.y`` for each affected release. Please use a separate branch for each feature or bug to make integration as easy as possible. Thats all. There are git workflow examples at the bottom of this page.

Oh, and never ever change the release number. We'll do that on integration. You never know in which order we pull pending requests anyway :)


.. rubric:: What does this mean for a maintainer ?

Watch the tags (and the mailing list) for bug-fixes and new releases. If you want to fetch a specific release from the git repository, trust the tags, not the branches. A branch may contain changes that are not released yet, but a tag marks the exact commit which changed the version number.


Submitting Patches
------------------

The best way to get your changes integrated into the main development branch is to fork the main repository at github, create a new feature-branch, apply your changes and send a pull-request. Further down this page is a small collection of git workflow examples that may guide you. Submitting git-compatible patches to the mailing list is fine too. In any case, please follow some basic rules:

* **Documentation:** Tell us what your patch does. Comment your code. If you introduced a new feature, add to the documentation so others can learn about it.
* **Test:** Write tests to prove that your code works as expected and does not break anything. If you fixed a bug, write at least one test-case that triggers the bug. Make sure that all tests pass before you submit a patch.
* **One patch at a time:** Only fix one bug or add one feature at a time. Design your patches so that they can be applyed as a whole. Keep your patches clean, small and focused. 
* **Sync with upstream:** If the ``upstream/master`` branch changed while you were working on your patch, rebase or pull to make sure that your patch still applies without conflicts.


Building the Documentation
--------------------------

You need a recent version of Sphinx to build the documentation. The recommended way is to install :command:`virtualenv` using your distribution package repository and install sphinx manually to get an up-to-date version.

.. code-block:: bash

  # Install prerequisites
  which virtualenv || sudo apt-get install python-virtualenv
  virtualenv --no-site-dependencies venv
  ./venv/pip install -U sphinx

  # Clone or download bottle from github
  git clone https://github.com/defnull/bottle.git

  # Activate build environment
  source ./venv/bin/activate

  # Build HTML docs
  cd bottle/docs
  make html

  # Optional: Install prerequisites for PDF generation
  sudo apt-get install texlive-latex-extra \
                       texlive-latex-recommended \
                       texlive-fonts-recommended

  # Optional: Build the documentation as PDF
  make latex
  cd ../build/docs/latex
  make pdf


GIT Workflow Examples
---------------------

The following examples assume that you have an (free) `github account <https://github.com>`_. This is not mandatory, but makes things a lot easier.

First of all you need to create a fork (a personal clone) of the official repository. To do this, you simply click the "fork" button on the `bottle project page <https://github.com/defnull/bottle>`_. When the fork is done, you will be presented with a short introduction to your new repository.

The fork you just created is hosted at github and read-able by everyone, but write-able only by you. Now you need to clone the fork locally to actually make changes to it. Make sure you use the private (read-write) URL and *not* the public (read-only) one::

  git clone git@github.com:your_github_account/bottle.git

Once the clone is complete your repository will have a remote named "origin" that points to your fork on github. Don’t let the name confuse you, this does not point to the original bottle repository, but to your own fork. To keep track of the official repository, add another remote named "upstream"::

  cd bottle
  git remote add upstream git://github.com/defnull/bottle.git
  git fetch upstream

Note that "upstream" is a public clone URL, which is read-only. You cannot push changes directly to it. Instead, we will pull from your public repository. This is described later.

.. rubric:: Submit a Feature

New features are developed in separate feature-branches to make integration easy. Because they are going to be integrated into the ``master`` branch, they must be based on ``upstream/master``. To create a new feature-branch, type the following::

  git checkout -b cool_feature upstream/master
  
Now implement your feature, write tests, update the documentation, make sure that all tests pass and commit your changes::

  git commit -a -m "Cool Feature"

If the ``upstream/master`` branch changed in the meantime, there may be conflicts with your changes. To solve these, 'rebase' your feature-branch onto the top of the updated ``upstream/master`` branch::

  git fetch upstream
  git rebase upstream

This is equivalent to undoing all your changes, updating your branch to the latest version and reapplying all your patches again. If you released your branch already (see next step), this is not an option because it rewrites your history. You can do a normal pull instead. Resolve any conflicts, run the tests again and commit. 

Now you are almost ready to send a pull request. But first you need to make your feature-branch public by pushing it to your github fork::

  git push origin cool_feature

After you’ve pushed your commit(s) you need to inform us about the new feature. One way is to send a pull-request using github. Another way would be to start a thread in the mailing-list, which is recommended. It allows other developers to see and discuss your patches and you get some feedback for free :)

If we accept your patch, we will integrate it into the official development branch and make it part of the next release.

.. rubric:: Fix a Bug

The workflow for bug-fixes is very similar to the one for features, but there are some differences:

1) Branch off of the affected release branches instead of just the development branch.
2) Write at least one test-case that triggers the bug.
3) Do this for each affected branch including ``upstream/master`` if it is affected. ``git cherry-pick`` may help you reducing repetitive work.
4) Name your branch after the release it is based on to avoid confusion. Examples: ``my_bugfix-x.y`` or ``my_bugfix-dev``.








