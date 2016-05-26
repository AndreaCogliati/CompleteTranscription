#
# CompleteTranscription.py
#
# by Andrea Cogliati <andrea.cogliati@rochester.edu>
# University of Rochester
#

from music21 import *
import subprocess
import operator
import math
from os import system

class MidiBeat:
    def __init__(self, timestamp, level, division):
        self.timestamp = timestamp
        self.level = level
        self.division = division
        pass


class MidiNote:
    _PITCHCLASSES = ['f', 'c', 'g', 'd', 'a', 'e', 'b']
    _ACCIDENTALS = ['', '#', '##', '--', '-']
    _MIDINAMES = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']

    def __init__(self, onset, offset, midinote, stream):
        self.onset = onset
        self.offset = offset
        self.midinote = midinote
        self.stream = stream
        self.tpc = None
        self.beat = None
        self.duration = None
        self.octave = midinote // 12 - 1
        pass

    @property
    def note_name(self):
        if self.tpc != None:
            pitch_idx = self.tpc % 7 - 1
            accidentals = (self.tpc - 1) // 7
            pitchname = self._PITCHCLASSES[pitch_idx] + self._ACCIDENTALS[accidentals]
        else:
            pitch_idx = self.midinote % 12
            pitchname = self._MIDINAMES[pitch_idx]
        return pitchname + str(self.octave)

    @property
    def note_list_name(self):
        return 'Note\t{}\t{}\t{}'.format(self.onset, self.offset, self.midinote)

    def __str__(self):
        return self.note_name


class MidiTimeSignaure:
    def __init__(self, tactus_division, upper_division, phase):
        self.phase = phase
        self.initial_division = 1
        if (tactus_division, upper_division) == (2, 2):
            self.beats = 4
            self.duration = 4
            self.divisions = 16
            self.division_per_quarter = 4
        elif (tactus_division, upper_division) == (2, 3):
            self.beats = 3
            self.duration = 4
            self.divisions = 12
            self.division_per_quarter = 4
            if phase == 2:
                self.initial_division = 9
        elif (tactus_division, upper_division) == (3, 2):
            self.beats = 6
            self.duration = 8
            self.divisions = 12
            self.division_per_quarter = 4
            if phase == 1:
                self.initial_division = 7
        elif (tactus_division, upper_division) == (3, 3):
            self.beats = 9
            self.duration = 8
            self.divisions = 18
            self.division_per_quarter = 4


    def __str__(self):
        return '{0}/{1}'.format(self.beats, self.duration)


class MidiScore:
    def __init__(self):
        self.key = None
        self.time_signature = None
        self.beats = None
        self.notes = None
        self.num_streams = None

    def set_key(self, key_string):
        key_string = key_string.replace('b','-')
        if key_string[-1] == 'm':
            key_string = key_string[0:-1].lower()
        self.key = key_string

    def set_meter(self, meter_output):
        meter_list = strlst_to_intlst(meter_output.split())
        tactus_division, upper_division, phase = meter_list[1], meter_list[2], meter_list[4]
        self.time_signature = MidiTimeSignaure(tactus_division, upper_division, phase)

    def parse_quantized_notes_output(self, quantized_note_events_output):
        self.beats = []
        division = self.time_signature.initial_division
        self.notes = []
        self.num_streams = 0
        for line in quantized_note_events_output.split('\n'):
            tokens = line.split()
            if tokens != []:
                if tokens[0] == 'Beat':
                    self.beats.append(MidiBeat(int(tokens[1]), int(tokens[2]), division))
                    division += 1
                elif tokens[0] == 'Note':
                    stream = int(tokens[4])
                    self.notes.append(MidiNote(int(tokens[1]), int(tokens[2]), int(tokens[3]), stream))
                    if stream > self.num_streams:
                        self.num_streams = stream

    def find_note(self, onset, offset, midinote):
        for idx in range(len(self.notes)):
            if self.notes[idx].onset == onset and self.notes[idx].offset == offset and self.notes[idx].midinote == midinote:
                return idx
        return None

    def parse_harmony_output(self, harmony_output):
        for line in harmony_output.split('\n'):
            tokens = line.split()
            if  tokens != []:
                if tokens[0] == 'TPCNote':
                    idx = self.find_note(int(tokens[1]), int(tokens[2]), int(tokens[3]))
                    if idx != None:
                        tpc = int(tokens[4])
                        self.notes[idx].tpc = tpc

    def find_notes_beat(self):
        for idx in range(len(self.notes)):
            self.notes[idx].beat = self.find_beat(self.notes[idx].onset)
            self.notes[idx].duration = self.find_beat(self.notes[idx].offset).division - self.notes[idx].beat.division

    def find_beat(self, onset):
        min_idx = 0
        for idx in range(1,len(self.beats)):
            if abs(self.beats[idx].timestamp - onset) <= abs(self.beats[min_idx].timestamp - onset):
                min_idx = idx
            else:
                break
        return self.beats[min_idx]

    def get_stream(self, key):
        return [note for note in self.notes if note.stream == key]


# Helper functions

def strlst_to_intlst(strlst):
    intlst = []
    for num in strlst:
        intlst.append(int(num))
    return intlst


def find_empty_voices(a_measure):
    empty_voices = []
    hasNotes = False
    for a_voice in a_measure.voices:
        if a_voice.hasElementOfClass(note.Note):
            hasNotes = True
        else:
            empty_voices.append(a_voice)
    if hasNotes:
        return empty_voices
    else:
        return empty_voices[1:]


def remove_extra_rests_from_score(the_score):
    # Remove extra rests
    emptyVoices = []
    for el in the_score.recurse():
        if isinstance(el, stream.Measure):
            emptyVoices.extend(find_empty_voices(el))

    the_score.remove(emptyVoices, recurse=True)

    return the_score


def fix_empty_voice(a_voice):
    a_duration = a_voice.elements[0].duration
    a_voice.remove(a_voice.elements[0])
    a_spacer = note.SpacerRest()
    a_spacer.duration = a_duration
    a_voice.insert(0, a_spacer)


def isStandardKey(a_key):
    for sharps in range(-7,7):
        ks = key.KeySignature(sharps)
        ks.mode = 'major'
        maj_ton = ks.getScale().tonic
        ks.mode = 'minor'
        min_ton = ks.getScale().tonic
        maj_key = key.Key(maj_ton, 'major')
        min_key = key.Key(min_ton, 'minor')
        if a_key == maj_key or a_key == min_key:
            return True
    return False


def pad_part(a_part, a_time_signature):
    if (a_part.duration.quarterLength * (a_time_signature.duration // 4)) % a_time_signature.beats:
        a_rest = note.Rest()
        a_rest.quarterLength = (a_time_signature.beats - (a_part.duration.quarterLength * (a_time_signature.duration // 4) % a_time_signature.beats)) / (a_time_signature.duration // 4)
        a_part.insert(a_part.duration.quarterLength, a_rest)


def setup():
    pass


def complete_transcription(midifile):
    setup()

    ## Process MIDI file according to the cognitive model
    print('Convert MIDI into note list')
    note_list = subprocess.check_output(['mftext', midifile])

    # fix overlapping notes
    print('Fix overlapping notes')
    new_note_list = []
    for line in note_list.decode().split('\n'):
        tokens = line.split()
        if tokens != []:
            if tokens[0] == 'Note':
                new_note_list.append(MidiNote(int(tokens[1]), int(tokens[2]), int(tokens[3]), 0))
    new_note_list.sort(key=operator.attrgetter('onset'))
    OVERLAP_THR = .30
    for i in range(len(new_note_list)):
        for j in range(i+1,len(new_note_list)):
            if new_note_list[j].onset >= new_note_list[i].offset:
                break
            len_note_i = new_note_list[i].offset - new_note_list[i].onset
            len_note_j = new_note_list[j].offset - new_note_list[j].onset
            overlap_start = max(new_note_list[i].onset, new_note_list[j].onset)
            overlap_end = min(new_note_list[i].offset, new_note_list[j].offset)
            overlap = overlap_end - overlap_start
            overlap_note_i = overlap/len_note_i
            overlap_note_j = overlap/len_note_j
            if overlap_note_i + overlap_note_j < OVERLAP_THR:
                new_note_list[i].offset = new_note_list[j].onset
    note_list = '\n'.join([note.note_list_name for note in new_note_list]).encode()
    print('Detect meter')
    polyph_proc = subprocess.Popen(['polyph', '-v', '-1'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    meter_output = polyph_proc.communicate(input=note_list)[0]
    # polyph_proc = subprocess.Popen(['polyph', '-v', '-2'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    # chords_output = polyph_proc.communicate(input=note_list)[0]
    print('Detect beats and quantized notes')
    polyph_proc = subprocess.Popen(['polyph', '-v', '-4'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    quantized_note_events_output = polyph_proc.communicate(input=note_list)[0]
    print('Determine note spelling')
    harmony_proc = subprocess.Popen(['harmony', '-p', 'harmony_params.txt'], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE)
    harmony_output = harmony_proc.communicate(input=quantized_note_events_output)[0]
    print('Estimate key')
    key_proc = subprocess.Popen('key', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    key_output = key_proc.communicate(input=harmony_output)[0]

    ## Create intermediate representation
    midi_score = MidiScore()

    # Parsing the key
    midi_score.set_key(key_output.decode().split()[0])
    print('The key is', midi_score.key)

    # Parsing the meter
    midi_score.set_meter(meter_output.decode())
    print('The time signature is', midi_score.time_signature)

    # Parsing quantized notes output
    midi_score.parse_quantized_notes_output(quantized_note_events_output.decode())

    # Parsing harmony output
    midi_score.parse_harmony_output(harmony_output.decode())

    # Find note beats
    midi_score.find_notes_beat()

    ## Create music21 score
    print('Creating score')
    trebleStaff = stream.PartStaff()
    trebleStaff.insert(0, meter.TimeSignature(str(midi_score.time_signature)))
    trebleStaff.insert(0, key.Key(str(midi_score.key)))
    trebleStaff.insert(0, clef.TrebleClef())

    bassStaff = stream.PartStaff()
    bassStaff.insert(0, meter.TimeSignature(str(midi_score.time_signature)))
    bassStaff.insert(0, key.Key(str(midi_score.key)))
    bassStaff.insert(0, clef.BassClef())

    # Create streams
    streams = stream.Score()
    for idx in range(1, midi_score.num_streams+1):
        new_stream = stream.Stream()
        note_stream = midi_score.get_stream(idx)
        stream_offset = (note_stream[0].beat.division - 1) / midi_score.time_signature.division_per_quarter
        for idx in range(len(note_stream)):
            midinote = note_stream[idx]
            new_note = note.Note(str(midinote))
            if idx != len(note_stream) - 1:
                new_note.quarterLength = (note_stream[idx+1].beat.division - midinote.beat.division) / midi_score.time_signature.division_per_quarter
            else:
                new_note.quarterLength = midinote.duration / midi_score.time_signature.division_per_quarter
            new_stream.insert((midinote.beat.division - 1) / midi_score.time_signature.division_per_quarter - stream_offset, new_note)
        streams.insert(stream_offset, new_stream)

    # Assign streams to correct staff
    for a_stream in streams.elements:
        if isinstance(a_stream.bestClef(), clef.TrebleClef):
            trebleStaff.insert(a_stream.offset, a_stream)
        else:
            bassStaff.insert(a_stream.offset, a_stream)

    # Make notation
    trebleStaff = trebleStaff.flat
    bassStaff = bassStaff.flat

    # Fix parts with different lengths
    treble_staff_bars = math.ceil((trebleStaff.duration.quarterLength * (midi_score.time_signature.duration // 4)) / midi_score.time_signature.beats)
    bass_staff_bars = math.ceil((bassStaff.duration.quarterLength * (midi_score.time_signature.duration // 4)) / midi_score.time_signature.beats)
    if treble_staff_bars > bass_staff_bars:
        a_rest = note.Rest()
        a_rest.quarterLength = midi_score.time_signature.beats / (midi_score.time_signature.duration // 4)
        bassStaff.insert((treble_staff_bars - 1) * midi_score.time_signature.beats / (midi_score.time_signature.duration // 4), a_rest)
    elif bass_staff_bars > treble_staff_bars:
        a_rest = note.Rest()
        a_rest.quarterLength = midi_score.time_signature.beats / (midi_score.time_signature.duration // 4)
        trebleStaff.insert((bass_staff_bars - 1) * midi_score.time_signature.beats / (midi_score.time_signature.duration // 4), a_rest)

    # Pad last measure of parts, if necessary
    pad_part(trebleStaff, midi_score.time_signature)
    pad_part(bassStaff, midi_score.time_signature)

    trebleStaff.makeVoices(inPlace=True)
    trebleStaff.makeRests(fillGaps=True)
    bassStaff.makeVoices(inPlace=True)
    bassStaff.makeRests(fillGaps=True)

    the_score = stream.Score()
    the_score.insert(0, trebleStaff)
    the_score.insert(0, bassStaff)

    the_score = the_score.makeNotation()

    # Fix missing key signature
    for part in range(2):
        if not the_score[part][0].hasElementOfClass(key.Key):
            the_score[part][0].insert(0, key.Key(str(midi_score.key)))

    # Fix non-standard key signatures
    if not isStandardKey(key.Key(str(midi_score.key))):
        print('Fixing key signature')
        for el in the_score.recurse():
            if isinstance(el, key.Key):
                el.tonic = el.pitchAndMode[0].getEnharmonic()
                el.sharps = key.Key(el.pitchAndMode[0].getEnharmonic(), el.mode).sharps
            elif isinstance(el, note.Note):
                el.pitch = el.pitch.getEnharmonic()

    # Remove extra rests
    print('Removing extra rests')
    empty_voices = []
    for el in the_score.recurse():
        if isinstance(el, stream.Measure):
            empty_voices.extend(find_empty_voices(el))

    for a_voice in empty_voices:
        fix_empty_voice(a_voice)

    return the_score


def convert_part_to_lilypond(a_part):
    lilypond_part = ''
    lpc = lily.translate.LilypondConverter()

    lilypond_part += lpc.lySequentialMusicFromStream(a_part.getKeySignatures()).stringOutput()
    lilypond_part += lpc.lySequentialMusicFromStream(a_part.getTimeSignatures()).stringOutput()

    all_voices = stream.Stream()
    voice_less = not a_part[0].hasVoices()
    if voice_less:
        voiceLess = True
        new_voice = stream.Voice()
        new_voice.id = 0
        all_voices.insert(0, new_voice)

    for el in a_part.recurse():
        if isinstance(el, note.GeneralNote):
            if voice_less:
                voice_in_score = all_voices.getElementById(0)
                measure_offset = el.activeSite.offset
            else:
                voice_in_score = all_voices.getElementById(el.activeSite.id)
                measure_offset = el.activeSite.activeSite.offset
            voice_in_score.insert(measure_offset + el.offset, el, setActiveSite=False)
        elif isinstance(el, stream.Voice) and not all_voices.getElementById(el.id):
            new_voice = stream.Voice()
            new_voice.id = el.id
            all_voices.insert(0, new_voice)

    voice_num = 0
    lilypond_part += ' << '
    for a_voice in all_voices:
        if voice_num > 0:
            lilypond_part += ' \\\\ '
        lilypond_part += ' { '
        for a_note in a_voice:
            if a_note.quarterLength == 0:
                continue
            if len(a_note.duration.components) == 1:
                lilypond_note = lpc.lySimpleMusicFromNoteOrRest(a_note).stringOutput().translate(str.maketrans('', '', '[]'))
            else:
                lilypond_note = ''
                is_first = True
                for a_duration in a_note.duration.components:
                    if is_first or isinstance(a_note, note.Rest) or isinstance(a_note, note.SpacerRest):
                        is_first = False
                    else:
                        lilypond_note += ' ~ '
                    if isinstance(a_note,note.Note):
                        simple_note = note.Note()
                        simple_note.pitch = a_note.pitch
                        # print(a_note,simple_note)
                    elif isinstance(a_note,note.Rest):
                        simple_note = note.Rest()
                    elif isinstance(a_note,note.SpeacerRest):
                        simple_note = note.SpeacerRest()
                    else:
                        print('I don''t know what {} is'.format(el))
                    simple_note.quarterLength = a_duration.quarterLength
                    lilypond_note += lpc.lySimpleMusicFromNoteOrRest(simple_note).stringOutput().translate(str.maketrans('', '', '[]'))
            lilypond_part += lilypond_note
        lilypond_part += ' } '
        voice_num += 1

    lilypond_part += ' >> \\bar "|." '

    return lilypond_part

def convert_music21_score_to_lilypond(the_score):
    lilypond_version = '\\version "2.18.2"'
    lilypond_header = '\\header { tagline = "" }'
    lilypond_score_footer = """\\score { \\new PianoStaff
    <<
    % \\set PianoStaff.instrumentName = #"Piano  "
    \\new Staff = "upper" \\upper
    \\new Staff = "lower" \\lower >> }"""

    lilypond_u = convert_part_to_lilypond(the_score.parts[0])
    lilypond_l = convert_part_to_lilypond(the_score.parts[1])

    lilypond_part_str = '{} = {{ \clef {} {} }}'
    lilypond_upper = lilypond_part_str.format('upper', 'treble', lilypond_u)
    lilypond_lower = lilypond_part_str.format('lower', 'bass', lilypond_l)

    lilypond_score = lilypond_version + '\n' + lilypond_header + '\n' + lilypond_upper + '\n' + lilypond_lower + '\n' + lilypond_score_footer

    return lilypond_score


def main():
    midifile = 'minuet.mid'
    the_score = complete_transcription(midifile)

    lilypond_score = convert_music21_score_to_lilypond(the_score)
    open('minuet.ly','w').write(lilypond_score)
    system('lilypond -o minuet minuet.ly')


if __name__ == '__main__':
    main()
