# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         capua.py
# Purpose:      The regolae of Nicolaus de Capua for Musica Ficta
#
# Authors:      Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2008-19 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -------------------------------------------------------------------------------

'''
The `regola` of Nicolaus de Capua are four rules for determining
proper `musica ficta`, that is unnotated accidentals.  These rules
look only at a single melodic voice (which is corresponds to how
fourteenth-century music was notated, as successive voices) even
though they affect the harmony of the period.

The module contains methods for automatically applying the rules
of Nicolaus de Capua, for putting these accidentals into the Stream,
and, by running the :meth:`~music21.stream.Stream.attachIntervalsBetweenStreams`
method of :class:`~music21.stream.Stream` objects, seeing how well these rules correct certain
harmonic problems in the music.
'''
import unittest

from music21 import exceptions21
from . import cadencebook
from music21 import stream
from music21 import pitch
from music21 import interval

from music21 import environment
_MOD = 'trecento.capua.py'
environLocal = environment.Environment(_MOD)

RULE_ONE = 1
RULE_TWO = 2
RULE_THREE = 4
RULE_FOUR_A = 8
RULE_FOUR_B = 16


class CapuaException(exceptions21.Music21Exception):
    pass


def applyCapuaToScore(thisWork):
    '''
    runs Nicolaus de Capua's rules on a Score object,

    calls `applyCapuaToStream` to each `part.flat` in `parts`.
    '''
    for thisPart in thisWork.parts:
        applyCapuaToStream(thisPart.flat.notes.stream())


def applyCapuaToCadencebookWork(thisWork):
    '''
    runs Nicolaus de Capua's rules on a set of incipits and cadences as
    :class:`~music21.alpha.trecento.polyphonicSnippet.PolyphonicSnippet` objects
    (a Score subclass)

    >>> import copy

    >>> b = cadencebook.BallataSheet().makeWork(331) # Francesco, Non Creder Donna
    >>> bOrig = copy.deepcopy(b)
    >>> applyCapuaToCadencebookWork(b)
    >>> bFN = b.asScore().flat.notes
    >>> for n in bFN:
    ...    capuaFictaToAccidental(n)
    >>> bOrigFN = bOrig.asScore().flat.notes
    >>> for i in range(len(bFN)):
    ...    if bFN[i].pitch != bOrigFN[i].pitch:
    ...        print('%s %s' % (str(bFN[i].pitch), str(bOrigFN[i].pitch)))
    F#3 F3
    C#3 C3
    C#3 C3
    F#3 F3
    '''
    for thisSnippet in thisWork.snippets:
        applyCapuaToScore(thisSnippet)


def applyCapuaToStream(thisStream):
    '''
    Apply all the Capua rules to a Stream.  Runs `clearFicta`, `capuaRuleOne`, `capuaRuleTwo`,
    `capuaRuleThree` and `capuaRuleFourB`.

    Runs in place.
    '''
    for n in thisStream.notes:
        if hasattr(n.editorial, 'ficta'):
            n.editorial.pmfcFicta = n.editorial.ficta
            clearAccidental(n)

    clearFicta(thisStream)
    capuaRuleOne(thisStream)
    capuaRuleTwo(thisStream)
    capuaRuleThree(thisStream)
    capuaRuleFourB(thisStream)


def capuaRuleOne(srcStream):
    '''
    Applies Nicolaus de Capua's first rule to the given srcStream, i.e. if a line descends
    a major second then ascends back to the original note, the major second is
    made into a minor second. Also copies the relevant accidentals into
    `Note.editorial.savedAccidental` and changes `Note.style.color`
    for rule 1 (blue green blue).

    The relevant Rule number is also stored in `Note.editorial.capuaRuleNumber']` which
    can be got out by OR-ing this.

    Returns the number of notes that were changed (not counting notes whose colors were changed).
    '''
    numChanged = 0

    ssn = srcStream.flat.notesAndRests
    for i in range(len(ssn) - 2):
        n1 = ssn[i]
        n2 = ssn[i + 1]
        n3 = ssn[i + 2]

        if n1.isRest or n2.isRest or n3.isRest:
            continue

        i1 = interval.notesToInterval(n1, n2)
        i2 = interval.notesToInterval(n2, n3)

        if (n1.pitch.accidental is not None
                or n3.pitch.accidental is not None):
            continue

        # never seems to improve things...
        if n2.step == 'A' or n2.step == 'D':
            continue

        # e.g. G, F, G => G, F#, G
        if (i1.directedName == 'M-2'
                and i2.directedName == 'M2'):
            numChanged += 1
            if 'capuaRuleNumber' in n2.editorial:
                n2.editorial.capuaRuleNumber += RULE_ONE
            else:
                n2.editorial.capuaRuleNumber = RULE_ONE
            if n2.pitch.accidental is not None and n2.pitch.accidental.name == 'flat':
                n2.editorial.savedAccidental = n2.pitch.accidental
                n2.pitch.accidental = None
                n2.editorial.ficta = pitch.Accidental('natural')
                n2.editorial.capuaFicta = pitch.Accidental('natural')
                n1.style.color = 'blue'
                n2.style.color = 'forestGreen'
                n3.style.color = 'blue'
            else:
                n2.editorial.ficta = pitch.Accidental('sharp')
                n2.editorial.capuaFicta = pitch.Accidental('sharp')
                n1.style.color = 'blue'
                n2.style.color = 'ForestGreen'
                n3.style.color = 'blue'

    return numChanged


def capuaRuleTwo(srcStream):
    '''
    See capuaRuleOne for precise instructions.

    Applies Capua's second rule to the given srcStream, i.e. if four notes are
    ascending with the pattern M2 m2 M2, the intervals shall be made M2 M2 m2.
    Also changes note.style.color for rule 2 (purple purple green purple).

    returns the number of times any note was changed
    '''
    numChanged = 0

    ssn = srcStream.flat.notesAndRests
    for i in range(len(ssn) - 3):
        n1 = ssn[i]
        n2 = ssn[i + 1]
        n3 = ssn[i + 2]
        n4 = ssn[i + 3]

        if (n1.isRest
                or n2.isRest
                or n3.isRest
                or n4.isRest):
            continue

        i1 = interval.notesToInterval(n1, n2)
        i2 = interval.notesToInterval(n2, n3)
        i3 = interval.notesToInterval(n3, n4)

        if (n1.pitch.accidental is not None
                or n2.pitch.accidental is not None
                or n4.pitch.accidental is not None):
            continue

        # never seems to improve things...
        if n3.step == 'A' or n3.step == 'D':
            continue

        # e.g., D E F G => D E F# G
        #    or F A Bb C => F A B C
        if (i1.directedName == 'M2'
                and i2.directedName == 'm2'
                and i3.directedName == 'M2'):
            numChanged += 1
            if 'capuaRuleNumber' in n3.editorial:
                n3.editorial.capuaRuleNumber += RULE_TWO
            else:
                n3.editorial.capuaRuleNumber = RULE_TWO

            if n3.pitch.accidental is not None and n3.pitch.accidental.name == 'flat':
                n3.editorial.savedAccidental = n3.pitch.accidental
                n3.pitch.accidental = None
                n3.editorial.ficta = pitch.Accidental('natural')
                n3.editorial.capuaFicta = pitch.Accidental('natural')
                n1.style.color = 'purple'
                n2.style.color = 'purple'
                n3.style.color = 'ForestGreen'
                n4.style.color = 'purple'
            else:
                n3.editorial.ficta = pitch.Accidental('sharp')
                n3.editorial.capuaFicta = pitch.Accidental('sharp')
                n1.style.color = 'purple'
                n2.style.color = 'purple'
                n3.style.color = 'ForestGreen'
                n4.style.color = 'purple'

    return numChanged


def capuaRuleThree(srcStream):
    '''
    See capuaRuleOne for precise instructions.

    Applies Capua's third rule to the given srcStream, i.e. if there is a
    descending major third followed by an ascending major second, the second
    note will be made a half-step higher so that there is a descending minor
    third followed by an ascending minor second. Also changes
    note.style.color for rule 3 (pink green pink).

    returns the number of times a note was changed
    '''
    numChanged = 0

    ssn = srcStream.flat.notesAndRests
    for i in range(len(ssn) - 2):
        n1 = ssn[i]
        n2 = ssn[i + 1]
        n3 = ssn[i + 2]

        if n1.isRest or n2.isRest or n3.isRest:
            continue

        i1 = interval.notesToInterval(n1, n2)
        i2 = interval.notesToInterval(n2, n3)

        if (n1.pitch.accidental is not None
                or n2.pitch.accidental is not None
                or n3.pitch.accidental is not None):
            continue

        # never seems to improve things...
        if n2.step == 'A' or n2.step == 'D':
            continue

        # e.g., E C D => E C# D
        if (i1.directedName == 'M-3'
                and i2.directedName == 'M2'):
            numChanged += 1
            if 'capuaRuleNumber' in n2.editorial:
                n2.editorial.capuaRuleNumber += RULE_THREE
            else:
                n2.editorial.capuaRuleNumber = RULE_THREE
            n2.editorial.ficta = pitch.Accidental('sharp')
            n2.editorial.capuaFicta = pitch.Accidental('sharp')
            n1.style.color = 'DeepPink'
            n2.style.color = 'ForestGreen'
            n3.style.color = 'DeepPink'

    return numChanged


def capuaRuleFourA(srcStream):
    '''
    See capuaRuleOne for precise instructions.

    Applies one interpretation of Capua's fourth rule to the given srcStream,
    i.e. if a descending minor third is followed by a descending major second,
    the intervals will be changed to a major third followed by a minor second.
    Also changes note.style.color for rule 4 (orange green orange).

    returns the number of notes that were changed

    This rule is a less likely interpretation of the ambiguous rule 4, thus
    applyCapuaToStream uses capuaRuleFourB instead.
    '''
    numChanged = 0

    ssn = srcStream.flat.notesAndRests
    for i in range(len(ssn) - 2):
        n1 = ssn[i]
        n2 = ssn[i + 1]
        n3 = ssn[i + 2]

        if n1.isRest or n2.isRest or n3.isRest:
            continue

        i1 = interval.notesToInterval(n1, n2)
        i2 = interval.notesToInterval(n2, n3)

        if (n1.pitch.accidental is not None
                or n2.pitch.accidental is not None
                or n3.pitch.accidental is not None):
            continue

        # never seems to improve things...
        if n2.step == 'A' or n2.step == 'D':
            continue

        # e.g., D B A => D Bb A
        if i1.directedName == 'm-3' and i2.directedName == 'M-2':
            numChanged += 1
            if 'capuaRuleNumber' in n2.editorial:
                n2.editorial.capuaRuleNumber += RULE_FOUR_A
            else:
                n2.editorial.capuaRuleNumber = RULE_FOUR_A
            n2.editorial.ficta = pitch.Accidental('flat')
            n2.editorial.capuaFicta = pitch.Accidental('flat')
            n1.style.color = 'orange'
            n2.style.color = 'ForestGreen'
            n3.style.color = 'orange'

    return numChanged


def capuaRuleFourB(srcStream):
    '''
    See capuaRuleOne for precise instructions.

    Applies more probable interpretation of Capua's fourth rule to the given
    srcStream, i.e. if a descending minor third is followed by a descending major
    second, the intervals will be changed to a major third followed by a minor
    second. Also copies any relevant accidental to note.editorial.savedAccidental
    and changes note.style.color for rule 4 (orange
    green orange).

    returns the number of times a note was changed.
    '''
    numChanged = 0
    ssn = srcStream.flat.notesAndRests
    for i in range(len(ssn) - 2):
        n1 = ssn[i]
        n2 = ssn[i + 1]
        n3 = ssn[i + 2]

        if n1.isRest or n2.isRest or n3.isRest:
            continue

        i1 = interval.notesToInterval(n1, n2)
        i2 = interval.notesToInterval(n2, n3)

        if (n1.pitch.accidental is not None
                or n3.pitch.accidental is not None):
            continue

        # never seems to improve things...
        if n2.step == 'A' or n2.step == 'D':
            continue

        # e.g., D F G => D F# G  or G Bb C => G B C
        if i1.directedName == 'm3' and i2.directedName == 'M2':
            numChanged += 1
            if 'capuaRuleNumber' in n2.editorial:
                n2.editorial.capuaRuleNumber += RULE_FOUR_B
            else:
                n2.editorial.capuaRuleNumber = RULE_FOUR_B
            if n2.pitch.accidental is not None and n2.pitch.accidental.name == 'flat':
                n2.editorial.savedAccidental = n2.pitch.accidental
                n2.pitch.accidental = None
                n2.editorial.ficta = pitch.Accidental('natural')
                n2.editorial.capuaFicta = pitch.Accidental('natural')
                n1.style.color = 'orange'
                n2.style.color = 'green'
                n3.style.color = 'orange'
            else:
                n2.editorial.ficta = pitch.Accidental('sharp')
                n2.editorial.capuaFicta = pitch.Accidental('sharp')
                n1.style.color = 'orange'
                n2.style.color = 'green'
                n3.style.color = 'orange'

    return numChanged


def clearFicta(srcStream1):
    '''
    In the given srcStream, moves anything under note.editorial.ficta into
    note.editorial.savedFicta.
    '''

    for n2 in srcStream1.flat.notes:
        if hasattr(n2.editorial, 'ficta'):
            n2.editorial.savedFicta = n2.editorial.ficta
        n2.editorial.ficta = None


def restoreFicta(srcStream1):
    '''
    In the given srcStream, moves anything under note.editorial.savedFicta
    back to note.editorial.ficta.
    '''
    for n2 in srcStream1:
        if hasattr(n2.editorial, 'savedFicta') and n2.editorial.savedFicta is not None:
            n2.editorial.ficta = n2.editorial.savedFicta
            n2.editorial.savedFicta = None


def clearAccidental(note1):
    '''
    moves the accidental to `note1.editorial.savedAccidental` and
    clears `note1.pitch.accidental`
    '''
    if note1.pitch.accidental is not None:
        note1.editorial.savedAccidental = note1.pitch.accidental
        note1.pitch.accidental = None


def restoreAccidental(note1):
    '''
    takes `Note.editorial.savedAccidental` and moves it back
    to the `Note.pitch.accidental`
    '''
    if hasattr(note1.editorial, 'savedAccidental'):
        note1.pitch.accidental = note1.editorial.savedAccidental
        note1.editorial.savedAccidental = None


def fictaToAccidental(note1):
    '''
    Moves the ficta (if any) in `Note.editorial.ficta` to the accidental
    '''
    if note1.editorial.ficta is not None:
        if note1.pitch.accidental is not None:
            clearAccidental(note1)
        note1.pitch.accidental = note1.editorial.ficta


def pmfcFictaToAccidental(note1):
    '''
    Moves any ficta in `Note.editorial.pmfcFicta` to the `Note.pitch.accidental`
    object and saves the previous accidental by calling `clearAccidental()` first.
    '''
    if (hasattr(note1.editorial, 'pmfcFicta')
            and note1.editorial.pmfcFicta is not None):
        clearAccidental(note1)
        note1.pitch.accidental = note1.editorial.pmfcFicta


def capuaFictaToAccidental(note1):
    '''
    Moves Capua's ficta from `Note.editorial.capuaFicta` to the
    `Note.pitch.accidental` object.  Saves the previous accidental by calling
    `clearAccidental` first.
    '''
    if (hasattr(note1.editorial, 'capuaFicta')
            and note1.editorial.capuaFicta is not None):
        clearAccidental(note1)
        note1.pitch.accidental = note1.editorial.capuaFicta


def evaluateRules(srcStream1, srcStream2):
    '''
    Runs evaluation method for capua on one srcStream only, and evaluating harmonies,
    for each srcStream; then runs method for applying capua rules to both and evaluating
    the resulting harmonies.
    '''
    # Returns SOMETHING USEFUL TO BE DETERMINED
    # srcStream1Count = evaluateCapuaOnesrcStream(srcStream1, srcStream2)
    # srcStream2Count = evaluateCapuaOnesrcStream(srcStream2, srcStream1)
    bothCount = evaluateCapuaTwoStreams(srcStream1, srcStream2)
    # do something with them...
    return bothCount


def evaluateCapuaOnesrcStream(srcStream1, srcStream2):
    '''
    Runs Capua rules on one srcStream only and evaluates the harmonies; stores harmonies
    under 'capua1FictaHarmony' in note.editorial; returns a list of the number of
    [perfect cons, imperfect cons, dissonances].
    '''
    applyCapuaToStream(srcStream1)
    for note1 in srcStream1:
        capuaFictaToAccidental(note1)
    srcStream1Count = compareOnesrcStream(srcStream1, srcStream2, 'capua1srcStream')
    for note1 in srcStream1:
        restoreAccidental(note1)
    return srcStream1Count


def evaluateCapuaTwoStreams(srcStream1, srcStream2):
    '''
    Runs Capua rules on both srcStreams and evaluates the harmonies; stores harmonies
    under 'capua2FictaHarmony' in note.editorial; returns a dictionary that contains
    the number of [perfect cons, imperfect cons, dissonances] for each srcStream, which can
    be obtained with keys 'srcStream1Count' and 'srcStream2Count'.
    '''
    applyCapuaToStream(srcStream1)
    applyCapuaToStream(srcStream2)
    for note1 in srcStream1:
        capuaFictaToAccidental(note1)
    for note2 in srcStream2:
        capuaFictaToAccidental(note2)
    srcStream1Count = compareOnesrcStream(srcStream1, srcStream2, 'capua2srcStream')
    srcStream2Count = compareOnesrcStream(srcStream2, srcStream1, 'capua2srcStream')
    for note1 in srcStream1:
        restoreAccidental(note1)
    for note2 in srcStream2:
        restoreAccidental(note2)
    bothCount = {
        'srcStream1Count': srcStream1Count,
        'srcStream2Count': srcStream2Count,
    }
    return bothCount


def evaluateEditorsFicta(srcStream1, srcStream2):
    '''
    Runs pmfcFictaToAccidental, then runs the evaluation method on the two srcStreams.
    Returns editorProfile, a list of lists with the number of perfect cons, imperfect
    cons, and dissonances for each srcStream.
    '''
    for note1 in srcStream1:
        pmfcFictaToAccidental(note1)
    for note2 in srcStream2:
        pmfcFictaToAccidental(note2)
    editorProfile = compareOnesrcStream(srcStream1, srcStream2, 'editor')
    for note1 in srcStream1:
        restoreAccidental(note1)
    for note2 in srcStream2:
        restoreAccidental(note2)
    return editorProfile


def evaluateWithoutFicta(srcStream1, srcStream2):
    '''
    Clears all ficta, then evaluates the harmonies of the two srcStreams. Returns
    a list of lists of the interval counts for each.
    '''
    clearFicta(srcStream1)  # probably not necessary to clear ficta, but just to be safe
    clearFicta(srcStream2)
    noneProfile1 = compareOnesrcStream(srcStream1, srcStream2, '')
    # noneProfile2 = compareOnesrcStream(srcStream2, srcStream1, '')
    restoreFicta(srcStream1)
    restoreFicta(srcStream2)
    return noneProfile1


PerfectCons = ['P1', 'P5', 'P8']
ImperfCons = ['m3', 'M3', 'm6', 'M6']
Others = ['m2', 'M2', 'A2', 'd3', 'A3', 'd4', 'P4', 'A4', 'd5', 'A5', 'd6',
          'A6', 'd7', 'm7', 'M7', 'A7']

PERFCONS = 1
IMPERFCONS = 2
OTHERS = 3


def compareThreeFictas(srcStream1, srcStream2):
    '''
    compares the output of noFicta, pmfcFicta, and capuaFicta and attaches each interval
    to a note.editorial tag.

    srcStream1 and srcStream2 should be .flat.notesAndRests

    >>> b = cadencebook.BallataSheet().makeWork(331).asScore()
    >>> #_DOCS_SHOW b.show()
    >>> b0n = b.parts[0].flat.notesAndRests.stream()
    >>> b1n = b.parts[1].flat.notesAndRests.stream()
    >>> applyCapuaToStream(b0n)
    >>> compareThreeFictas(b0n, b1n)
    >>> for n in b0n:
    ...    pass
    '''
    # populates the editorial.interval attribute on each note
    srcStream1.attachIntervalsBetweenStreams(srcStream2)
    srcStream2.attachIntervalsBetweenStreams(srcStream1)

    for note1 in srcStream1.notes:
        if hasattr(note1.editorial.harmonicInterval, 'name'):
            note1.editorial.normalHarmonicInterval = note1.editorial.harmonicInterval.name

        if 'pmfcFicta' in note1.editorial:
            pmfcFictaToAccidental(note1)
            note1.editorial.harmonicInterval.reinit()
            if hasattr(note1.editorial.harmonicInterval, 'name'):
                note1.editorial.pmfcHarmonicInterval = note1.editorial.harmonicInterval.name
            restoreAccidental(note1)
        else:
            if hasattr(note1.editorial.harmonicInterval, 'name'):
                note1.editorial.pmfcHarmonicInterval = note1.editorial.harmonicInterval.name
        if 'capuaFicta' in note1.editorial:
            capuaFictaToAccidental(note1)
            note1.editorial.harmonicInterval.reinit()
            if hasattr(note1.editorial.harmonicInterval, 'name'):
                note1.editorial.capuaHarmonicInterval = note1.editorial.harmonicInterval.name
            restoreAccidental(note1)
        else:
            if hasattr(note1.editorial.harmonicInterval, 'name'):
                note1.editorial.capuaHarmonicInterval = note1.editorial.harmonicInterval.name


def compareSrcStreamCapuaToEditor(srcStream1):
    '''
    takes a Stream (can be flat.notesAndRests or not) and
    returns a dictionary showing how many notes
    are there `totalNotes`, how many the editors of PMFC altered, how many
    the Capua program altered, how many PMFC but not Capua altered and how
    many both altered.
    '''

    totalDict = {
        'totalNotes': 0,
        'pmfcAlt': 0,
        'capuaAlt': 0,
        'pmfcNotCapua': 0,
        'capuaNotPmfc': 0,
        'pmfcAndCapua': 0,
        }
    for note1 in srcStream1.flat.notesAndRests:
        thisDict = compareNoteCapuaToEditor(note1)
        for thisKey in thisDict:
            totalDict[thisKey] += thisDict[thisKey]
    return totalDict


def compareNoteCapuaToEditor(note1):
    '''
    Takes in a single note and returns a dictionary showing how many notes
    are there `totalNotes`, how many the editors of PMFC altered, how many
    the Capua program altered, how many PMFC but not Capua altered and how
    many both altered.

    To be added up by compareSrcStreamCapuaToEditor.  To be run after applyCapua.
    '''
    statsDict = {
        'totalNotes': 0,
        'pmfcAlt': 0,
        'capuaAlt': 0,
        'pmfcNotCapua': 0,
        'capuaNotPmfc': 0,
        'pmfcAndCapua': 0,
        }

    if note1.isRest:
        return statsDict
    statsDict['totalNotes'] += 1
    if 'pmfcFicta' in note1.editorial and 'capuaFicta' in note1.editorial:
        statsDict['pmfcAlt'] += 1
        statsDict['capuaAlt'] += 1
        statsDict['pmfcAndCapua'] += 1
    elif 'pmfcFicta' in note1.editorial:
        statsDict['pmfcAlt'] += 1
        statsDict['pmfcNotCapua'] += 1
    elif 'capuaFicta' in note1.editorial:
        statsDict['capuaAlt'] += 1
        statsDict['capuaNotPmfc'] += 1
    return statsDict


def compareOnesrcStream(srcStream1, srcStream2, fictaType='editor'):
    '''
    Helper function for evaluating Harmony that for each note in srcStream1 determines
    that notes starting interval in relation to srcStream2, and assigns identifiers to
    the fictaHarmony and fictaInterval in note.editorial if there is ficta, or to the
    noFictaHarmony if there is no ficta for that note. Returns a list of the number
    of perfect consonances, imperfect consonances, and other (dissonances) for srcStream1.
    For the fictaType variable, write 'editor' or 'capua', 'capua1srcStream' or 'capua2srcStream'.
    '''
    perfectConsCount = 0
    imperfConsCount = 0
    othersCount = 0

    # populates the note.editorial.harmonicInterval object
    srcStream1.attachIntervalsBetweenStreams(srcStream2)
    srcStream2.attachIntervalsBetweenStreams(srcStream1)
    for note1 in srcStream1.notes:
        hasFicta = False
        interval1 = note1.editorial.harmonicInterval
        if interval1 is None:
            continue   # must have a rest in the other voice
        # name1 = interval1.diatonic.name
        # read ficta as actual accidental
        if note1.editorial.ficta is not None:
            hasFicta = True

        iType = getIntervalType(interval1)
        if hasFicta and fictaType == 'editor':
            environLocal.printDebug('found ficta of Editor type')
            note1.editorial.editorFictaHarmony = iType
            note1.editorial.editorFictaInterval = interval1
        elif hasFicta and fictaType == 'capua1srcStream':
            environLocal.printDebug('found ficta of capua1srcStream type')
            note1.editorial.capua1FictaHarmony = iType
            note1.editorial.capua1FictaInterval = interval1
        elif hasFicta and fictaType == 'capua2srcStream':
            environLocal.printDebug('found ficta of capua2srcStream type')
            note1.editorial.capua2FictaHarmony = iType
            note1.editorial.capua2FictaInterval = interval1
        else:
            note1.editorial.noFictaHarmony = iType

        if iType == 'perfect cons':
            perfectConsCount += 1
        elif iType == 'imperfect cons':
            imperfConsCount += 1
        elif iType == 'dissonance':
            othersCount += 1
        else:
            raise CapuaException('Hmmm.... I thought we already trapped this for errors...')
    return [perfectConsCount, imperfConsCount, othersCount]


def getIntervalType(interval1):
    '''returns either None (if interval is undef),  'perfect cons', 'imperfect cons', 'dissonance'
    or an error depending on how the interval fits into 14th century harmonic principles'''
    if interval1 is None:
        return None
    elif interval1.diatonic is None:
        return None
    elif interval1.diatonic.name in PerfectCons:
        return 'perfect cons'
    elif interval1.diatonic.name in ImperfCons:
        return 'imperfect cons'
    elif interval1.diatonic.name in Others:
        return 'dissonance'
    else:
        raise CapuaException(
            'Wow!  The first ' + interval1.niceName
            + ' I have ever seen in 14th century music!  Go publish!  (or check for errors...)'
        )


betterColor = 'green'
worseColor = 'red'
neutralColor = 'blue'


def colorCapuaFicta(srcStream1, srcStream2, oneOrBoth='both'):
    '''
    Given two srcStreams, applies the capua rules and colors each note (in
    note.editorial.fictaColor) as compared to the srcStreams with no ficta,
    using betterColor, worseColor, and neutralColor.

    '''
    srcStream1.attachIntervalsBetweenStreams(srcStream2)
    srcStream2.attachIntervalsBetweenStreams(srcStream1)
    capuaCount = evaluateRules(srcStream1, srcStream2)
    environLocal.printDebug('Capua count: %r' % capuaCount)
    noFictaCount = evaluateWithoutFicta(srcStream1, srcStream2)
    environLocal.printDebug('No ficta count: %r' % noFictaCount)
    for note1 in srcStream1:
        colorNote(note1, oneOrBoth)
    for note2 in srcStream2:
        colorNote(note2, oneOrBoth)


def colorNote(note1, oneOrBoth='both'):
    '''
    Applies all rules to a note according to what harmonies are better/worse/neutral.
    '''
    if 'capua2FictaHarmony' not in note1.editorial:
        return
    elif oneOrBoth == 'one':
        capuaHarmony = note1.editorial.capua1FictaHarmony
    elif oneOrBoth == 'both':
        capuaHarmony = note1.editorial.capua2FictaHarmony
    else:
        raise CapuaException('Please specify "one" or "both" for the variable "oneOrBoth".')
    nonCapuaHarmony = note1.editorial.noFictaHarmony
    # nonCapuaHarmony = getIntervalType(nonCapuaInterval)
    ruleOne(note1, nonCapuaHarmony, capuaHarmony)
    # ruleTwo(....), ruleThree(...), and so on


def ruleOne(note1, nonCapuaHarmony, capuaHarmony):
    '''
    Colors a note based on the rule dissonance -> perfect cons is better,
    perfect cons -> dissonance is worse.
    '''
    if nonCapuaHarmony == 'dissonance' and capuaHarmony == 'perfect cons':
        note1.editorial.fictaColor = betterColor
        # can put the color somewhere else; I didn't want to step on the color-coded
        # capua rules
    elif nonCapuaHarmony == 'perfect cons' and capuaHarmony == 'dissonance':
        note1.editorial.fictaColor = worseColor


def findCorrections(correctionType='Maj3', startPiece=2, endPiece=459):
    '''
    Find all cases where a Major 3rd moves inward to unison (within the next two or
    three notes, excluding rests)
    and see how often the PMFC editors correct it to minor 3rd and how often Capua gets it.

    or if correctionType == 'min6' find all instances of a minor 6th moving outward to
    octave and see how often the PMFC
    editors correct it to a Major 6th and how often Capua gets it.

#    >>> from pprint import pprint as pp
#    >>> (totalDict, foundPieceOpus) = findCorrections(correctionType='Maj3', 2, 50)
#    >>> pp(totalDict)
#    {'potentialChange': 82, 'capuaAlt': 30, 'pmfcAndCapua': 3, 'capuaNotPmfc': 27,
#        'pmfcAlt': 4, 'pmfcNotCapua': 1, 'totalNotes': 82}
#    >>> foundPieceOpus.show('lily.pdf')

#    >>> (totalDict, foundPieceOpus) = findCorrections(correctionType='min6')
#    >>> pp(totalDict)
#    {'potentialChange': 82, 'capuaAlt': 30, 'pmfcAndCapua': 3, 'capuaNotPmfc': 27,
#        'pmfcAlt': 4, 'pmfcNotCapua': 1, 'totalNotes': 82}
#    >>> foundPieceOpus.show('lily.pdf')

#    >>> #_DOCS_SHOW (totalDict, foundPieceOpus) = correctedMin6()
#    >>> totalDict = {'potentialChange': 82, 'capuaAlt': 30, 'pmfcAndCapua': 3, #_DOCS_HIDE
#    ...    'capuaNotPmfc': 27, 'pmfcAlt': 4, 'pmfcNotCapua': 1, 'totalNotes': 82} #_DOCS_HIDE
#    >>> pp(totalDict)
#    {'alterAll': 82, 'capuaAlt': 30, 'pmfcAndCapua': 3, 'capuaNotPmfc': 27,
#        'pmfcAlt': 4, 'pmfcNotCapua': 1, 'totalNotes': 82}
#    >>> #_DOCS_SHOW foundPieceOpus.show('lily.pdf')

    '''
    ballataObj = cadencebook.BallataSheet()
    totalDict = {
        'totalNotes': 0,
        'pmfcAlt': 0,
        'capuaAlt': 0,
        'pmfcNotCapua': 0,
        'capuaNotPmfc': 0,
        'pmfcAndCapua': 0,
        'potentialChange': 0
        }

    if correctionType == 'Maj3':
        notesToCheck = 1
        simpleNameToCheck = 'm3'
    elif correctionType == 'min6':
        notesToCheck = 2  # allows Landini cadences, but not much more
        simpleNameToCheck = 'M6'
    else:
        raise CapuaException('Invalid correctionType to check; I can check "Maj3" or "min6"')

    foundPieceOpus = stream.Opus()

    for j in range(startPiece, endPiece):  # all ballate
        pieceObj = ballataObj.makeWork(j)  # N.B. -- we now use Excel column numbers
        if pieceObj.incipit is None:
            continue
        environLocal.warn('Working on piece number %d, %s ' % (j, pieceObj.title))
        for thisSnippet in pieceObj.snippets:
            thisSnippetAppended = False
            if thisSnippet is None:
                continue
            if 'Incipit' in thisSnippet.classes:
                continue
            thisSnippetParts = thisSnippet.parts
            if len(thisSnippetParts) < 2:
                continue
            srcStream1 = thisSnippetParts['C'].flat.notesAndRests
            srcStream2 = thisSnippetParts['T'].flat.notesAndRests
            # ignore 3rd voice for now...
            srcStream1.attachIntervalsBetweenStreams(srcStream2)
            srcStream2.attachIntervalsBetweenStreams(srcStream1)

            if thisSnippetAppended is False:
                foundPieceOpus.insert(0, thisSnippet)
                thisSnippetAppended = True
            applyCapuaToStream(srcStream1)
            applyCapuaToStream(srcStream2)

            for ss in [srcStream1, srcStream2]:
                srcStreamNotes = ss.notes  # get rid of rests
                srcStreamLen = len(srcStreamNotes)
                for (i, note1) in enumerate(srcStreamNotes):
                    if (note1.editorial.harmonicInterval is None
                            or note1.editorial.harmonicInterval.simpleName != simpleNameToCheck):
                        continue
                    if i >= srcStreamLen - notesToCheck:
                        if i == srcStreamLen - 1:
                            continue
                        else:
                            nextFewNotes = srcStreamNotes[i + 1:]
                    else:
                        nextFewNotes = srcStreamNotes[(i + 1):(i + 1 + notesToCheck)]
                    # nextFewNotes = srcStream1.notesFollowingNote(note1,
                    #                       notesToCheck, allowRests = False)
                    foundP8 = False
                    for thisNote in nextFewNotes:
                        if thisNote is None:
                            raise CapuaException(
                                'This was only supposed to return non-None, what is up???')
                        if thisNote.editorial.harmonicInterval is None:
                            continue  # probably a rest; should not happen
                        if (correctionType == 'Maj3'
                                and thisNote.editorial.harmonicInterval.simpleName == 'P1'):
                            foundP8 = True
                        elif (correctionType == 'min6'
                                and thisNote.editorial.harmonicInterval.semiSimpleName == 'P8'):
                            foundP8 = True
                    if foundP8 is False:
                        continue
                    newResults = compareNoteCapuaToEditor(note1)
                    newResults['potentialChange'] = 1
                    for thisKey in newResults:
                        if thisKey == 'alterAll':
                            continue
                        if (thisKey == 'capuaNotPmfc'
                                and newResults[thisKey] == 1
                                and thisSnippetAppended is False):
                            foundPieceOpus.insert(0, thisSnippet)
                            thisSnippetAppended = True
                        totalDict[thisKey] += newResults[thisKey]

    return totalDict, foundPieceOpus


def improvedHarmony(startPiece=2, endPiece=459):
    '''
    Find how often an augmented or diminished interval was corrected to a perfect
    interval and vice-versa
    by capua.

    Returns a dict showing the results


    >>> #_DOCS_SHOW improvedHarmony()
    >>> print("{'imperfCapua': 22, 'imperfIgnored': 155, " + #_DOCS_HIDE
    ...    "'perfCapua': 194, 'perfIgnored': 4057}") #_DOCS_HIDE
    {'imperfCapua': 22, 'imperfIgnored': 155, 'perfCapua': 194, 'perfIgnored': 4057}
    '''

    ballataObj = cadencebook.BallataSheet()

    checkDict = {
                 'perfIgnored': 0,
                 'perfCapua': 0,
                 'imperfIgnored': 0,
                 'imperfCapua': 0
                 }

    for j in range(startPiece, endPiece):  # all ballate
        # environLocal.printDebug('Working on piece number %d ' % j)
        pieceObj = ballataObj.makeWork(j)  # N.B. -- we now use Excel column numbers
        if pieceObj.incipit is None:
            continue
        for thisSnippet in pieceObj.snippets:
            # thisSnippetAppended = False
            if thisSnippet is None:
                continue
            if 'Incipit' in thisSnippet.classes:
                continue
            thisSnippetParts = thisSnippet.parts
            if len(thisSnippetParts) < 2:
                continue
            srcStream1 = thisSnippetParts['C'].flat.notesAndRests
            srcStream2 = thisSnippetParts['T'].flat.notesAndRests  # ignore 3rd voice for now...
            srcStream1.attachIntervalsBetweenStreams(srcStream2)
            # srcStream2.attachIntervalsBetweenStreams(srcStream1)
            applyCapuaToStream(srcStream1)

            for ss in [srcStream1, srcStream2]:
                srcStreamNotes = ss.notes  # get rid of rests
                # srcStreamLen = len(srcStreamNotes)

                for (i, note1) in enumerate(srcStreamNotes):
                    hI = note1.editorial.harmonicInterval
                    if (hI is None or
                            hI.generic.perfectable is False or
                            hI.generic.simpleUndirected == 4):
                        continue

                    # KEEP PROGRAMMING FROM HERE
                    if hI.diatonic.specificName == 'Perfect':
                        if 'capuaFicta' in note1.editorial:
                            checkDict['perfCapua'] += 1  # ugh, Capua changed a P1, P5, or P8
                        else:
                            checkDict['perfIgnored'] += 1  # yay, Capua left it alone
                    else:
                        if 'capuaFicta' in note1.editorial:
                            checkDict['imperfCapua'] += 1
                            # yay Capua changed a A1 or d1, A5 or d5, or A8 or d8
                        else:
                            checkDict['imperfIgnored'] += 1  # hrumph, Capua left it alone

    return checkDict


def runPiece(pieceNum=331, snipNum=0):  # random default piece...
    ballataObj = cadencebook.BallataSheet()
    pieceObj = ballataObj.makeWork(pieceNum)
    # pieceObj.snippets[0].lily.showPNG()
    applyCapuaToScore(pieceObj)
    # pieceObj.snippets[snipNum].show('lily.png')
    srcStream = pieceObj.snippets[snipNum].parts[0].flat.notesAndRests
    cmpStream = pieceObj.snippets[snipNum].parts[1].flat.notesAndRests
    # ignore 3rd voice for now...
    srcStream.attachIntervalsBetweenStreams(cmpStream)

    for n in srcStream.notes:
        if n.editorial.harmonicInterval is not None:
            environLocal.printDebug(n.name)
            environLocal.printDebug(n.editorial.harmonicInterval.semiSimpleName)
            if 'capuaFicta' in n.editorial:
                environLocal.printDebug(n.editorial.capuaFicta)


def ruleFrequency(startNumber=2, endNumber=459):
    ballataObj = cadencebook.BallataSheet()
    num1 = 0
    num2 = 0
    num3 = 0
    num4a = 0
    num4b = 0
    for i in range(startNumber, endNumber):  # all ballate
        pieceObj = ballataObj.makeWork(i)  # N.B. -- we now use Excel column numbers
        for thisPolyphonicSnippet in pieceObj.snippets:
            if thisPolyphonicSnippet is None:
                continue
            for thisPart in thisPolyphonicSnippet.parts:
                thisStream = thisPart.flat.notes
                num1 += capuaRuleOne(thisStream)
                num2 += capuaRuleTwo(thisStream)
                num3 += capuaRuleThree(thisStream)
                num4a += capuaRuleFourA(thisStream)
                num4b += capuaRuleFourB(thisStream)

    return num1, num2, num3, num4a, num4b


class Test(unittest.TestCase):

    def runTest(self):
        pass

    def testRunNonCrederDonna(self):
        pieceNum = 331  # Francesco, PMFC 4 6-7: Non creder, donna
        ballataObj = cadencebook.BallataSheet()
        pieceObj = ballataObj.makeWork(pieceNum)

        applyCapuaToCadencebookWork(pieceObj)
        srcStream = pieceObj.snippets[0].parts[0].flat.notesAndRests.stream()
        cmpStream = pieceObj.snippets[0].parts[1].flat.notesAndRests.stream()
        # ignore 3rd voice for now...
        srcStream.attachIntervalsBetweenStreams(cmpStream)
        cmpStream.attachIntervalsBetweenStreams(srcStream)

        # colorCapuaFicta(srcStream, cmpStream, 'both')

        outList = []
        for n in srcStream:
            if n.editorial.harmonicInterval is not None:
                outSublist = [n.name, n.editorial.harmonicInterval.simpleName]
                if 'capuaFicta' in n.editorial:
                    outSublist.append(repr(n.editorial.capuaFicta))
                else:
                    outSublist.append(None)
                outList.append(outSublist)

        self.assertEqual(outList,
                         [
                             ['A', 'P5', None], ['A', 'M6', None],
                             ['G', 'P5', None], ['G', 'm6', None],
                             ['A', 'm7', None], ['F', 'd5', '<accidental sharp>'],
                             ['G', 'm6', None], ['A', 'P1', None],
                             ['B', 'M6', None], ['A', 'P5', None],
                             ['G', 'm7', None], ['G', 'm6', None],
                             ['F', 'd5', None], ['E', 'M3', None],
                             ['D', 'P1', None]
                          ])
        # pieceObj.asOpus().show('lily.pdf')

        return pieceObj

    def testRun1(self):
        ballataSht = cadencebook.BallataSheet()
        pieceObj = ballataSht.makeWork(20)  # N.B. -- we now use Excel column numbers
        if pieceObj.incipit is None:
            return None
        cadenceA = pieceObj.cadenceA
        if len(cadenceA.parts) >= 2:
            srcStream1 = cadenceA.parts[0].flat.notes.stream()
            srcStream2 = cadenceA.parts[1].flat.notes.stream()  # ignore 3rd voice for now...
            clearFicta(srcStream1)
            compareThreeFictas(srcStream1, srcStream2)
            cons, imperfCons, diss = compareOnesrcStream(srcStream1, srcStream2)

            restoreFicta(srcStream1)
            self.assertEqual([cons, imperfCons, diss], [4, 3, 3])

    def testColorCapuaFicta(self):
        from music21.note import Note
        from music21.stream import Stream

        (n11, n12, n13, n14) = (Note('D'), Note('E'), Note('F'), Note('G'))
        (n21, n22, n23, n24) = (Note('C'), Note('C'), Note('B3'), Note('C'))

        stream1 = Stream()
        stream1.append([n11, n12, n13, n14])
        stream2 = Stream()
        stream2.append([n21, n22, n23, n24])

        # Need twoStreamComparer to Work
        evaluateWithoutFicta(stream1, stream2)
        assert n13.editorial.harmonicInterval.name == 'd5', n13.editorial.harmonicInterval.name
        evaluateCapuaTwoStreams(stream1, stream2)

        colorCapuaFicta(stream1, stream2, 'both')
        assert n13.editorial.harmonicInterval.name == 'P5', n13.editorial.harmonicInterval.name
#
#        assert n11.style.color == 'yellow'
#        assert n12.style.color == 'yellow'
#        assert n13.style.color == 'green'
#        assert n14.style.color == 'yellow'
#
#        assert n11.editorial.harmonicInterval.name == 'M2'
#        assert n21.editorial.harmonicInterval.name == 'M2'
#
#        assert n13.editorial.harmonicInterval.name == 'P5'
#        assert n13.editorial.noFictaHarmony == 'perfect cons'
#        assert n13.editorial.capua2FictaHarmony == 'perfect cons'
#        assert n13.editorial.capua2FictaInterval.name == 'P5'
#        assert n13.style.color == 'green'


class TestExternal(unittest.TestCase):  # pragma: no cover
    def runTest(self):
        pass

    def testRunNonCrederDonna(self):
        t = Test()
        pObj = t.testRunNonCrederDonna()
        pObj.asOpus().show('lily.png')

    def testShowFourA(self):
        ballataObj = cadencebook.BallataSheet()
        showStream = stream.Opus()
        for i in range(2, 45):  # 459): # all ballate
            pieceObj = ballataObj.makeWork(i)  # N.B. -- we now use Excel column numbers
            theseSnippets = pieceObj.snippets
            for thisSnippet in theseSnippets:
                if thisSnippet is None:
                    continue
                appendSnippet = False
                theseStreams = thisSnippet.parts
                for thisStream in theseStreams:
                    if capuaRuleFourA(thisStream) > 0:
                        appendSnippet = True
                if appendSnippet is True:
                    showStream.insert(0, thisSnippet)

        showStream.show('lily.pdf')


class TestSlow(unittest.TestCase):

    def runTest(self):
        pass

    def testCompare1(self):
        ballataObj = cadencebook.BallataSheet()
        totalDict = {
            'totalNotes': 0,
            'pmfcAlt': 0,
            'capuaAlt': 0,
            'pmfcNotCapua': 0,
            'capuaNotPmfc': 0,
            'pmfcAndCapua': 0,
            }

        for i in range(232, 349):  # 232-349 is most of Landini PMFC
            pieceObj = ballataObj.makeWork(i)  # N.B. -- we now use Excel column numbers
            if pieceObj.incipit is None:
                continue
            environLocal.printDebug(pieceObj.title)
            cadenceA = pieceObj.cadenceA
            if cadenceA is not None and len(cadenceA.parts) >= 2:
                srcStream1 = cadenceA.parts[0]  # .flat.notesAndRests
                # srcStream2 = cadenceA.parts[1].flat.notesAndRests
                # # ignore 3rd voice for now...
                # twoStreams1 = twoStreams.TwoStreamComparer(srcStream1, srcStream2)
                # twoStreams1.intervalToOtherStreamWhenAttacked()
                # srcStream1.attachIntervalsBetweenStreams(srcStream2)
                # srcStream2.attachIntervalsBetweenStreams(srcStream1)

                applyCapuaToStream(srcStream1)
                thisDict = compareSrcStreamCapuaToEditor(srcStream1)
                for thisKey in thisDict:
                    totalDict[thisKey] += thisDict[thisKey]

        self.assertEqual(totalDict['capuaAlt'], 18)
        self.assertEqual(totalDict['totalNotes'], 200)
        environLocal.printDebug(totalDict)

    def testRuleFrequency(self):
        import time
        print(time.ctime())
        (num1, num2, num3, num4a, num4b) = ruleFrequency()
        print(time.ctime())
        print(num1)
        print(num2)
        print(num3)
        print(num4a)
        print(num4b)
        self.assertEqual(num4a,  57)
        self.assertEqual(num4b, 104)


if __name__ == '__main__':
    # runPiece(267)
    # (totalDict, foundPieceOpus) = findCorrections(correctionType='min6',
    #             startPiece=21, endPiece=22)
    # print totalDict
    # if len(foundPieceOpus) > 0:
    #     foundPieceOpus.show('lily.png')
    import music21
    music21.mainTest(Test, 'importPlusRelative')  # , TestExternal)

    # correctedMin6()
    # correctedMaj3()
    # improvedHarmony()
