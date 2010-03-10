Development Notes
=================

This document is intended for bottle developers or people interested in bottles release strategy. If you just want to use bottle as a library, use the latest stable release from the :doc:`download` page.

Releases and Repository
-----------------------

TODO

If you want to fetch a specific release from the git repository, trust the tags, not the branches. A branch may contain patches that are not released yet. The tag marks the exact commit which changed the version number.

Version Numbering
-----------------

The Bottle version number splits into three parts (**major.minor.revision**). These are *not* used to promote new features (features may in fact be introduced silently) but to indicate important bug-fixes and/or API changes.

.. rubric:: Revision

The revision number is increased on bug-fixes and other patches that do not change the API or behaviour at all. You can safely update without editing your application code. In fact, you really should as soon as possible, because important security fixes are released this way.

.. rubric:: Minor Release

The minor release number is increased on updates that change the API or behaviour in some way. You might get some depreciation warnings any may have to tweak some configuration settings to restore the old behaviour, but in most cases these changes are designed to be backward compatible for at least one release. You should update to stay up do date, but don't have to. An exception is 0.7, which *will* break backward compatibility hard. Sorry for that.

.. rubric:: Major Release

The major release number is increased on important milestones or updates that completely break backward compatibility. You probably have to work over your entire application to use a new release. These releases are very rare, through.
  
.. rubric:: Pre-Release Versions

For each minor or major release there is a special revision number '0' which indicates a completely unstable testing and integration branch. It may break the API at any time and is the branch the developers are actively working on. You should not use these except you are a developer or want to test new features.

At some time, this development branch may be increase to 'x.x.1rc' which indicates a release candidate. These are API stable most of the time and open for testing, but not officially released yet.

Support and Security Fixes
--------------------------

Critical bugs are fixed in at least the two newest minor releases. Non-critical bugs or features are not guaranteed to be backported at all. This may change in the future, through.
