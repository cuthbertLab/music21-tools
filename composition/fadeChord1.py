'''
Experiment in fading from one chord to another
'''
from copy import deepcopy
from typing import cast

import math

from music21 import *


def smooth01(steps):
    # f(x) = arcsin(2x-1)/pi+1/2
    out = []
    for i in range(1, steps+1):
        frac = i/steps
        out.append(math.asin(2*frac-1)/math.pi + 1/2)
    return out

    # return [0] + [math.asin(2*(i/steps)+1)/math.pi + 1/2 for i in range(1, steps-1)] + [1]
    # return [math.sin((i+1)/steps * math.pi/2) for i in range(steps)]
    # return [-1*(math.cos((i+1)/steps * math.pi) - 1)/2 for i in range(steps)]


def main():
    reps = 20
    basis = cast(stream.Measure, converter.parse("tinynotation: 2/4 c16 d e f g a c' b")
                 .getElementsByClass('Measure').first())
    vols = [[1, 0, 1, 0, 1, 0, 1, 0] * reps]
    smooths = smooth01(reps)
    for i, n in enumerate(basis.notes):
        n.volume.velocityScalar = vols[0][i]
    notes = basis[note.Note]
    notes[0].groups.append('C')
    notes[1].groups.append('D')
    notes[2].groups.append('E')
    notes[3].groups.append('F')
    # notes[3].offset -= 0.25
    notes[4].groups.append('G')
    notes[5].groups.append('A')
    notes[6].groups.append('CC')
    notes[7].groups.append('B')

    part = stream.Part()
    for rep_n in range(reps):
        new_measure = deepcopy(basis)
        part.append(new_measure)

    fade_note(part, 'F', 2, 8)  # , pos_offset_at_zero=0.25)
    fade_note(part, 'E', 4, 12, fade_out=True)  # , pos_offset_at_zero=-0.25)
    fade_note(part, 'D', 6, 12)
    fade_note(part, 'C', 8, 15, fade_out=True)
    fade_note(part, 'A', 11, 16)
    fade_note(part, 'B',  9, 16)
    fade_note(part, 'CC', 11, 18, fade_out=True)
    fade_note(part, 'G', 12, 19, fade_out=True)

    part.show('midi')
    part.write('midi', '/Users/cuthbert/Desktop/t1.mid')


def fade_note(
    part,
    group_name,
    start_rep,
    end_rep,
    fade_out=False,
    pos_offset_at_zero=0.0,
):
    reps = end_rep - start_rep
    smooths = smooth01(reps)
    positions = [(1-s) * pos_offset_at_zero for s in smooths]
    if fade_out:
        smooths = [1-s for s in smooths]

    m: stream.Measure
    for i, m in enumerate(part.getElementsByClass('Measure')):
        if i < start_rep:
            continue
        found = m.getElementsByClass(note.Note).getElementsByGroup(group_name)
        index_in_smooths = i-start_rep if i < end_rep else end_rep-1-start_rep
        # print(index_in_smooths, smooths)
        for n in found:
            n.volume.velocityScalar = smooths[index_in_smooths]
            n.setOffsetBySite(m, n.offset + positions[index_in_smooths])

if __name__ == '__main__':
    # print(smooth01(100))
    main()
