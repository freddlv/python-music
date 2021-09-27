from mido import Message, MidiFile, MidiTrack
from mido.midifiles.meta import MetaMessage
from Note import Note
import mido
from Sequence import Sequence
from Harmony import Harmony, Chord
from ChordProg import ChordProg


class MusicWriter:
    def __init__(self, fpath: str, tempoBPM: int):
        self.midf = MidiFile(type=1)
        self.timeSigNum = 4
        self.timeSigDen = 4
        self.fpath = fpath
        self.categories = {
            "Piano": [1, 8, 0],
            "Chromatic Percussion": [9, 16, 0],
            "Organ": [17, 24, 0	],
            "Guitar": [25, 32, 0	],
            "Bass": [33, 40, 0	],
            "Strings": [41, 48, 0	],
            "Ensemble": [49, 56, 0	],
            "Brass": [57, 64, 0	],
            "Reed": [65, 72, 0	],
            "Pipe": [73, 80, 0	],
            "Synth Lead": [81, 88, 0	],
            "Synth Pad": [89, 96, 0	],
            "Synth Effects": [97, 104, 0	],
            "Ethnic": [105, 112, 0],
            "Percussive": [113, 120, 0],
            "Sound Effects": [121, 128, 0]
        }
        self.silenceAwaitTime = list()

        track0 = self.midf.add_track("Settings")
        track0.append(MetaMessage(
            'set_tempo', tempo=mido.bpm2tempo(tempoBPM), time=0))
        self.silenceAwaitTime.append(0)

    def addInstrument(self, instrumentType: str):
        if instrumentType not in self.categories:
            raise f"Instrument type: {instrumentType} specified doesn't exist"

        insCount = self.categories[instrumentType][2]
        min = self.categories[instrumentType][0]
        max = self.categories[instrumentType][1]
        diff = max - min
        if insCount >= diff:
            raise f"Max number of instruments of type {instrumentType} reached."

        track = self.midf.add_track(instrumentType)
        insNumber = insCount + min

        trackIdx = len(self.midf.tracks)-1
        track.append(Message('program_change', channel=trackIdx,
                     program=insNumber, time=0))
        self.silenceAwaitTime.append(0)
        self.categories[instrumentType][2] += 1
        return trackIdx

    def isValidTrackIndex(self, trackIdx: int):
        size = len(self.midf.tracks)
        if trackIdx < 0 or trackIdx >= size:
            return False
        return True

    def durationToTPQ(self, duration: float):
        tpq = self.midf.ticks_per_beat
        return int(self.timeSigNum * float(tpq) * duration)

    def writeNote(self, trackIdx: int, note: Note):
        if not self.isValidTrackIndex(trackIdx):
            raise f"[writeNote] Invalid track index: {trackIdx}"

        tpqNoteLength = self.durationToTPQ(note.duration)
        if note.is_rest():
            self.silenceAwaitTime[trackIdx] += tpqNoteLength
        else:
            noteNumber = note.get_midinum()
            self.midf.tracks[trackIdx].append(Message(
                'note_on',  channel=trackIdx, note=noteNumber, velocity=note.velocity, time=self.silenceAwaitTime[trackIdx]))
            self.midf.tracks[trackIdx].append(Message(
                'note_off', channel=trackIdx, note=noteNumber, velocity=note.velocity, time=tpqNoteLength))
            self.silenceAwaitTime[trackIdx] = 0

    def writeSequence(self, trackIdx: int, noteSequence: Sequence):
        for note in noteSequence.sequence:
            self.writeNote(trackIdx, note)

    def writeHarmony(self, trackIdx: int, harmony: Harmony):
        if not self.isValidTrackIndex(trackIdx):
            raise f"[writeHarmony] Invalid track index: {trackIdx}"

        size = len(harmony.notes)
        if not size:
            return 0
        self.midf.tracks[trackIdx].append(Message('note_on', note=harmony.notes[0].get_midinum(
        ), channel=trackIdx, velocity=harmony.notes[0].velocity, time=self.silenceAwaitTime[trackIdx]))
        for i in range(1, size):
            self.midf.tracks[trackIdx].append(Message('note_on', note=harmony.notes[i].get_midinum(), velocity=harmony.notes[i].velocity, channel=trackIdx,
                                                      time=0))

        harmony.notesSorted = sorted(harmony.notes, key=lambda x: x.duration)
        tpqElapsed = 0
        for i in range(0, size):
            tpqTime = self.durationToTPQ(
                harmony.notesSorted[i].duration) - tpqElapsed
            tpqElapsed += tpqTime
            self.midf.tracks[trackIdx].append(Message('note_off', note=harmony.notesSorted[i].get_midinum(), velocity=harmony.notes[i].velocity, channel=trackIdx,
                                                      time=tpqTime))

    def writeChordProg(self, trackIdx: int, chordProg: ChordProg):
        for chord in chordProg.chords:
            self.writeHarmony(trackIdx, chord)

    def save(self):
        self.midf.save(self.fpath)
        print("[debug]: file has been written.")

    class DrumTrack:
        def __init__(self) -> None:
            pass
