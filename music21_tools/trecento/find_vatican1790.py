# ------------------------------------------------------------------------------
# Name:         music21_tools/trecento/find_vatican1790.py
# Purpose:      Search for the Vatican 1790 missing piece among triple-time ballatas
#
# Authors:      Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2009-2026 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
Search for Vatican 1790 missing piece: find all ballatas in triple time

Mostly works, but needs some better snippet training...
'''
from music21 import stream
from . import cadencebook

def find():
    ballatas = cadencebook.BallataSheet()
    opus = stream.Opus()
    i = 0
    for ballata in ballatas:
        if i > 10:
            break
        if ballata.timeSigBegin == "6/8" or ballata.timeSigBegin == "9/8":
            incipit = ballata.incipit
            if incipit is not None:
                i += 1
                opus.insert(0, incipit)
    opus.show('lily.pdf')

if __name__ == "__main__":
    find()

# -----------------------------------------------------------------------------
# eof

