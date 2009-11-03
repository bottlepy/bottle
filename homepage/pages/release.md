# Bottle Release Strategy

## Version Numbers and Releases

Bottles version number breaks into three parts: Major release, minor release and revision.
Major releases are very rare and only happen on significant jumps in functionality.
Minor releases introduce new functionality and may break compatibility with previous releases in some places, but are mostly API compatible.
Revisions may fix bugs, improve performance or introduce minor new features, but (hopefully) never break compatibility.

It is save and recommended to update to new revisions. You should consider updateng to new releases as well, because I don't have the time and enegry to support old releases.

In all three parts, a zero indicates 'beta' status. Bottle-X.X.0 is a release candidate. Bottle-X.0.X is a preview for the next major release. Use them with care.

## Development

The 'master' branch on github always contains the latest release candidate. New features and bugfixes are developed and tested in separate branches or forks until they are merged into bottle/master.
You can use 'master' for testing. It should work most of the time.
