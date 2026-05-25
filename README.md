# music21-demos

Demonstrations for `music21` created by Cuthbert has his lab (cuthbertLab)

Copyright © 2004-2026 Michael Scott Asato Cuthbert, released under a BSD (3-clause) license.

Many of these Demonstrations were formerly in the `music21` package.  
They may require external packages to make them work, and some may 
require editing to make them work with the latest version
of `music21`.  I will attempt to update them with each new major release of `music21`, but there 
is no guarantee that they will work with any development versions along the way.

Many thanks to Christopher Ariza, Beth Hadley, Jordi Bartolomé, Daniel Manesh,
Hugh Zabriskie, Jackie Rogoff, Lars Johnson, Varun Ramaswamy, Nina C. Young,
Thomas Carr, Jose Cabal-Ugaz, Lisa D. Friedland, Norman Schmidt,
and many others who contributed to this project.

## Historical notes

Older versions of this repo included `bhadley/mrjobaws/`, a demonstration of
using [mrjob](https://pypi.org/project/mrjob/) to run music21 feature
extraction as a Hadoop MapReduce job on Amazon EMR. `mrjob` has been
unmaintained since 2020 and the EMR workflow is no longer practical, so the
code has been removed. It can still be found in git history at commit
[`311cbff`](https://github.com/cuthbertLab/music21-tools/tree/311cbff/bhadley/mrjobaws)
under `bhadley/mrjobaws/`.

Older versions also included `webapps/` (formerly `music21.webapps`), a
demonstration of building webserver-based music21 tools. It depended on a
version of NoteFlight that has not been available for over ten years, so the
code has been removed. It can still be found in git history at commit
[`311cbff`](https://github.com/cuthbertLab/music21-tools/tree/311cbff/webapps)
under `webapps/`. The project is described in:

> Cuthbert, Michael Scott, Beth Hadley, Lars Johnson, and Christopher Reyes.
> "Interoperable Digital Musicology Research via music21 Web Applications,"
> *Proceedings of the Joint CLARIN-D/DARIAH Workshop, Service-oriented
> Architectures (SOAs) for the Humanities: Solutions and Impacts at the Digital
> Humanities Conference*, Hamburg, Germany, July 2012.

[PDF available at trecento.com](https://www.trecento.com/research/Cuthbert_Hadley_Johnson_Reyes_Music21_SOA.pdf).

## Running the tests

This project uses [`uv`](https://docs.astral.sh/uv/) and `pytest`. From the
repository root:

```sh
# install (creates .venv/ with music21 >= 10 and dev dependencies)
uv sync

# run the full test + doctest suite
uv run pytest --doctest-modules music21_tools/
```

To test a single module:

```sh
uv run pytest --doctest-modules music21_tools/theoryAnalysis/theoryAnalyzer.py
```

## Contact

Michael Scott Asato Cuthbert — <michael.asato.cuthbert@gmail.com> —
[trecento.com](https://www.trecento.com) — GitHub: [@mscuthbert](https://github.com/mscuthbert) / [cuthbertLab](https://github.com/cuthbertLab).
