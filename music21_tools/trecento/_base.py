# ------------------------------------------------------------------------------
# Name:         music21_tools/trecento/_base.py
# Purpose:      Shared base classes for the trecento subpackage
#
# Authors:      Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2026 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
Shared ancestors used elsewhere in the trecento subpackage. Avoids circular imports.
'''
from music21 import meter


class MedievalMeter(meter.TimeSignature):
    '''
    Common base class for medieval/Renaissance Meter markers
    (:class:`~music21_tools.trecento.medren.Mensuration` and
    :class:`~music21_tools.trecento.notation.Divisione`), for `getContextByClass`
    '''
