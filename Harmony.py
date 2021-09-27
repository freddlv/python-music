

from Note import Pitch, Note
from enum import Enum
from utils import parse_num_frac, raiseError
from copy import copy, deepcopy


class ChordType:
    def __init__(self, name: str, symbol: str, semitones: tuple):
        self.semitones: tuple = semitones
        self.type: str = symbol
        self.name: str = name


cList = dict()
cList[''] = ChordType("Major Triad", "", (0, 4, 7))
cList['maj'] = ChordType("Major Triad", "", (0, 4, 7))
cList['maj6'] = ChordType("Major Sixth", "maj6", (0, 4, 7, 9))
cList['7'] = ChordType("Dominant Seventh", "7", (0, 4, 7, 10))
cList['maj7'] = ChordType("Major Seventh", "maj7", (0, 4, 7, 11))
cList['aug'] = ChordType("Augmented triad", "aug", (0, 4, 8))
cList['aug7'] = ChordType("Augmented seventh", "aug7", (0, 4, 8, 10))
cList['m'] = ChordType("Minor triad", "m", (0, 3, 7))
cList['m6'] = ChordType("Minor sixth", "m6", (0, 3, 7, 9))
cList['m7'] = ChordType("Minor seventh", "m7", (0, 3, 7, 10))
cList['m9'] = ChordType("Minor ninth", "m9", (0, 3, 7, 10, 14))
cList['m7b5'] = ChordType("Half Diminished Seventh", "m7b5", (0, 3, 6, 10))
cList['m(M7)'] = ChordType("Minor-major seventh", "m(M7)", (0, 3, 7, 11))
cList['dim'] = ChordType("Diminished triad", "dim", (0, 3, 6))
cList['dim7'] = ChordType("Diminished seventh", "dim7", (0, 3, 6, 9))
cList['sus4'] = ChordType("Suspended Fourth", "dim7", (0, 5, 7))
cList['sus2'] = ChordType("Suspended Second", "dim7", (0, 2, 7))
cList['5'] = ChordType("Fifth", "dim7", (0, 7))

pitchMap = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

pitchDict = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "D#": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "A#": 10,
    "B": 11
}


class Harmony:
    def __init__(self):
        self.durationSpan: float = -float("inf")
        self.notes: list = []

    def add(self, note: Note):
        self.notes.append(note)
        if note.duration > self.durationSpan:
            self.durationSpan = note.duration

    def transpose(self, semitones: int):
        for note in self.notes:
            note.transpose(semitones)
        print("called :(")


class Chord(Harmony):
    parameter_delim = '|'
    inverse_char = '*'

    def __init__(self, chordStr: str = ""):
        super().__init__()
        self.components = set()
        self.root = 0
        self.color = ""
        self.parse(chordStr)

    def transpose(self, semitones: int):
        self.root = (self.root + semitones) % 12
        nset = set()
        for k in self.components:
            nset.add((k + semitones) % 12)
        self.components = nset
        print(f"set is: {nset}")
        super().transpose(semitones)

    def parse(self, chordStr: str):
        if len(chordStr) > 0:
            try:
                values = Chord.parse_chord(chordStr)
                self.root = values["pitch"]
                self.color = values["color"]
                for c in values["components"]:
                    finalPitch = (c + values["pitch"]) % 12
                    note = Note(duration=values["duration"], isRest=False, pitch=finalPitch,
                                velocity=values["velocity"], octave=values["octave"])
                    self.add(note)
                    self.components.add(finalPitch)
                return True
            except:
                return False
        return False

    def get_chord_name(self):
        return f"{pitchMap[self.root]}{self.color}"

    def __str__(self):
        return f"[Chord] Name: {self.get_chord_name()} | Duration: {self.durationSpan} | Components {self.components}"

    @staticmethod
    def parse_chord(chordStr: str):
        duration = 1
        velocity = 127
        octave = 3
        size = len(chordStr)
        if size == 0:
            raiseError("parse_chord", IndexError,
                       "invalid string size to parse")
        if chordStr[0] not in pitchDict:
            raiseError("parse_chord", IndexError, "invalid chord specified")

        chunks = chordStr.split(Chord.parameter_delim)
        totalChunks = len(chunks)
        # chunk 0 contains pitch and sharpness

        chordPitch = pitchDict[chunks[0][0]]
        part1 = chunks[0][0]
        if len(chunks[0]) > 1:
            if chunks[0][1] == '#':
                chordPitch += 1
                part1 = chunks[0][1]
        chordPitch %= 12
        color = chunks[0].split(part1)
        if len(color) != 2:
            raiseError(chordStr)
        if color[1] not in cList:
            raiseError(chordStr)

        chordComponents = cList[color[1]].semitones

        # chunk 1 duration:
        if totalChunks >= 2:
            shouldInvert = False
            chunkLen = len(chunks[1])
            if chunks[1][chunkLen-1] == Chord.inverse_char:
                shouldInvert = True
                chunkLen -= 1
            duration = parse_num_frac(chunks[1][0:chunkLen])
            if duration == None:
                raiseError("parse_chord", ValueError,
                           "invalid duration specified")
            else:
                if duration < 0:
                    raiseError("parse_chord", ValueError,
                               "negative duration specified")

            if shouldInvert:
                duration = 1.0 / duration

        # octave:
        if totalChunks >= 3:
            octave = parse_num_frac(chunks[2])
            if octave == None:
                raiseError("parse_chord", ValueError,
                           "invalid octave specified")
            else:
                octave = int(octave)
                if octave > 10 or octave < -2:
                    raiseError("parse_chord", ValueError,
                               "invalid octave number specified")

        # velocity:
        if totalChunks >= 4:
            velocity = parse_num_frac(chunks[3])
            if velocity == None:
                raiseError("parse_chord", ValueError,
                           "invalid velocity specified")
            else:
                velocity = int(velocity)
                if velocity > 127 or velocity < 0:
                    raiseError("parse_chord", ValueError,
                               "invalid velocity number specified")

        output = dict()
        output["pitch"] = chordPitch
        output["components"] = chordComponents
        output["velocity"] = velocity
        output["octave"] = octave
        output["duration"] = duration
        output["color"] = color[1]
        return output
