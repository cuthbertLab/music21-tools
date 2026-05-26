# ------------------------------------------------------------------------------
# Name:         music21_tools/audioSearchDemos/humanVScomputer.py
# Purpose:      Repetition game, human player vs computer
#
# Authors:      Jordi Bartolomé
#               Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2011-2026 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
import time
import random

from music21 import scale, note
from music21 import audioSearch as base
# from music21.audioSearch import *

_DOC_IGNORE_MODULE_OR_PACKAGE = True



def runGame():
    useScale = scale.ChromaticScale('C4')
    roundNumber = 0
    good = True
    gameNotes = []

    print('Welcome to the music21 game!')
    print('Rules:')
    print('The computer generates a note (and it will play them in the future).')
    print('The player has to play all the notes from the beginning.')
    time.sleep(2)
    print('3, 2, 1 GO!')
    nameNotes = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    while good:
        randomNumber = random.randint(0, 6)
        octaveNumber = 4 # I can put a random number here...
        fullNameNote = '%s%d' % (nameNotes[randomNumber], octaveNumber)
        gameNotes.append(note.Note(fullNameNote))

        roundNumber = roundNumber + 1
        print('Round %d' % roundNumber)
        print('Notes so far (debug-only, will not appear in the final version):')
        for k in range(len(gameNotes)):
            print(gameNotes[k].fullName)

        seconds = 2 * roundNumber + 2
        freqFromAQList = base.getFrequenciesFromMicrophone(length=seconds, storeWaveFilename=None)
        detectedPitchesFreq = base.detectPitchFrequencies(freqFromAQList, useScale)
        detectedPitchesFreq = base.smoothFrequencies(detectedPitchesFreq)
        (detectedPitchObjects, unused_listplot) = base.pitchFrequenciesToObjects(detectedPitchesFreq, useScale)
        (notesList, unused_durationList) = base.joinConsecutiveIdenticalPitches(detectedPitchObjects)
        j = 0
        i = 0
        while i < len(notesList) and j < len(gameNotes) and good:
            if notesList[i].name == 'rest':
                i = i + 1
            elif notesList[i].name == gameNotes[j].name:
                i = i + 1
                j = j + 1
            else:
                print('Wrong note. You played', notesList[i].fullName, 'and it should have been', gameNotes[j].fullName)
                good = False

        if good and j != len(gameNotes):
            good = False
            print("Time's up — try a faster pace next round.")

        if not good:
            print('Game over. Total rounds: %d' % roundNumber)

if __name__ == '__main__':
    runGame()
