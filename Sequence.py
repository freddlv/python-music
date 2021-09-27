from mido import Message, MidiFile, MidiTrack, second2tick
from enum import IntEnum
import os.path
from os import path
from noteWriter import NoteWriter
from Note import Note, Pitch
from random import *
from utils import randomBiased


class Sequence:

    def __init__(self):
        self.duration: float = 0.0
        self.sequence: list = []
        self.restCount = 0

    def add(self, note: Note):
        self.sequence.append(note)
        self.duration += note.duration
        if note.rest:
            self.restCount += 1

    def extract(self, midiFile: str):
        if not path.exists(midiFile):
            raise "[Rhythm] file does not exist"

        mid = MidiFile(midiFile)
        tpq = mid.ticks_per_beat
        tempo = None
        for msg in mid:
            if 'tempo' in msg.dict():
                tempo = msg.dict()['tempo']

            if 'note' in msg.dict():
                type = msg.dict()['type']
                time = second2tick(msg.dict()['time'], tpq, tempo)
                midiPitch = msg.dict()['note']
                velocity = msg.dict()['velocity']
                durationTpb = time / (4 * tpq)
                if type == 'note_on':
                    if durationTpb > 0:
                        note = Note(duration=durationTpb, isRest=True, velocity=velocity, midiNumber=midiPitch)
                        self.add(note)
                elif type == 'note_off':
                    note = Note(False, durationTpb)
                    self.add(note)

    def writeSample(self, filepath: str):
        nw = NoteWriter(filepath)
        count = 0
        pitches = [Pitch.C, Pitch.E, Pitch.G]
        for note in self.sequence:
            note.pitchNum = Pitch.B
            note.octave = 5
            nw.writeNote(note)
            count += 1
        nw.save()

    def parse(self, strSequence: str):
        pass

    def generate_rhythm(self, minunit: float, duration: float, multipliers: list, multipliers_probs: list, is_rest_prob: float = 0.5):
        inv = int(pow(minunit, -1))
        total_divisions = int(duration) * inv
        currentPos = 0
        output = dict()
        output['durations'] = list()
        output['rest_bools'] = list()
        while currentPos < total_divisions:
            lengthChoices = multipliers
            choice = randomBiased(multipliers, multipliers_probs)
            isRest = True if randomBiased([0, 1], [is_rest_prob, 1.0-is_rest_prob]) == 0 else False
            if choice + currentPos > total_divisions:
                continue
            currentPos += choice
            n = Note(isRest=isRest, duration=float(choice) * minunit)
            self.add(n)
            

    def print(self):
        size = len(self.sequence)
        print(f'Total notes in rhythm: {size}')
        print(f'Rests: {self.restCount}, Tones: {size - self.restCount}')
        print(f'Total duration: {self.duration}')
        for note in self.sequence:
            print(note)

