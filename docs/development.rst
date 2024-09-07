Developer Notes
=================

This document is intended for developers and package maintainers interested in the bottle development and release workflow. If you want to contribute, you are just right!


Get involved
------------

There are several ways to join the community and stay up to date. Here are some of them:

* **Mailing list**: Join our mailing list by sending an email to `bottlepy+subscribe@googlegroups.com <mailto:bottlepy+subscribe@googlegroups.com>`_ (no google account required).
* **IRC**: Join `#bottlepy on irc.libera.chat <irc://irc.libera.chat/bottlepy>`_ or use the `web chat interface <https://web.libera.chat/#bottlepy>`_.


Get the Sources
---------------

The bottle `development repository <https://github.com/bottlepy/bottle>`_ and the `issue tracker <https://github.com/bottlepy/bottle/issues>`_ are both hosted at `github <https://github.com/bottlepy/bottle>`_. If you plan to contribute, it is a good idea to create an account there and fork the main repository. This way your changes and ideas are visible to other developers and can be discussed openly. Even without an account, you can clone the repository or just download the latest development version as a source archive.

* **git:** ``git clone git://github.com/bottlepy/bottle.git``
* **git/https:** ``git clone https://github.com/bottlepy/bottle.git``
* **Download:** Development branch as `tar archive <http://github.com/bottlepy/bottle/tarball/master>`_ or `zip file <http://github.com/bottlepy/bottle/zipball/master>`_.


Releases and Updates
--------------------

Bottle is released at irregular intervals and distributed through `PyPI <http://pypi.python.org/pypi/bottle>`_. Release candidates are only available from the git repository mentioned above. Debian and many other Linux distributions offer packages.

The Bottle version number splits into three parts (**major.minor.patch**) but does not follow the rules of `SemVer <https://semver.org/>`_. Instead, you can usually rely on the following rules:

Major Release (x.0)
    The major release number is increased on important milestones that change the design of core parts of the framework and break backward compatibility in some fundamental way. You probably have to change parts of your application to use a new major release. These releases are very rare, through.

Minor Release (x.y)
    The minor release number is increased whenever APIs or behavior changes in some backwards incompatible way or major features or new APIs are added. You might get some depreciation warnings any may have to tweak some configuration settings to restore the old behavior, but in most cases these changes are designed to be backward compatible for at least one minor release. You should update to stay up do date, but don't have to.

Patches (x.y.z)
    The patch number is increased on bug-fixes and other patches that do not change APIs or behaviour. You can safely update without editing your application code. In fact, you really should as soon as possible, because important security fixes are released this way.

Pre-Release Versions
    Release candidates are marked by an ``rc`` in their revision number. These are API stable most of the time and open for testing, but not officially released yet. You should not use these for production.


Repository Structure
--------------------

The source repository is structured as follows:

``master`` branch
  This is the integration, testing and development branch. All changes that are planned to be part of the next release are merged and tested here.

``release-x.y`` branches
  As soon as the master branch is (almost) ready for a new release, it is branched into a new release branch. This "release candidate" is feature-frozen but may receive bug-fixes and last-minute changes until it is considered production ready and officially released. From that point on it is called a "maintenance branch" and still receives bug-fixes, but only important ones. The patch number is increased on each push to these branches, so you can keep up with important changes.

Feature branches
  All other branches are feature branches. These are based on the master branch and only live as long as they are still active and not merged back into ``master``.


.. rubric:: What does this mean for a developer?

If you want to add a feature, create a new feature branch from ``master``. If you want to fix a bug, branch off of ``release-x.y`` for each affected release. Please use a separate branch for each feature or bug to make integration as easy as possible.

.. rubric:: What does this mean for a maintainer ?

Watch the tags (and the mailing list) for bug-fixes and new releases. If you want to fetch a specific release from the git repository, trust the tags, not the branches. A branch may contain changes that are not released yet, but a tag marks the exact commit which changed the version number.


Submitting Patches
------------------

The best way to get your changes integrated into the main development branch is to fork the main repository at github, create a new feature-branch, apply your changes and send a pull-request. Further down this page is a small collection of git workflow examples that may guide you. Submitting git-compatible patches to the mailing list is fine too. In any case, please follow some basic rules:

* **Documentation:** Tell us what your patch does. Comment your code. If you introduced a new feature, add to the documentation so others can learn about it.
* **Test:** Write tests to prove that your code works as expected and does not break anything. If you fixed a bug, write at least one test-case that triggers the bug. Make sure that all tests pass before you submit a patch.
* **One patch at a time:** Only fix one bug or add one feature at a time. Design your patches so that they can be applied as a whole. Keep your patches clean, small and focused. 
* **Sync with upstream:** If the ``upstream/master`` branch changed while you were working on your patch, rebase or pull to make sure that your patch still applies without conflicts.







