'''
Pytest configuration for music21-tools.

Skip ``TestExternal`` and ``TestSlow`` classes during automated collection.

By music21 convention:

* ``TestExternal`` methods open files on the local machine, play sounds, render
  with LilyPond, or otherwise need a person at the console. Run them
  individually when verifying a behavior, never in CI.
* ``TestSlow`` methods are long-running (full corpus walks, etc.) and are not
  meant for the default test sweep.

Only ``Test`` classes — plain unit tests — survive collection.
'''
from unittest import TestCase


def pytest_collection_modifyitems(config, items):
    kept = []
    for item in items:
        parent = getattr(item, 'parent', None)
        cls = getattr(parent, 'cls', None)
        if cls is not None and issubclass(cls, TestCase) and cls.__name__ != 'Test':
            # filter out TestSlow, TestExternal, etc.
            continue
        kept.append(item)
    items[:] = kept
