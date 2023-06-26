'''
parseYcacCsv.py -- parse YCAC files
'''
import csv
from ast import literal_eval
from dataclasses import dataclass
from typing import List, Dict, Optional

from music21.chord import Chord
from music21.note import Rest
from music21 import stream
from music21.common.numberTools import opFrac


@dataclass
class YcacSalamiSlice:
    offset: float
    chord: Optional[Chord]
    normal_form: List[int]
    pcs_normal_form: List[int]
    global_scale_degrees: List[int]
    highest_pitch: int
    lowest_pitch: int

    def validate_and_fix(self):
        if self.lowest_pitch < 12 and isinstance(self.chord, Chord):
            for n in list(self.chord):
                # difference between B,-1 and B-,1 is 23:
                if n.pitch.ps == self.lowest_pitch + 23:
                    self.chord.remove(n)
                    break
            else:
                print(f'Could not fix {self.chord} - {self.lowest_pitch}')

            new_bass = self.chord.bass()
            if new_bass is None:
                self.chord = None
                self.normal_form = []
                self.pcs_normal_form = []
                self.global_scale_degrees = []
                self.highest_pitch = 0
                self.lowest_pitch = 0
            else:
                self.lowest_pitch = new_bass.ps

            # normal_form, etc.


class YcacScoreFile:
    def __init__(self, name, composer, rows):
        self.name = name.replace('.mid', '')
        self.composer = composer
        self.rows_dicts: List[Dict] = rows
        self.slices: List[YcacSalamiSlice] = []
        self.stream: Optional[stream.Part] = None

    def __repr__(self):
        return f'<parseYcacCsv.YcacScoreFile {self.name!r} - {self.composer}>'

    def parse_rows(self):
        self.slices = []
        for rd in self.rows_dicts:
            self.slices.append(self.parse_one_row_dict(rd))

    def parse_one_row_dict(self, r: Dict):
        chord_str = r['Chord'][21:-1]
        if chord_str:
            chord_or_rest = Chord(chord_str.split())
        else:
            chord_or_rest = Rest()

        ss = YcacSalamiSlice(
            offset=opFrac(float(r['offset'])),
            chord=chord_or_rest,
            normal_form=literal_eval(r['NormalForm']),
            pcs_normal_form=literal_eval(r['PCsInNormalForm']),
            global_scale_degrees=literal_eval(r['GlobalScaleDegrees']),
            highest_pitch=int(r['HighestPitch']),
            lowest_pitch=int(r['LowestPitch'])
        )
        ss.validate_and_fix()
        return ss

    def rows_to_stream(self):
        s = stream.Part()
        last_chord = Rest()
        last_offset = 0.0
        for ss in self.slices:
            new_offset = ss.offset
            last_chord.duration.quarterLength = new_offset - last_offset
            s.coreAppend(ss.chord)
            last_chord = ss.chord
            last_offset = new_offset
        s.coreElementsChanged()
        self.stream = s
        return s


class YcacCsvFile:
    def __init__(self, fn: str):
        self.filename = fn
        self.rows: List[Dict] = []
        self.scoreFiles: List[YcacScoreFile] = []

    def parse(self):
        with open(self.filename) as csvFile:
            reader = csv.DictReader(csvFile)
            self.rows = list(reader)
        self.split()

    def split(self):
        currentRows = []
        currentName = ''
        currentComposer = ''

        scoreFiles = []
        for r in self.rows:
            if r['file'] != currentName:
                if currentRows:
                    currentScoreFile = YcacScoreFile(currentName, currentComposer, currentRows)
                    currentScoreFile.parse_rows()
                    scoreFiles.append(currentScoreFile)
                currentName = r['file']
                currentComposer = r['Composer']
                currentRows = []
            currentRows.append(r)

        if currentRows:
            currentScoreFile = YcacScoreFile(currentName, currentComposer, currentRows)
            currentScoreFile.parse_rows()
            scoreFiles.append(currentScoreFile)

        self.scoreFiles = scoreFiles
        return scoreFiles


if __name__ == '__main__':
    in_fn = '/Users/cuthbert/Downloads/YCAC-data-1/ISlices.csv'
    ycsv = YcacCsvFile(in_fn)
    ycsv.parse()
    ycsv.split()

