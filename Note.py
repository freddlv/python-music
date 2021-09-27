from enum import IntEnum



class Pitch(IntEnum):
    C = 0
    Db = 1
    D = 2
    Eb = 3
    E = 4
    F = 5
    Gb = 6
    G = 7
    Ab = 8
    A = 9
    Bb = 10
    B = 11

class Note:
    # Constants
    default_velocity: int = 127

    noteNames = {
        1: "Whole",
        1/2: "Half",
        1/4: "Quarter",
        1/8: "Eighth",
        1/16: "Sixteenth",
        1/32: "Thirty-second",
        1/64: "Sixty Fourth",
        1/(4*3): "Third of a Quarter",
        1/(4*6): "Sixth of a Quarter"
    }

    pitchMap = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    def __init__(self, duration, isRest: bool = False, pitch: int = Pitch.C, octave: int = 3, midiNumber: int = -1, velocity=default_velocity):
        self.rest: bool = isRest
        self.duration: float = duration
        self.midiNumber = 0
    
        if midiNumber == -1:
            self.midiNumber = Note.poctave_to_midinum(pitch, octave)
        else:
            self.midiNumber = midiNumber
        self.velocity = velocity

    def get_pitch_name(self):
        (pitch, octave) = Note.midinum_to_pitch_octave(self.midiNumber)
        return Note.pitchMap[pitch]
    
    def get_pitch(self):
        (pitch, octave) = Note.midinum_to_pitch_octave(self.midiNumber)
        return pitch
    
    def get_octave(self):
        (pitch, octave) = Note.midinum_to_pitch_octave(self.midiNumber)
        return octave
    
    def __str__(self):
        return f'[Note]: Type: {self.get_pitch_name()}{self.get_octave()} | Duration: {self.duration} | Rest: {self.is_rest()}'

    def transpose(self, semitones: int = 0, octaves: int = 0):
        self.midiNumber += semitones + 12*octaves
    
    def get_midinum(self):
        return self.midiNumber
        
    @staticmethod
    def poctave_to_midinum(pitch: int, octave: int) -> int:
        if pitch > 12 or pitch < 0:
            raise f"[error]: (poctave_to_midinum): invalid pitch number: {pitch}"
        
        if octave > 10 or octave < -2:
            raise f"[error]: (poctave_to_midinum): invalid octave number: {octave}"
        
        return 12*octave+pitch

    @staticmethod
    def midinum_to_pitch_octave(midiNum: int):
        return (midiNum % 12, midiNum // 12)

    def is_rest(self):
        return self.rest