
import copy

from Harmony import Chord
class ChordProg:
    prog_delim = ','
    def __init__(self, chordString: str = "") -> None:
        self.chords: list = []
        self.parse_prog(chordString)
    
    def add(self, chord: Chord):
        self.chords.append(chord)

    def parse_prog(self, string: str):
        if len(string) > 0:
            chunks = string.split(ChordProg.prog_delim)
            for cstr in chunks:
                fstr = cstr.strip()
                print(f"chunk: {fstr}")
                chord = Chord(fstr)
                self.add(chord)

    def transpose(self, semitones: int):
        for chord in self.chords:
            chord.transpose(semitones)
    
    def arp(self):
        prog2 = copy.deepcopy(self)
        


    def __str__(self):
        cstr = ""
        for chord in self.chords:
            cstr += chord.get_chord_name() + ', '
        rstr = f"[Chord Prog]: {cstr}"
        return rstr




    