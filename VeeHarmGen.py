#!/usr/bin/env python
# -*- coding: utf-8 -*-
# VeeHarmGen.py
#
# Given an input compressed musicxml file (.mxl) with a melody stave:
# if in demo mode it calculates chord symbols for different harmonic rhythms and chord types and saves the result.
# If not in demo mode:
#       if the input has no chord symbols then
#           it calculates chord symbols for different harmonic rhythms and
#           saves the result.
#       else
#           for each style:
#               for each placeholder chords it calculates a new chord in the current style and
#               saves the result.
#
# free and open-source software, Paul Wardley Davies, see license.txt

# standard libraries
import argparse
import ast
import bisect
import copy
import datetime
import math
import music21
import numpy
import operator
import os
from pathlib import Path
import re
import sys
import VeeHarmGen_utilities

from collections import Counter
from enum import Enum
from fractions import Fraction
from itertools import islice
from music21 import *
from music21 import stream, note, harmony
from music21.harmony import ChordSymbol, NoChord
from VeeHarmGen_utilities import *

# VEEHARMGEN_VERSION 
__version__ = "3.0.0"

# on ubuntu 20.04 default python 3.8.10 (without removesuffix)

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

class Chord_Output(Enum):
    ON_KEY_MOST = 100
    ON_KEY_LEAST = 101
    ON_KEY_FIRST = 102
    ON_KEY_LAST = 103
    PEDAL = 111
    NEXT_INTERVAL_SECOND_OR_THIRD = 123
    NEXT_INTERVAL_FOURTH_OR_FIFTH = 145
    NEXT_INTERVAL_SIXTH_OR_SEVENTH = 167
    DESCENDING_BASS_TETRA = 174
    DESCENDING_CHROMATIC_BASS_TETRA = 175
    DESCENDING_BASS = 176
    DESCENDING_CHROMATIC_BASS = 177
    ASCENDING_BASS_TETRA_1 = 181
    ASCENDING_BASS_TETRA_2 = 182
    ASCENDING_BASS_TETRA_3 = 183
    SUSPENDED2 = 200
    ADD2 = 202
    MINOR = 300
    MAJOR = 301
    SUSPENDED4 = 400
    ADD4 = 404
    FIFTH = 500
    SIXTH = 600
    ADDSIXTH = 606
    SEVENTH = 700
    NINTH = 900
    ELEVENTH = 911
    THIRTEENTH = 913

class Harmonic_Rhythm(Enum):
    BEAT1 = 0
    BEAT2 = 1
    BAR1 = 2
    BAR2 = 3
    BAR4 = 4

class Harmonic_Rhythm(Enum):
    BEAT1 = 0
    BEAT2 = 1
    BAR1 = 2
    BAR2 = 3
    BAR4 = 4

def get_chord(initial_offset, offset_chord, prev_sho_cho):
    """
    given offset and offset_chord dictionary, return short chord (e.g. Am or C) at offset
    :param initial_offset: e.g. 3.0
    :param chords_offset : e.g. {'F': 0.0, 'F': 1.0, 'G': 2.0, 'E': 3.0, 'F': 4.0, 'G': 5.0, 'A': 6.0} etc
    :param: prev_sho_cho: previous short chord
    :return: short_chord e.g. 'E'
    """

    # harmonic rhythm = 2nd key - 1st key
    harmonic_rhythm = list(offset_chord.keys())[1] - next(iter(offset_chord))

    offset = initial_offset
    negative_offset = False
    while True:
        val = offset_chord.get(offset)
        if val != None:
            break
        offset = offset - 0.125
        if offset < 0.0:
            negative_offset = True
            break

    if not negative_offset:
        try:
            short_chord = offset_chord[offset]
        except KeyError:
            print('exit: KeyError. initial_offset, offset, offset_chord', initial_offset, offset, offset_chord)
            sys.exit()
    else:
        short_chord = prev_sho_cho

    return short_chord

def get_chord_from_pitch_to_chord_by_rank(number, v):
    """
    given a pitch_to_chord v and a rank number return the short chord (e.g. Am or C) for the rank number
    :param number 
    :param v: a pitch_to_chord : e.g. {'1000 0000 0000': {'C': 2, 'Am7': 1, 'Am': 1}, '0010 0000 0000': {'F': 2, 'G': 1}, '1010 0000 0001': {'G': 1}, '0000 1000 0000': {'C': 1, 'Am': 1}, '0000 1100 0000': {'F': 1}, '1000 0000 0001': {'G': 1}, '1010 1100 0000': {'C': 1}, '0010 1100 0000': {'G': 1}, '1010 1101 0000': {'C': 1}, '0000 0100 0100': {'F': 1}, '0010 1000 0000': {'G': 1}}
    :return: short_chord e.g. 'E' 
    """
    
    # print('get_chord_from_pitch_to_chord_by_rank(number, v)', number, v) 
    # print('type(v), v', type(v), v)
    # sort
    sorted_v = dict(sorted(v.items(), key=operator.itemgetter(1), reverse=True))

    # get count of entries in the dictionary
    sorted_v_len = len(sorted_v)

    # convert rank to iter_num
    iter_num = sorted_v_len - math.ceil((number * (sorted_v_len / 100.0)))

    if (iter_num < 0) or (iter_num > sorted_v_len): iter_num = 0    # bug if sorted_v_len = 7 then iter_num = -1

    # access the nth element of dict sorted_v where n is iter_num
    # but check if a subsequent element with the same frequency has a shorter length use that
    # i.e. use the simplest chord with the same frequency
    iter_num_1 = 0
    for ch1, f1 in sorted_v.items():
        if iter_num_1 == iter_num:
            ch = ch1
            f = f1
        if iter_num_1 > iter_num:
            if f1 == f and (len(ch1) < len(ch)):
                ch = ch1
        iter_num_1 = iter_num_1 + 1

    print('number, sorted_v_len, iter_num, ch, sorted_v', number, sorted_v_len, iter_num, ch, sorted_v)
    # print('type(ch), ch, type(f), f', type(ch), ch, type(f), f )
    # input('Press Enter to continue...')
    return ch 


def get_chord_from_pitch_to_chord_by_nth_outcome(number, v):
    """
    given a pitch_to_chord v and a nth_outcome number return the short chord (e.g. Am or C) for the nth_outcome number
    :param number 
    :param v: a pitch_to_chord : e.g. {'1000 0000 0000': {'C': 2, 'Am7': 1, 'Am': 1}, '0010 0000 0000': {'F': 2, 'G': 1}, '1010 0000 0001': {'G': 1}, '0000 1000 0000': {'C': 1, 'Am': 1}, '0000 1100 0000': {'F': 1}, '1000 0000 0001': {'G': 1}, '1010 1100 0000': {'C': 1}, '0010 1100 0000': {'G': 1}, '1010 1101 0000': {'C': 1}, '0000 0100 0100': {'F': 1}, '0010 1000 0000': {'G': 1}}
    :return: short_chord e.g. 'E' 
    """
    
    print('get_chord_from_pitch_to_chord_by_nth_outcome(number, v)', number, v) 
    # print('type(v), v', type(v), v)
    # sort
    sorted_v = dict(sorted(v.items(), key=operator.itemgetter(1), reverse=True))

    # get count of entries in the dictionary
    sorted_v_len = len(sorted_v)
    print('sorted_v_len', sorted_v_len)

    # given the the nth_outcome number, determine the iteration number for the dict sorted_v
    if (number <= 0): iter_num = 0 
    elif (sorted_v_len == 1): iter_num = 0
    elif (number < sorted_v_len): iter_num = number
    # elif (number >= sorted_v_len): iter_num = sorted_v_len % number
    elif (number >= sorted_v_len): iter_num = number % sorted_v_len

    
    # access the nth element of dict sorted_v where n is iter_num
    print('sorted_v', sorted_v)
    print('iter_num, iter_num + 1', iter_num, iter_num + 1)
    print('islice(iter(sorted_v), iter_num, iter_num + 1)',islice(iter(sorted_v), iter_num, iter_num + 1))
    # print('next(islice(iter(sorted_v), iter_num, iter_num + 1))', next(islice(iter(sorted_v), iter_num, iter_num + 1)))
    ch = next(islice(iter(sorted_v), iter_num, iter_num + 1))
    print('type(ch), ch', type(ch), ch )
 
    print('number, sorted_v_len, iter_num, ch, sorted_v', number, sorted_v_len, iter_num, ch, sorted_v)
    # input('Press Enter to continue...')
    # print('type(ch), ch, type(f), f', type(ch), ch, type(f), f )
    # input('Press Enter to continue...')
    
    # return the chord by nth_outcome
    return ch 
    
def get_chord_for_pitch_class(pitch_class, pitch_to_chord, output_filename, chord_choice, number):
    """
    given pitch_class and pitch_to_chord dictionary, return short chord (e.g. Am or C) at offset
    :param pitch_class: e.g. 1000 0000 0000
    :param pitch_to_chord : e.g. {'1000 0000 0000': {'C': 2, 'Am7': 1, 'Am': 1}, '0010 0000 0000': {'F': 2, 'G': 1}, '1010 0000 0001': {'G': 1}, '0000 1000 0000': {'C': 1, 'Am': 1}, '0000 1100 0000': {'F': 1}, '1000 0000 0001': {'G': 1}, '1010 1100 0000': {'C': 1}, '0010 1100 0000': {'G': 1}, '1010 1101 0000': {'C': 1}, '0000 0100 0100': {'F': 1}, '0010 1000 0000': {'G': 1}}
    :param output_filename (used in printed warnings)
    :param chord_choice
    :param number 
    :return: short_chord e.g. 'E'
    if no chord pitch_class then short_chord = 'NC'
    else
        using pitch_class get value from pitch_to_chord
        get first chord from value (TBD add pre-determined slice parameter)
        short_chord = validated chord symbol
        if invalid short_chord = 'NC'
    return short_chord
    """

    short_chord = 'C'
    # if no chord pitch_class then short_chord = 'NC
    if pitch_class == NO_CHORD_DISPLAY_PITCH_CLASSES:
        short_chord = 'NC'
    else:
        #     using pitch_class get value from pitch_to_chord
        try:
            v = pitch_to_chord[pitch_class]
        except KeyError as error:
            print('WARNING Invalid pitch_class so get_nearest_chord_from_pitch_to_chord', pitch_class, 'in', output_filename)
            v = get_nearest_chord_for_pitch_class(pitch_class, pitch_to_chord, output_filename)
        if v != None:
            if chord_choice is Chord_Choice.RANK:
                print('chord_choice is rank')
                ch = get_chord_from_pitch_to_chord_by_rank(number, v)
                print('rank ch is', ch)  
                # input('Press Enter to continue...')
            if chord_choice is Chord_Choice.NTH_OUTCOME:
                print('chord_choice is nth_outcome')
                ch = get_chord_from_pitch_to_chord_by_nth_outcome(number, v)
                print('nth_outcome ch is', ch)  
                # input('Press Enter to continue...')
                
            short_chord = ch    
            try:
                test_chord = harmony.ChordSymbol(ch)
            except music21.Music21Exception:
                print('WARNING Invalid chord symbol', ch)
                short_chord = 'NC'
            # input('Press Enter to continue...')

    return short_chord

def get_first_note(a_stream):
    """
    :param a_stream:
    :return: the first note in the stream or None
    """
    first_note = None

    for n in a_stream.flatten():
        if type(n) == music21.note.Note:
            if first_note == None:
                first_note = n

    return first_note

def get_last_note(a_stream):
    """
    :param a_stream:
    :return: the last note in the stream or None
    """
    last_note = None

    for n in a_stream.flatten():
        if type(n) == music21.note.Note:
            last_note = n

    return last_note

def stream_has_a_note(a_stream):
    """
    return True if stream has a note
    :param a_stream:
    :return: True if stream has a note
    """
    stream_has_note = False

    for n in a_stream.flatten():
        if type(n) == music21.note.Note:
            stream_has_note = True

    return stream_has_note

def has_chord_symbols(a_stream):
    """
    return True if stream has a chord_symbol
    :param a_stream:
    :return: True if stream has a chord_symbol
    """
    stream_has_chord_symbol = False

    stream_copy = copy.deepcopy(a_stream)

    for n in stream_copy.flatten():
        if type(n) == music21.harmony.ChordSymbol:
            stream_has_chord_symbol = True

    if stream_has_chord_symbol:
            print(a_stream, 'has chord symbols')
    else:
            print(a_stream, 'does NOT have chord symbols')

    return stream_has_chord_symbol

class SongSectionValues:
    """
    A class that stores SongSectionValues
    such as duration types and tone range in a section of a song.
    Methods include __init__ and update with a note
    """
    # class variables shared by all instances

    analyze_choice = 'Krumhansl' # my default as least errors on GSTQ 1 bar (Music21 default is Aarden same as key)

    current_song_length_offset = 0.0

    # lists of the key finder offset chord dictionaries for each harmonic rhythm
    key_finder_offset_chords_1_beat = []
    key_finder_offset_chords_2_beat = []
    key_finder_offset_chords_1_bar = []
    key_finder_offset_chords_2_bar = []
    key_finder_offset_chords_4_bar = []

    last_bass = 'C'
    letter_current = 'A'

    number_of_song_sections = 0

    # offset_section = {}  # dictionary to hold offset to section mapping e.g. {0.0: 'intro 1'}
    offsets = None
    OUTPUT_PATH = 'output' + os.sep

    section_letter = {} # dictionary to hold section to letter mapping e.g. {'verse': 'A', 'chorus': 'B'}

    song_chords_1_beat = ''
    song_chords_2_beat = ''
    song_chords_1_bar = ''
    song_chords_2_bar = ''
    song_chords_4_bar = ''

    song_key = None

    # offset_chord Dictionaries
    song_offset_chord_1_beat = '{'
    song_offset_chord_2_beat = '{'
    song_offset_chord_1_bar = '{'
    song_offset_chord_2_bar = '{'
    song_offset_chord_4_bar = '{'
    song_offset_placeholder_chords = '{'

    songTimeSig = None

    structure_by_name_long = ''
    structure_by_name = ''
    structure_by_name_initial = ''
    structure_by_letter  = ''

    the_instrument = music21.instrument.Instrument(instrumentName='Piano')
    TIME_SIG_WANTED = '3/4'
    transpose = None

    def get_first_note(self):
        """
        :return: last first in stream1
        """
        return self.stream1[0]

    def get_last_note(self):
        """
        :return: last note in stream1
        """
        return self.stream1[-1]


    def get_stream(self, start_note_offset, end_note_offset):
        """
        gets a subset of stream1 (the whole song)
        :param start_note_offset: song offsets >= this included in stream
        :param end_note_offset: song offsets < this included in stream
        :return: stream
        """
        sub_stream = stream.Stream()
        for n in self.stream1.flatten():
            if type(n) == music21.note.Note or type(n) == music21.note.Rest:
                if (n.offset >= start_note_offset) and (n.offset < end_note_offset):
                    sub_stream.append(n)

        return sub_stream

    def increment_sections(self):
        SongSectionValues.number_of_song_sections += 1

    # class instantiation automatically invokes __init__
    def __init__(self, song_key, song_stream):
        """
        takes song_key
        and initialises section data
        """

        print('SongSectionValues.__init__(self, song_key, song_stream)',  song_key, song_stream)
        # update class variables
        SongSectionValues.song_key = song_key
        SongSectionValues.song_stream = song_stream

        # set instance variable unique to each instance
        self.dur_prev = 0
        self.note_prev = None

        self.DURATION_SET = []
        self.DUR_PREV_DIFF = 0
        self.DUR_RATIONAL = True
        self.DUR_TUPLET = False
        self.DUR_LEAST = 99.0
        self.DUR_LONGEST = 0.01
        self.REST_NOTE_LINE_OFFSET = None

        # self.stream_raw = stream.Stream()   # original stream NR see .song_stream
        self.stream1 = stream.Stream()      # only notes and rests not chord symbols
        self.TONES_ON_KEY = True
        self.TONE_PREV_INTERVAL = 0
        self.TONE_RANGE_BOTTOM = 'B9'
        self.TONE_RANGE_TOP = 'C0'
        self.TONE_SCALE_SET = []

        # when looping over several analysis classes need to initialise more variables

        SongSectionValues.current_song_length_offset = 0.0

        SongSectionValues.letter_current = 'A'

        SongSectionValues.number_of_song_sections = 0

        SongSectionValues.offset_section = {}  # dictionary to hold offset to section mapping e.g. {0.0: 'intro 1'}

        SongSectionValues.OUTPUT_PATH = 'output' + os.sep

        SongSectionValues.section_letter = {}  # dictionary to hold section to letter mapping e.g. {'verse': 'A', 'chorus': 'B'}

        SongSectionValues.song_chords_1_beat = ''
        SongSectionValues.song_chords_2_beat = ''
        SongSectionValues.song_chords_1_bar = ''
        SongSectionValues.song_chords_2_bar = ''
        SongSectionValues.song_chords_4_bar = ''

        # offset_chord Dictionaries
        SongSectionValues.song_offset_chord_1_beat = '{'
        SongSectionValues.song_offset_chord_2_beat = '{'
        SongSectionValues.song_offset_chord_1_bar = '{'
        SongSectionValues.song_offset_chord_2_bar = '{'
        SongSectionValues.song_offset_chord_4_bar = '{'
        SongSectionValues.song_offset_placeholder_chords = '{'

        # SongSectionValues.songTimeSig = None

        SongSectionValues.structure_by_name_long = ''
        SongSectionValues.structure_by_name = ''
        SongSectionValues.structure_by_name_initial = ''
        SongSectionValues.structure_by_letter = ''

        SongSectionValues.the_instrument = music21.instrument.Instrument(instrumentName='Piano')
        # SongSectionValues.TIME_SIG_WANTED = '3/4'

        SongSectionValues.offset_section = get_offset_section(song_stream)

        print('# -----------------------------------------------------------------------')

    def get_analyze_choice(self):
        """
        get analyze_choice from class variable
        """
        # return analyze_choice class variable
        return SongSectionValues.analyze_choice

    def set_analyze_choice(self, analyze_choice):
        """
        given analyze_choice update class variable
        """
        # update class variable
        SongSectionValues.analyze_choice = analyze_choice

    def set_instrument(self, instrument):
        """
        given instrument update class variable
        """
        # update class variable
        SongSectionValues.the_instrument = music21.instrument.Instrument(instrumentName=instrument)

    def set_time_sig(self, songTimeSig):
        """
        given time signature update class variable
        """
        # update class variable
        SongSectionValues.songTimeSig = songTimeSig


    def set_section(self, name):
        """
        given a section name
        update the class and instance variables
        """

        # update class variables
        self.increment_sections()

        SongSectionValues.structure_by_name_long = SongSectionValues.structure_by_name_long + str(name) + '-'
        SongSectionValues.structure_by_name = SongSectionValues.structure_by_name + truncate_section(name) + '-'
        SongSectionValues.structure_by_name_initial = SongSectionValues.structure_by_name_initial + truncate_section(name)[0]

        # if section not in section_letter dictionary: add to dictionary, increment value
        if truncate_section(name) not in SongSectionValues.section_letter:
            SongSectionValues.section_letter[truncate_section(name)] = SongSectionValues.letter_current
            SongSectionValues.letter_current = chr((ord(SongSectionValues.letter_current) - ord('A') + 1) % 26 + ord('A'))
        # add section letter to structure_by_letter
        SongSectionValues.structure_by_letter = SongSectionValues.structure_by_letter + SongSectionValues.section_letter[truncate_section(name)]

        # set instance variable unique to each instance
        self.name = name


    def show_text_in_stream(self, a_stream):
        # print('show_text_in_stream ------------------------------------------------- stream.id = decimal, hex', song.id, hex(song.id))
        print("show_text_in_stream ------------------------------------------------- stream.id", a_stream.id)

        # song.show('text')

        offset_end = 0.0
        stream_copy = copy.deepcopy(a_stream)

        for n in stream_copy.flatten():
            # print('type(n) ', type(n) )
            if type(n) == music21.clef.TrebleClef:
                print('music21.clef.TrebleClef')

            if type(n) == music21.expressions.TextExpression:
                # print('music21.expressions.TextExpression')
                print('TextExpression =', n.content)

            if type(n) == music21.key.KeySignature:
                # print('music21.key.KeySignature', song.tonic.name, song.mode)
                print('music21.key.KeySignature', self.stream1.keySignature)  # None
                first = True
                for sKS in a_stream.flatten().getElementsByClass('KeySignature'):
                    if first:
                        a_stream.KeySignature = sKS
                        print('First KeySignature:', a_stream.KeySignature)  # e.g. <music21.key.KeySignature of 1 flat>
                        print('.sharps:', a_stream.KeySignature.sharps)  # e.g. -1
                        print('.getScale(major):',
                              a_stream.KeySignature.getScale('major'))  # e.g. <music21.scale.MajorScale F major>
                        first = False
                    else:
                        print('other KeySignature:', sKS)

            if type(n) == music21.metadata.Metadata:
                # Metadata represent data for a work or fragment, including
                # title, composer, dates, and other relevant information.
                print('music21.metadata.Metadata')
                print('all =', a_stream.metadata.all())

                # print('title =', song.metadata.title) # crash if none
                # print('composer =', song.metadata.composer)
                # print('date = ', song.metadata.date)
                # print('lyricist = ', song.metadata.lyricist)

            if type(n) == music21.meter.TimeSignature:
                # get the timesignatures
                first = True
                for tSig in a_stream.getTimeSignatures():  # may not be required, .cf song_section_values missed n=3/4 as tsig=4/4 on God_Save_The_Queen.mxl
                    if first:
                        a_stream.TimeSig = tSig
                        print('First Time Signature:',
                              tSig)  # eg First Time Signature: <music21.meter.TimeSignature 4/4>
                        first = False
                    else:
                        print('Other Time Signature:', tSig)

            if type(n) == music21.note.Note or type(n) == music21.note.Rest:
                self.show_text_of_note(n)

            if type(n) == music21.tempo.MetronomeMark:
                print('music21.tempo.MetronomeMark', n.number)

        # min_note, max_note = calc_the_note_range(song)
        # print('min_note, max_note', min_note, max_note)

        pass

    def show_text_of_note(self, n):
        """
        takes a note and the beats to the bar
        and print the text to the console
        """
        beat_count = SongSectionValues.songTimeSig.numerator / (SongSectionValues.songTimeSig.denominator / 4)
        # print('beat_count = ts.numerator / (ts.denominator / 4)', beat_count, ts.numerator, ts.denominator)

        offset_end = n.offset + n.duration.quarterLength
        # calculate offset_bar_end = beat_count * ( truncated (n.offset / beat_count) + 1)
        truncated_bar = int('%.0f' % (n.offset / beat_count))
        offset_bar_end = beat_count * (truncated_bar + 1)
        # print('offset_bar_end = beat_count * (truncated_bar + 1)', offset_bar_end, beat_count, truncated_bar)
        if offset_end > offset_bar_end:
            # print('WARNING next duration: \t\t\t\t  offset_end', offset_end, '>', 'offset_bar_end', offset_bar_end,'- Replace with tied note or rest to end of bar and rest at beginning of next bar.')
            pass
        # print("Note: %s%d %0.1f" % (n.pitch.name, n.pitch.octave, n.duration.quarterLength))

        if type(n) == music21.note.Note:
            print('offset %.4f' % n.offset, '\t bar %.4f' % ((n.offset / beat_count) + 1), '\t o', n.offset, '\t + ql',
                  n.duration.quarterLength, '\t = o_end %.4f' % offset_end, '\t note qLen lyric:\t', n.nameWithOctave,
                  '\t',
                  n.duration.quarterLength, '\t', n.lyric)

        if type(n) == music21.note.Rest:
            # print('offset_float %.4f' % n.offset, 'bar %.4f'% (n.offset / beat_count), 'rest quarterLength, offset_fraction, offset_end:', n.duration.quarterLength, n.offset, '%.4f' %offset_end )
            print('offset %.4f' % n.offset, '\t bar %.4f' % ((n.offset / beat_count) + 1), '\t o', n.offset, '\t + ql',
                  n.duration.quarterLength, '\t = o_end %.4f' % offset_end, '\t rest quarterLength:',
                  n.duration.quarterLength)

    def update_rest(self, n):
        """
        add rest note to stream
        """
        # append note
        self.stream1.append(n)

    def update(self, n, first_note_of_section):
        """
        if triplet: DUR_TUPLET = True
        if note.dur < DUR_LEAST: DUR_LEAST = note.dur
        if note.dur > DUR_LONGEST: DUR_LONGEST = note.dur
        if note not scale note: TONES_ON_KEY = True
        if note.nameWithOctave < TONE_RANGE_BOTTOM: TONE_RANGE_BOTTOM = note.nameWithOctave
        if note.nameWithOctave > TONE_RANGE_TOP: TONE_RANGE_TOP = note.nameWithOctave
        """

        # complex durations
        c1_6 = Fraction(1, 6)
        c1_3 = Fraction(1, 3)
        c2_3 = Fraction(2, 3)
        c4_3 = Fraction(4, 3)
        c8_3 = Fraction(8, 3)

        if first_note_of_section:
            # update (only on first note) REST_NOTE_LINE_OFFSET
            prev_measure_offset = (math.trunc(n.offset / SongSectionValues.songTimeSig.beatCount) ) * SongSectionValues.songTimeSig.beatCount
            note_offset_from_start_measure = n.offset - prev_measure_offset
            # print('n.offset',n.offset,'ts.beatCount',ts.beatCount,'prev_measure_offset',prev_measure_offset,'note_offset_from_start_measure',note_offset_from_start_measure )
            self.REST_NOTE_LINE_OFFSET = note_offset_from_start_measure
            first_note_of_section = False
            # append note
            self.stream1.append(n)

        else: # notes other than first note

            # append note
            self.stream1.append(n)

            # update DUR_PREV_DIFF, TONE_PREV_INTERVAL

            # from MarkMelGen.conf:
            # DUR_PREV_DIFF - compare duration with previous duration, e.g. where 2, duration is >= 1/2 previous and <= 2 x previous etc ,
            # where 0 and <= 1, do not compare with previous duration.

            # if this_dur_Prev_diff is bigger, update DUR_PREV_DIFF
            bigger = False
            if self.dur_prev != 0:  # do not work out for first note
                if self.dur_prev < n.duration.quarterLength:  # previous note is shorter e.g. dur_prev = 1.0 <  n = 2.0
                    this_dur_Prev_diff = (float(n.duration.quarterLength)) / (float(Fraction(self.dur_prev)))
                    # this_dur_Prev_diff =  e.g. (n = 2.0) / dur_prev = 1.0
                    if this_dur_Prev_diff > self.DUR_PREV_DIFF: bigger = True
                if self.dur_prev > n.duration.quarterLength:  # previous note is longer e.g. dur_prev = 4.0 <  n = 2.0
                    this_dur_Prev_diff = (float(Fraction(self.dur_prev)) / float(
                        n.duration.quarterLength))  # this_dur_Prev_diff =  e.g. (n = 2.0) * dur_prev = 4.0
                    if this_dur_Prev_diff > self.DUR_PREV_DIFF: bigger = True
            if bigger: self.DUR_PREV_DIFF = this_dur_Prev_diff

            # update TONE_PREV_INTERVAL: calc semitone_interval_with_prev_note for
            aInterval = interval.Interval(self.note_prev, n)
            AIntSemi = abs(aInterval.semitones)
            if AIntSemi > self.TONE_PREV_INTERVAL: self.TONE_PREV_INTERVAL = AIntSemi

        # any note update:
        # DURATION_SET, DUR_RATIONAL, DUR_TUPLET, DUR_LEAST, DUR_LONGEST, TONES_ON_KEY, TONE_RANGE_BOTTOM, TONE_RANGE_TOP
        # dur_prev
        duration_found = False
        for dur_from_set in self.DURATION_SET:
            if Fraction(n.duration.quarterLength) == Fraction(dur_from_set):
                duration_found = True
        if not duration_found:
            bisect.insort(self.DURATION_SET, str(n.duration.quarterLength))

        # if triplet: DUR_TUPLET = True
        if ((n.duration.quarterLength == c1_6) or (n.duration.quarterLength == c1_3) or (n.duration.quarterLength == c2_3)):
            self.DUR_TUPLET = True
            self.DUR_RATIONAL = False
        # if note.dur < DUR_LEAST: DUR_LEAST = note.dur
        if n.duration.quarterLength < self.DUR_LEAST: self.DUR_LEAST = n.duration.quarterLength
        # if note.dur > DUR_LONGEST: DUR_LONGEST = note.dur
        if n.duration.quarterLength > self.DUR_LONGEST: self.DUR_LONGEST = n.duration.quarterLength

        # if note not scale note: TONES_ON_KEY = True
        if self.song_key.mode == 'major':
            sc = scale.MajorScale(self.song_key.tonic.name)
        else:
            sc = scale.MinorScale(self.song_key.tonic.name)
        scale_degree = sc.getScaleDegreeFromPitch(n)
        if scale_degree == None:
            self.TONES_ON_KEY = False

        # if note.nameWithOctave < TONE_RANGE_BOTTOM: TONE_RANGE_BOTTOM = note.nameWithOctave
        # if n.nameWithOctave < self.TONE_RANGE_BOTTOM: self.TONE_RANGE_BOTTOM = n.nameWithOctave
        # if note.nameWithOctave > TONE_RANGE_TOP: TONE_RANGE_TOP = note.nameWithOctave
        # Following gave False with next line: A5 > G5, B5 > G5, C6 > G5 (assume bug with music21)
        # if n.nameWithOctave > self.TONE_RANGE_TOP: self.TONE_RANGE_TOP = n.nameWithOctave

        new_note = note.Note()
        new_note.nameWithOctave = n.nameWithOctave
        min_note = note.Note()
        min_note.nameWithOctave = self.TONE_RANGE_BOTTOM
        max_note = note.Note()
        max_note.nameWithOctave = self.TONE_RANGE_TOP

        if note.Note(n.nameWithOctave) < note.Note(min_note.nameWithOctave):
            self.TONE_RANGE_BOTTOM = n.nameWithOctave

        if note.Note(n.nameWithOctave) > note.Note(max_note.nameWithOctave):
            self.TONE_RANGE_TOP = n.nameWithOctave

        # TONE_SCALE_SET
        tone_found = False
        for tone_from_set in self.TONE_SCALE_SET:
            if pitch.Pitch(n.name).ps == pitch.Pitch(tone_from_set).ps:
                tone_found = True
        if not tone_found:
            bisect.insort(self.TONE_SCALE_SET, str(n.name))

        self.dur_prev = n.duration.quarterLength  # update self.dur_prev
        self.note_prev = n

    def print_placeholder_chords(self):
        """
        populate song_offset_placeholder_chords with offsets and pitch class "chords" from input music and print e.g.

        get first and last note
        for each chord symbol stream item
            get_pitch_classes_in_stream of the chord
            append the offset and pitch_classes to the song_offset_placeholder_chords

        e.g. song_offset_placeholder_chords  =  {0.0: '1000 0000 0000', 12.0: '0000 1100 0000', 24.0: '1000 0000 0001', 36.0: '1000 0000 0000'}

        :return: void
        """

        print('print_placeholder_chords(self)')

        # print('song_key.name', song_key.name)
        first_note = self.get_first_note()
        first_note_offset = first_note.offset

        print('first note offset', first_note.offset)
        last_note = self.get_last_note()
        last_note_offset = last_note.offset
        last_note_duration_quarterLength = last_note.duration.quarterLength
        end_of_last_note_offset = last_note_offset + last_note_duration_quarterLength
        current_section_start_note_offset = SongSectionValues.current_song_length_offset

        print('last_note_offset', last_note_offset,'last_note_duration_quarterLength',last_note_duration_quarterLength)
        # self.show_text_in_stream(self.stream1)
        # print('# section key', song_key.name)

        looking_for_first_chord = True
        next_note_is_first_chord_offset = False
        next_note_is_chord_offset = False
        start_note_offset = 0.0
        last_note_duration = 0.0
        tune_sig_to_chord = {}
        first_chord = True
        #

        print('has_chord_symbols(self.song_stream)', has_chord_symbols(self.song_stream))
        # input('Press Enter to continue...')


        # for each stream element in a_song
        for n in self.song_stream.flatten():
            # print('type(n)',type(n))
            if type(n) == music21.harmony.ChordSymbol or type(n) == music21.harmony.NoChord:
                if type(n) == music21.harmony.NoChord:
                    print('NoChord', n.figure, n)
                else:
                    # print('ChordSymbol ', n, n.figure, n.key, 'If writeAsChord False the harmony symbol is written',n.writeAsChord, n.romanNumeral )
                    print('ChordSymbol ', n.figure, n )
                #     if chord and chord not 'NC' and looking_for_first_chord:
                if looking_for_first_chord and type(n) != music21.harmony.NoChord:
                    looking_for_first_chord = False
                    next_note_is_first_chord_offset = True
                    chord_1 = n.figure
                    map_chord = chord_1
                else: # found a later chord
                    # if type(n) != music21.harmony.NoChord:
                    next_note_is_chord_offset = True
                    chord_2 = n.figure


            # if type(n) == music21.harmony.NoChord:
            #     print('NoChord', n.figure, n)

            if type(n) == music21.note.Note or type(n) == music21.note.Rest:

                last_note_duration = n.duration.quarterLength
                if type(n) == music21.note.Note:
                    print('note offset, duration, nameWithOctave', n.offset, n.duration.quarterLength, n.nameWithOctave,)
                else:
                    print('rest offset, duration,               ', n.offset, n.duration.quarterLength)

                if next_note_is_first_chord_offset:
                    # get next note
                    start_note_offset = n.offset
                    looking_for_first_chord = False
                    next_note_is_first_chord_offset = False
                if next_note_is_chord_offset:
                    next_note_is_chord_offset = False
                    end_note_offset = n.offset
                    shorter_stream = self.get_stream(start_note_offset, end_note_offset)

                    if stream_has_a_note(shorter_stream) :
                        # print('ANALYZE_CHOICE =', analyze_choice)
                        if map_chord != 'N.C.' and map_chord != 'NC':
                            # different_pitch_classes = get_different_pitch_classes_in_stream(shorter_stream)

                            key_chord = get_pitch_classes_in_stream(shorter_stream)
                            key = (display_pitch_classes(key_chord))

                            # convert key_chord to sho_cho
                            if first_chord:
                                SongSectionValues.song_offset_placeholder_chords = SongSectionValues.song_offset_placeholder_chords + str(
                                    start_note_offset) + ": '" + key + "'"
                                first_chord = False
                            else:  # subsequent chords
                                SongSectionValues.song_offset_placeholder_chords = SongSectionValues.song_offset_placeholder_chords + ", " + str(
                                    start_note_offset) + ": '" + key + "'"

                        else: # no chord
                            # append offset and no chord to song_offset_placeholder_chords
                            if first_chord:
                                SongSectionValues.song_offset_placeholder_chords = SongSectionValues.song_offset_placeholder_chords + str(
                                    start_note_offset) + ": '" + NO_CHORD_DISPLAY_PITCH_CLASSES + "'"
                                    # start_note_offset) + ": '" + str(NO_CHORD_DISPLAY_PITCH_CLASSES).replace(" ", "") + "'"

                                first_chord = False
                            else:  # subsequent chords
                                SongSectionValues.song_offset_placeholder_chords = SongSectionValues.song_offset_placeholder_chords + ", " + str(
                                    start_note_offset) + ": '" + NO_CHORD_DISPLAY_PITCH_CLASSES + "'"
                                    # start_note_offset) + ": '" + str(NO_CHORD_DISPLAY_PITCH_CLASSES).replace(" ", "") + "'"

                        map_chord = chord_2
                        start_note_offset = end_note_offset
        # handle last chord / note(s)

        # 20221224 last note chord wrong
        map_chord = chord_1

        if map_chord != 'N.C.' and map_chord != 'NC':
            end_note_offset = start_note_offset + last_note_duration
            shorter_stream = self.get_stream(start_note_offset, end_note_offset)
            if stream_has_a_note(shorter_stream) :
                # key_chord = shorter_stream.analyze(self.analyze_choice)
                key_chord = get_pitch_classes_in_stream(shorter_stream)
                key = (display_pitch_classes(key_chord))

                # convert key_chord to sho_cho
                # sho_cho = short_chord(key_chord.name)
                SongSectionValues.song_offset_placeholder_chords = SongSectionValues.song_offset_placeholder_chords + ", " + str(
                    start_note_offset) + ": '" + key + "'"

        else:  # no chord
            SongSectionValues.song_offset_placeholder_chords = SongSectionValues.song_offset_placeholder_chords + ", " + str(
                start_note_offset) + ": '" + NO_CHORD_DISPLAY_PITCH_CLASSES + "'"

        # print('tune_sig_to_chord with frequency=', tune_sig_to_chord)
        print('SongSectionValues.song_offset_placeholder_chords', SongSectionValues.song_offset_placeholder_chords)
        # input('Press Enter to continue...')

    def print(self):
        """
        get first and last note
        calc harmonic rhythm, offset_increment
        for each harmonic rhythm
            for each offset_increment
                analyse the short chord from the song key of the short stream
                append the offset and short chord to the song_offset_chord

        :return: void
        """
        print('# section', self.number_of_song_sections, 'name      =', self.name)

        truncated_section_name = truncate_section(self.name)
        printable_name = '[song_' + truncated_section_name + ']'

        # song_key = self.stream1.analyze('key')
        # print('ANALYZE_CHOICE =', self.analyze_choice)
        song_key = self.stream1.analyze(self.analyze_choice)

        # print('song_key.name', song_key.name)
        first_note = self.get_first_note()
        first_note_offset = first_note.offset

        # print('first note offset', first_note.offset)
        last_note = self.get_last_note()
        last_note_offset = last_note.offset
        last_note_duration_quarterLength = last_note.duration.quarterLength
        current_section_start_note_offset = SongSectionValues.current_song_length_offset

        # print('last_note_offset', last_note_offset,'last_note_duration_quarterLength',last_note_duration_quarterLength)
        # self.show_text_in_stream(self.stream1)

        # calc harmonic rhythm 1 bars per chord i.e. offset length of 1 bar
        beat_count = SongSectionValues.songTimeSig.numerator / (SongSectionValues.songTimeSig.denominator / 4)

        # print('Possible Harmonic rhythms ------------------------------------------------------------------------------')
        # print('song_key.name', song_key.name)
        # print('Possible Harmonic rhythms.  Chord changes every: -------------------------------------------------------')
        print('# section key', song_key.name)
        print('Harmonic rhythms. Chord may change every: 1 beat, 2 beats, 1 bar, 2 bars or 4 bars.')


        # chord each beat
        print('1 beat ...')
        chord_each_beat = ''
        chord_count_init = 1.0
        chord_count = 1.0
        chord_count_inc = 1.0
        first_chord = True
        sho_cho = 'NC '
        offset_increment = beat_count / SongSectionValues.songTimeSig.numerator
        if SongSectionValues.songTimeSig.ratioString == '6/8':
            print('Time Signature', SongSectionValues.songTimeSig)
            chord_count_init = offset_increment
            chord_count = offset_increment
            chord_count_inc = offset_increment
        if SongSectionValues.songTimeSig.ratioString == '9/8':
            print('Time Signature 9/8')
            chord_count_init = offset_increment
            chord_count = offset_increment
            chord_count_inc = offset_increment
        if SongSectionValues.songTimeSig.ratioString == '2/2' or SongSectionValues.songTimeSig.ratioString == '12/8':
            print('Time Signature', SongSectionValues.songTimeSig)
            offset_increment = beat_count / 4
            # e.g. for 2 / 2, beat_count = 4.0 , offset_increment  = 1.0
            # e.g. = 6 / 4 = 1.5
            chord_count_init = 1.5
            chord_count = 1.5
            chord_count_inc = 1.5
        # print('1 beat: offset_increment', offset_increment,'chord_count_inc',chord_count_inc)
        if SongSectionValues.offsets != None:
            offset_increment = SongSectionValues.offsets[Harmonic_Rhythm.BEAT1.value]
        print('1 beat: offset_increment', offset_increment)

        for start_note_offset in numpy.arange(current_section_start_note_offset, (last_note_offset + last_note_duration_quarterLength), offset_increment):
            # print('start_note_offset', start_note_offset, 'end_note_offset', (start_note_offset + offset_increment))
            shorter_stream = self.get_stream(start_note_offset, (start_note_offset + offset_increment) )
            # self.show_text_in_stream(shorter_stream)
            if stream_has_a_note(shorter_stream):
                # print('ANALYZE_CHOICE =', self.analyze_choice)
                song_key = shorter_stream.analyze(self.analyze_choice)
                song_key_name = short_chord(song_key.name)
                sho_cho = short_chord(song_key.name)
            else:
                song_key_name = sho_cho
            # print('Chord = ', song_key.name)
            chord_each_beat = chord_each_beat + song_key_name
            if first_chord:
                SongSectionValues.song_offset_chord_1_beat = SongSectionValues.song_offset_chord_1_beat + str(start_note_offset) + ": '" + str(sho_cho).replace(" ", "") + "'"
                first_chord = False
            else: # subsequent chords
                SongSectionValues.song_offset_chord_1_beat = SongSectionValues.song_offset_chord_1_beat + ", " + str(start_note_offset) + ": '" + str(sho_cho).replace(" ", "") + "'"

            if chord_count == beat_count:
                chord_each_beat = chord_each_beat + '|'
                chord_count = chord_count_init
            else:
                chord_count = chord_count + chord_count_inc

        SongSectionValues.song_chords_1_beat = SongSectionValues.song_chords_1_beat + chord_each_beat
        # print('1 beat  |' + chord_each_beat)

        SongSectionValues.song_offset_chord_1_beat = SongSectionValues.song_offset_chord_1_beat + ','

        # chords_half_a_bar for even beats (different for odd beats in a bar)
        print('2 beats ...')
        offset_increment = beat_count / 2
        # for 9/8 offset_increment = 1.5
        if SongSectionValues.songTimeSig.ratioString == '9/4' or SongSectionValues.songTimeSig.ratioString == '9/8':
            print('Time Signature', SongSectionValues.songTimeSig)
            offset_increment = beat_count / 3
        if SongSectionValues.offsets != None:
            offset_increment = SongSectionValues.offsets[Harmonic_Rhythm.BEAT2.value]
        print('2_beat offset_increment', offset_increment)
        chords_half_a_bar = ''
        first_chord = True
        second_chord = False
        sho_cho = 'NC '

        for start_note_offset in numpy.arange(current_section_start_note_offset, (last_note_offset + last_note_duration_quarterLength),
                                                  offset_increment):
            # print('start_note_offset', start_note_offset, 'end_note_offset', (start_note_offset + offset_increment))
            shorter_stream = self.get_stream(start_note_offset, (start_note_offset + offset_increment) )
            # self.show_text_in_stream(shorter_stream)
            if stream_has_a_note(shorter_stream):
                # print('ANALYZE_CHOICE =', self.analyze_choice)
                song_key = shorter_stream.analyze(self.analyze_choice)
                song_key_name = short_chord(song_key.name)
                sho_cho = short_chord(song_key.name)
            else:
                song_key_name = sho_cho
            # print('Chord = ', song_key.name)

            if SongSectionValues.songTimeSig.numerator == 3:
                if second_chord:
                    chords_half_a_bar = chords_half_a_bar + song_key_name
                else:
                    # chords_half_a_bar = chords_half_a_bar + song_key_name + '   '
                    chords_half_a_bar = chords_half_a_bar + song_key_name + sho_cho

            else:
                if SongSectionValues.songTimeSig.ratioString == '6/8':
                    chords_half_a_bar = chords_half_a_bar + song_key_name + '      '
                else:
                    if SongSectionValues.songTimeSig.ratioString == '9/8':
                        chords_half_a_bar = chords_half_a_bar + sho_cho
                    else:
                        chords_half_a_bar = chords_half_a_bar + song_key_name + sho_cho

            if second_chord:
                chords_half_a_bar = chords_half_a_bar + '|'
                second_chord = False
            else:
                second_chord = True

            if first_chord:
                SongSectionValues.song_offset_chord_2_beat = SongSectionValues.song_offset_chord_2_beat + str(start_note_offset) + ": '" + str(sho_cho).replace(" ", "") + "'"
                first_chord = False
            else: # subsequent chords
                SongSectionValues.song_offset_chord_2_beat = SongSectionValues.song_offset_chord_2_beat + ", " + str(start_note_offset) + ": '" + str(sho_cho).replace(" ", "") + "'"

        SongSectionValues.song_chords_2_beat = SongSectionValues.song_chords_2_beat + chords_half_a_bar
        # print('2 beats |' + chords_half_a_bar)
        SongSectionValues.song_offset_chord_2_beat = SongSectionValues.song_offset_chord_2_beat + ','


        # chords_1_per_bar
        print('1 bar ...')
        offset_increment = beat_count
        if SongSectionValues.offsets != None:
            offset_increment = SongSectionValues.offsets[Harmonic_Rhythm.BAR1.value]
        print('offset_increment', offset_increment)
        chords_1_per_bar = ''
        first_chord = True
        sho_cho = 'NC '

        for start_note_offset in numpy.arange(current_section_start_note_offset, (last_note_offset + last_note_duration_quarterLength),
                                                  offset_increment):
            # print('start_note_offset', start_note_offset, 'end_note_offset', (start_note_offset + offset_increment))
            shorter_stream = self.get_stream(start_note_offset, (start_note_offset + offset_increment) )
            # self.show_text_in_stream(shorter_stream)
            if stream_has_a_note(shorter_stream):
                # print('ANALYZE_CHOICE =', self.analyze_choice)
                song_key = shorter_stream.analyze(self.analyze_choice)
                sho_cho = short_chord(song_key.name)
            else:
                sho_cho = 'NC '
            chords_1_per_bar = chords_1_per_bar + sho_cho + '|'


            if first_chord:
                SongSectionValues.song_offset_chord_1_bar = SongSectionValues.song_offset_chord_1_bar + str(start_note_offset) + ": '" + str(sho_cho).replace(" ", "") + "'"
                first_chord = False
            else: # subsequent chords
                SongSectionValues.song_offset_chord_1_bar = SongSectionValues.song_offset_chord_1_bar + ", " + str(start_note_offset) + ": '" + str(sho_cho).replace(" ", "") + "'"

        SongSectionValues.song_chords_1_bar = SongSectionValues.song_chords_1_bar + chords_1_per_bar
        # print('1 bar   |' + chords_1_per_bar)
        SongSectionValues.song_offset_chord_1_bar = SongSectionValues.song_offset_chord_1_bar + ','


        # chord every 2 measures
        print('2 bars ...')

        # if there are < 2 measures then
        if (last_note_offset + last_note_duration_quarterLength - current_section_start_note_offset) < (beat_count * 2):
            SongSectionValues.song_chords_2_bar = SongSectionValues.song_chords_2_bar + chords_1_per_bar
            SongSectionValues.song_offset_chord_2_bar = SongSectionValues.song_offset_chord_2_bar + str(
                current_section_start_note_offset) + ": '" + str(sho_cho).replace(" ", "") + "'"
            SongSectionValues.song_offset_chord_2_bar = SongSectionValues.song_offset_chord_2_bar + ','

        else:
            # chords_2_bars_each
            offset_increment = beat_count * 2
            if SongSectionValues.offsets != None:
                offset_increment = SongSectionValues.offsets[Harmonic_Rhythm.BAR2.value]
            print('offset_increment', offset_increment)
            chords_2_bars_each = ''
            num_slices = int((last_note_offset + last_note_duration_quarterLength - current_section_start_note_offset) / offset_increment)
            segment_last_note_offset = (last_note_offset + last_note_duration_quarterLength) - (
                        offset_increment * num_slices)
            segment_last_note_bar = int(segment_last_note_offset / beat_count)
            # print('last_note_offset',last_note_offset,'last_note_duration_quarterLength',last_note_duration_quarterLength,'offset_increment', offset_increment,'num_slices', num_slices,'segment_last_note_offset',segment_last_note_offset,'segment_last_note_bar',segment_last_note_bar)
            slice = 0
            first_chord = True
            sho_cho = 'NC '

            for start_note_offset in numpy.arange(current_section_start_note_offset,
                                                      (last_note_offset + last_note_duration_quarterLength),
                                                      offset_increment):
                # print('start_note_offset', start_note_offset, 'end_note_offset', (start_note_offset + offset_increment))
                shorter_stream = self.get_stream(start_note_offset, (start_note_offset + offset_increment) )
                # self.show_text_in_stream(shorter_stream)
                if stream_has_a_note(shorter_stream):
                    song_key = shorter_stream.analyze(self.analyze_choice)
                    sho_cho = short_chord(song_key.name)
                else:
                    sho_cho = 'NC '
                chords_2_bars_each = chords_2_bars_each + sho_cho

                if slice < num_slices:
                    chords_2_bars_each = chords_2_bars_each + '|' + sho_cho + '|'
                else:
                    chords_2_bars_each = chords_2_bars_each + '|'

                slice = slice + 1
                if first_chord:
                    SongSectionValues.song_offset_chord_2_bar = SongSectionValues.song_offset_chord_2_bar + str(
                        start_note_offset) + ": '" + str(sho_cho).replace(" ", "") + "'"
                    first_chord = False
                else:  # subsequent chords
                    SongSectionValues.song_offset_chord_2_bar = SongSectionValues.song_offset_chord_2_bar + ", " + str(
                        start_note_offset) + ": '" + str(sho_cho).replace(" ", "") + "'"

            SongSectionValues.song_chords_2_bar = SongSectionValues.song_chords_2_bar + chords_2_bars_each
            # print('2 bars  |' + chords_2_bars_each)
            SongSectionValues.song_offset_chord_2_bar = SongSectionValues.song_offset_chord_2_bar + ','

        # chord every 4 measures
        print('4 bars ...')
        first_chord = True

        # < 2 measures use 1 bar
        if (last_note_offset + last_note_duration_quarterLength - current_section_start_note_offset) < (beat_count * 2):
            SongSectionValues.song_chords_4_bar = SongSectionValues.song_chords_4_bar + chords_1_per_bar
            SongSectionValues.song_offset_chord_4_bar = SongSectionValues.song_offset_chord_4_bar + str(
                current_section_start_note_offset) + ": '" + str(sho_cho).replace(" ", "") + "'"
            SongSectionValues.song_offset_chord_4_bar = SongSectionValues.song_offset_chord_4_bar + ','

        # >=2 and < 4 measures: use 2 bars
        if ((last_note_offset + last_note_duration_quarterLength - current_section_start_note_offset) >= (beat_count * 2)) and (
            (last_note_offset + last_note_duration_quarterLength - current_section_start_note_offset) < (beat_count * 4)):
            SongSectionValues.song_chords_4_bar = SongSectionValues.song_chords_4_bar + chords_2_bars_each
            if first_chord:
                SongSectionValues.song_offset_chord_4_bar = SongSectionValues.song_offset_chord_4_bar + str(
                    current_section_start_note_offset + start_note_offset) + ": '" + str(sho_cho).replace(" ",
                                                                                                          "") + "'"
                SongSectionValues.song_offset_chord_4_bar = SongSectionValues.song_offset_chord_4_bar + ','

                first_chord = False
            else:  # subsequent chords
                SongSectionValues.song_offset_chord_4_bar = SongSectionValues.song_offset_chord_4_bar + ", " + str(
                    current_section_start_note_offset + start_note_offset) + ": '" + str(sho_cho).replace(" ","") + "'"

        # if there are >= 4 measures then calc
        if ( last_note_offset + last_note_duration_quarterLength - current_section_start_note_offset) >= (beat_count * 4):
            # calc chord every 4 measures
            offset_increment = beat_count * 4
            if SongSectionValues.offsets != None:
                offset_increment = SongSectionValues.offsets[Harmonic_Rhythm.BAR4.value]
            print('offset_increment', offset_increment)

            chords_4_bars_each = ''
            num_slices = int((last_note_offset + last_note_duration_quarterLength - current_section_start_note_offset) / offset_increment)
            segment_last_note_offset = (last_note_offset + last_note_duration_quarterLength - current_section_start_note_offset) - ( offset_increment * num_slices)
            segment_last_note_bar = int(segment_last_note_offset / beat_count)
            # print('last_note_offset',last_note_offset,'last_note_duration_quarterLength',last_note_duration_quarterLength,'offset_increment', offset_increment,'num_slices', num_slices,'segment_last_note_offset',segment_last_note_offset,'segment_last_note_bar',segment_last_note_bar)
            slice = 0
            # first_chord = True
            sho_cho = 'NC '

            for start_note_offset in numpy.arange(current_section_start_note_offset, (last_note_offset + last_note_duration_quarterLength),
                                                  offset_increment):
                # print('start_note_offset', start_note_offset, 'end_note_offset', (start_note_offset + offset_increment))
                shorter_stream = self.get_stream(start_note_offset, (start_note_offset + offset_increment))
                # self.show_text_in_stream(shorter_stream)
                if stream_has_a_note(shorter_stream):
                    # print('ANALYZE_CHOICE =', self.analyze_choice)
                    song_key = shorter_stream.analyze(self.analyze_choice)
                    sho_cho = short_chord(song_key.name)
                else:
                    sho_cho = 'NC '
                chords_4_bars_each = chords_4_bars_each + sho_cho

                if slice < num_slices:
                    chords_4_bars_each = chords_4_bars_each + '|' + sho_cho + '|' + sho_cho + '|' + sho_cho + '|'
                else:
                    # chords_4_bars_each = chords_4_bars_each + '|'
                    if segment_last_note_bar == 1:
                        chords_4_bars_each = chords_4_bars_each + '|'
                    else:
                        # for 2 to segment_last_note_bar: add | %
                        for i in list(range(2, (segment_last_note_bar + 1))):
                            chords_4_bars_each = chords_4_bars_each + '|' + sho_cho
                        chords_4_bars_each = chords_4_bars_each + '|'
                slice = slice + 1
                if first_chord:
                    SongSectionValues.song_offset_chord_4_bar = SongSectionValues.song_offset_chord_4_bar + str(
                        start_note_offset) + ": '" + str(sho_cho).replace(" ", "") + "'"
                    first_chord = False
                else:  # subsequent chords
                    SongSectionValues.song_offset_chord_4_bar = SongSectionValues.song_offset_chord_4_bar + ", " + str(
                        start_note_offset) + ": '" + str(sho_cho).replace(" ", "") + "'"

            SongSectionValues.song_chords_4_bar = SongSectionValues.song_chords_4_bar + chords_4_bars_each
            # print('4 bars  |' + chords_4_bars_each)
            SongSectionValues.song_offset_chord_4_bar = SongSectionValues.song_offset_chord_4_bar + ','

        # update current_song_length_offset
        SongSectionValues.current_song_length_offset = last_note_offset + last_note_duration_quarterLength

    def print_class_variable(self):
        print('# -----------------------------------------------------------------------')
        print('')
        if SongSectionValues.song_offset_chord_1_beat != '{}':
            print('song_offset_chord_1_beat =',SongSectionValues.song_offset_chord_1_beat)
            print('song_offset_chord_2_beat =',SongSectionValues.song_offset_chord_2_beat)
            print('song_offset_chord_1_bar  = ',SongSectionValues.song_offset_chord_1_bar)
            print('song_offset_chord_2_bar  = ',SongSectionValues.song_offset_chord_2_bar)
            print('song_offset_chord_4_bar  = ',SongSectionValues.song_offset_chord_4_bar)
        if SongSectionValues.song_offset_placeholder_chords != '{}':
            # print('song_offset_placeholder_chords  = ',SongSectionValues.song_offset_placeholder_chords)
            pass

        print('')
        print('# number_of_sections_found =', SongSectionValues.number_of_song_sections)
        print('# song structure:')
        print('# long    =', SongSectionValues.structure_by_name_long[:-1])
        print('# name    =', SongSectionValues.structure_by_name[:-1])
        print('# initial =', self.structure_by_name_initial)
        print('# letter  =', self.structure_by_letter)


    def write_chords(self, input_filename, offset_chord, output_filename):
        """
        write melody with chords to mxl
        :param input_filename for score title
        :param offset_chord: dictionary
        :param output_filename: e.g. my.mxl
        :return: void

        prev_sho_cho = ''
        for each element
            if not note:
                copy to output stream
            else:
                sho_cho = get_chord(n.offset, offset_chord)
                if sho_cho != prev_sho_cho:
                    append sho_cho
                append note
        write output stream
        """

        print('write_chords(self, input_filename, offset_chord, output_filename):', input_filename, offset_chord, output_filename)
        # print('SongSectionValues.offset_section',SongSectionValues.offset_section)

        score_to_write = stream.Score()
        p0 = stream.Part()
        p0.insert(0, self.the_instrument)

        prev_sho_cho = 'NC'
        the_offset = 0.0

        # for each element
        for n in SongSectionValues.song_stream.flatten():
            # if not note:
            if type(n) != music21.note.Note and type(n) != music21.note.Rest:
                # copy to output stream
                # print('type(n)', type(n))

                # copy all non-note types to output stream (unless instrument, ChordSymbol or TextBox)
                if issubclass(n.__class__, music21.instrument.Instrument) or \
                        issubclass(n.__class__, music21.harmony.ChordSymbol) or \
                        issubclass(n.__class__, music21.text.TextBox) :
                    # do not copy an Instrument or a chord
                    pass
                # if text expression and only one 1 section (dummy intro)
                elif issubclass(n.__class__, music21.expressions.TextExpression) and len(SongSectionValues.offset_section) == 1:
                    # print('len(SongSectionValues.offset_section)', len(SongSectionValues.offset_section))
                    pass
                else:
                    p0.append(n)
            # else is note or rest
            else:
                # get chord for note
                # sho_cho = get_chord(float(int(n.offset)), offset_chord)
                sho_cho = get_chord(n.offset, offset_chord, prev_sho_cho )
                # if new chord or beginning of a section
                if sho_cho != prev_sho_cho or (n.offset in SongSectionValues.offset_section):
                    # append chord
                    if sho_cho == 'NC':
                        p0.append(NoChord())
                    else:
                        p0.append(ChordSymbol(sho_cho))
                    prev_sho_cho = sho_cho
                # append note/rest
                p0.append(n)

        score_to_write.insert(0, p0)
        # self.show_text_in_stream(score_to_write)
        # score_to_write.show('text')

        # metadata
        score_to_write.insert(0, metadata.Metadata())
        filename = Path(input_filename)
        score_to_write.metadata.title = filename.with_suffix('')
        score_to_write.metadata.composer = 'VeeHarmGen ' + __version__ + '\n' + output_filename + '\n'

        # self.show_text_in_stream(score_to_write)
        # score_to_write.show('text')

        # write output stream
        score_to_write.write(fp=self.OUTPUT_PATH + output_filename)

        print('output =',self.OUTPUT_PATH + output_filename)
        pass


    def write_placeholder_chords(self, pitch_to_chord, output_filename, chord_choice, number):
        """
        Write melody with chords to output_filename mxl.
        Chords mapped using offsets in SongSectionValues.song_offset_placeholder_chords
        and pitch_to_chord dictionary.

        :param pitch_to_chord dictionary
        :param output_filename: e.g. my.mxl
        :param chord_choice
        :param number
        :return: void

        Given:
            SongSectionValues.song_offset_placeholder_chords e.g. =
            {0.0: '1000 0000 0000', 12.0: '0000 1100 0000', 24.0: '1000 0000 0001', 36.0: '1000 0000 0000'}
            pitch_to_chord e.g. =
            {'1000 0000 0000': {'C': 2, 'Am7': 1, 'Am': 1}, '0010 0000 0000': {'F': 2, 'G': 1}, '1010 0000 0001': {'G': 1}, '0000 1000 0000': {'C': 1, 'Am': 1}, '0000 1100 0000': {'F': 1}, '1000 0000 0001': {'G': 1}, '1010 1100 0000': {'C': 1}, '0010 1100 0000': {'G': 1}, '1010 1101 0000': {'C': 1}, '0000 0100 0100': {'F': 1}, '0010 1000 0000': {'G': 1}}

        next_chord_offset = first offset from song_offset_placeholder_chords
        next_pitch_class = first pitch_class from song_offset_placeholder_chords
        for each element
            if not note:
                copy to output stream
            else:
                if n.offset >= next_chord_offset:
                    sho_cho = get_chord_for_pitch_class(next_pitch_class, pitch_to_chord)
                    append sho_cho
                    next_chord_offset = get_next_chord_offset(next_chord_offset)
                    next_pitch_class = get_next_pitch_class(next_chord_offset)
                append note

        write output stream
        """

        print('write_placeholder_chords(self, pitch_to_chord, output_filename, chord_choice, number)', pitch_to_chord, output_filename, chord_choice, number)
        # input('Press Enter to continue...')
        # print('song_offset_placeholder_chords', SongSectionValues.song_offset_placeholder_chords)
        # print('pitch_to_chord', pitch_to_chord)

        score = stream.Score()
        p0 = stream.Part()
        p0.insert(0, self.the_instrument)

        prev_sho_cho = 'NC'

        # next_chord_offset = first offset from song_offset_placeholder_chords
        # next_pitch_class = first pitch_class from song_offset_placeholder_chords
        next_chord_offset, next_pitch_class = next(iter(SongSectionValues.song_offset_placeholder_chords.items()))
        print('next_chord_offset', next_chord_offset)
        print('next_pitch_class', next_pitch_class)

        last_chord_offset = list(SongSectionValues.song_offset_placeholder_chords)[-1]
        print('last_chord_offset', last_chord_offset)
        # input('Press Enter to continue...')

        # for each element
        for n in SongSectionValues.song_stream.flatten():
            # if not note:
            if type(n) != music21.note.Note and type(n) != music21.note.Rest:
                # copy all non-note types to output stream (unless instrument, ChordSymbol or TextBox)
                if issubclass(n.__class__, music21.instrument.Instrument) or \
                        issubclass(n.__class__, music21.harmony.ChordSymbol) or \
                        issubclass(n.__class__, music21.text.TextBox) :
                    # do not copy an Instrument or a chord
                    pass
                # if text expression and only one 1 section (dummy intro)
                elif issubclass(n.__class__, music21.expressions.TextExpression) and len(SongSectionValues.offset_section) == 1:
                    # print('len(SongSectionValues.offset_section)', len(SongSectionValues.offset_section))
                    pass
                else:
                    p0.append(n)
            # else is note or rest
            else:
                #         if n.offset >= next_chord_offset:
                if n.offset >= next_chord_offset:
                    print('n.offset >= next_chord_offset',  n.offset, next_chord_offset)
                    sho_cho = get_chord_for_pitch_class(next_pitch_class, pitch_to_chord, output_filename, chord_choice, number)
                    # append chord
                    if sho_cho == 'NC':
                        p0.append(NoChord())
                    else:
                        p0.append(ChordSymbol(sho_cho))
                    prev_sho_cho = sho_cho

                    if next_chord_offset != last_chord_offset:
                        chord_offset = None
                        temp = iter(SongSectionValues.song_offset_placeholder_chords)
                        curr_pitch_class = next_pitch_class
                        for k in temp:
                            if k == next_chord_offset:
                                next_chord_offset = next(temp, None)
                        # given key get value
                        next_pitch_class = SongSectionValues.song_offset_placeholder_chords[next_chord_offset]
                        print('the next_chord_offset', next_chord_offset)
                        print('the next_pitch_class', next_pitch_class)
                # append note/rest
                p0.append(n)

        # input('Press Enter to continue...')

        # write output stream
        # metadata
        score.insert(0, metadata.Metadata())
        filename = Path(output_filename)
        score.metadata.title = filename.with_suffix('')
        score.metadata.composer = 'VeeHarmGen ' + __version__ + '\n' + output_filename + '\n'

        score.insert(0, p0)

        # write output stream
        score.write(fp=self.OUTPUT_PATH + output_filename)

        print('output =',self.OUTPUT_PATH + output_filename)

        return None
    # end of SongSectionValues class

def has_section(a_song):
    """
    :param a_song: e.g. a song melody
    :return: True if a_stream has a section name
    """
    print('Looking for a section...')
    result = False

    # for each element in stream
    for n in a_song.flatten():
        if type(n) == music21.expressions.TextExpression:
            if is_section(n.content):
                print('has_section',n.content)
                result = True

    return result

def is_section(content):
    """
    content_is_section = False
    if content starts with section_name: content_is_section = True
    return content_is_section
    """
    section_name_matches = ['Intro', 'Verse', 'Prechorus', 'Chorus', 'Solo', 'Bridge', 'Outro',
                            'intro', 'verse', 'prechorus', 'chorus', 'solo', 'bridge', 'outro',
                            'INTRO', 'VERSE', 'PRECHORUS', 'CHORUS', 'SOLO', 'BRIDGE', 'OUTRO', 'preChorus']
    content_is_section = False
    # if content.startswith('intro',  'verse', 'prechorus', 'chorus', 'solo', 'bridge', 'outro'):
    if any(x in content for x in section_name_matches):
        content_is_section = True
    return content_is_section

def truncate_section(name):
    """
    given a long section name e.g. VERSE_1
    return short name e.g. verse
    """
    section_name = ['intro', 'verse', 'prechorus', 'chorus', 'solo', 'bridge', 'outro']
    # for each section_name
    #   if section_name is a case-insensitive match to the beginning of the string
    #       return section_name
    for sec in  section_name:
        if name.lower().startswith(sec):
            return sec

def short_chord(chord):
    """
    given a long chord name e.g. A minor or C major
    return short name e.g. A- or C
    """

    if chord.lower().endswith(' minor'):
        chord = chord.replace(' minor', 'm')

    if chord.lower().endswith(' major'):
        chord = chord.replace(' major', ' ')

    # add extra space to natural chords to pad to sharp or flat chords
    if chord[1] != '#' and chord[1] != 'b':
        chord = chord + ' '

    # workaround B- bug
    # if chord.lower().startswith('b'):
    #     print('found a B chord')

    if chord == 'B-  ' or chord == 'B-m ' :
        chord = 'Bm '


    return chord


def short_placeholder_chord(chord_in):
    """
    given a long chord name e.g. A minor or C major
    return short name e.g. A- or C
    """
    chord = str(chord_in)
    chord = chord.upper()
    if chord.endswith(' MINOR'):
        chord = chord.replace(' MINOR', 'm')

    if chord.endswith(' MAJOR'):
        chord = chord.replace(' MAJOR', '')

    # add extra space to natural chords to pad to sharp or flat chords
    # if chord[1] != '#' and chord[1] != 'b':
    #     chord = chord + ' '

    # workaround B- bug
    # if chord.startswith('b'):
    #     print('found a B chord')

    if chord == 'B-  ' or chord == 'B-m ' :
        chord = 'Bm '


    return chord

def chord_is_on_key(val):
    """
    :param val: the simple chord e.g. C or Am
    :return: True if Chord is on key
    """
    result = False
    # I don't like Bdim, so not "on key" as far as I'm concerned
    # if val == 'C' or val == 'Dm' or val == 'Em' or val == 'F' or val == 'G' or val == 'Am' or val == 'B' or val == 'Bm' or val == 'Bdim' :

    if val == 'C' or val == 'Dm' or val == 'Em' or val == 'F' or val == 'G' or val == 'Am':
        result = True
    return result

def force_chord_on_key(val_in):
    """
    :param val_in: the input simple chord e.g. C or Cm, Dm or D .. Bm
    :return: the output chord on key e.g. C, Dm, Em, F, G, Am or Bdim
    """
    result = 'NC'
    if val_in == 'C' or val_in == 'Cm':
        result = 'C'
    if val_in == 'D' or val_in == 'Dm':
        result = 'Dm'
    if val_in == 'E' or val_in == 'Em':
        result = 'Em'
    if val_in == 'F' or val_in == 'Fm':
        result = 'F'
    if val_in == 'G' or val_in == 'Gm':
        result = 'G'
    if val_in == 'Am' or val_in == 'A':
        result = 'Am'
    if val_in == 'B' or val_in == 'Bm' or val_in == 'Bdim':
        result = 'Bdim'

    return result


def force_B_chord_on_key(val_in):
    """
    :param val_in: the input simple chord e.g. B Bm
    :return: the output chord on key  Bdim
    """
    result = val_in
    if val_in == 'B' or val_in == 'Bm':
        result = 'Bdim'

    return result

def chord_is_major(val):

    """
    :param val: the simple chord e.g. C or Am
    :return: True if Chord is major
    """
    result = False
    if chord_is_on_key(val) and not val.endswith('m'):
        result = True
    return result

def chord_is_minor(val):

    """
    :param val: the simple chord e.g. C or Am
    :return: True if Chord is minor
    """
    result = False
    if chord_is_on_key(val) and val.endswith('m'):
        result = True
    return result


def get_seventh_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: seventh chord i.e. Cmaj7 or Dm7 or Em7 or Fmaj7 or G7 or Am7 or Bm7b5
    """
    result = 'NC'
    if val == 'C': result = 'Cmaj7'
    if val == 'Dm': result = 'Dm7'
    if val == 'Em': result = 'Em7'
    if val == 'F': result = 'Fmaj7'
    if val == 'G': result = 'G7'
    if val == 'Am': result = 'Am7'
    if val == 'Bm': result = 'Bm7b5'

    return result

def get_ninth_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: ninth chord i.e. CMaj9 Dm9 Em7b9 FMaj9 G9 Am9 Bm7b9b5
    """
    result = 'NC'
    if val == 'C': result = 'CMaj9'
    if val == 'Dm': result = 'Dm9'
    if val == 'Em': result = 'Em7b9'
    if val == 'F': result = 'FMaj9'
    if val == 'G': result = 'G9'
    if val == 'Am': result = 'Am9'
    if val == 'Bm': result = 'Bm7b9b5'

    return result

def get_eleventh_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: eleventh chord i.e. CMaj11 Dm11 Em11b9 FMaj9#11 G11 Am11 Bm11b9b5
    """
    result = 'NC'
    if val == 'C': result = 'CMaj11'
    if val == 'Dm': result = 'Dm11'
    if val == 'Em': result = 'Em11b9'
    if val == 'F': result = 'FMaj9#11'
    if val == 'G': result = 'G11'
    if val == 'Am': result = 'Am11'
    if val == 'Bm': result = 'Bm11b9b5'

    return result

def get_thirteenth_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: thirteenth chord i.e. CMaj13 Dm13 Em11b9b13 FMaj13#11 G13 Am11b13 Bm11b5b9b13
    """
    result = 'NC'
    if val == 'C': result = 'CMaj13'
    if val == 'Dm': result = 'Dm13'
    if val == 'Em': result = 'Em11b9b13'
    if val == 'F': result = 'FMaj13#11'
    if val == 'G': result = 'G13'
    if val == 'Am': result = 'Am11b13'
    if val == 'Bm': result = 'Bm11b5b9b13'

    return result


def get_suspended2_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: suspended chord, mostly sus2
    """
    result = 'NC'
    if val == 'C': result = 'Csus2'
    if val == 'Dm': result = 'Dsus2'
    if val == 'Em': result = 'Esus4'
    if val == 'F': result = 'Fsus2'
    if val == 'G': result = 'Gsus2'
    if val == 'Am': result = 'Asus2'
    if val == 'Bm' or val == 'Bdim': result = 'Bdim' #  should be Bsus4dim5 but get invalid literal for int() with base 10: 'sus4dim5'

    return result


def get_add2_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: add2 chord
    """
    result = 'NC'
    if val == 'C': result = 'Cadd2'
    if val == 'Dm': result = 'Dmadd2'
    if val == 'Em': result = 'Emadd2' # should be Emadd♭2 but get ChordStepModification('add', int(degree)), updatePitches=False) ValueError: invalid literal for int() with base 10: '♭2'. the hyphen is confusing w/ music21 flat notation gives musescore invaid xml file
    if val == 'F': result = 'Fadd2'
    if val == 'G': result = 'Gadd2'
    if val == 'Am': result = 'Amadd2'
    if val == 'Bm' or val == 'Bdim': result = 'Bdimadd2' # should be Bdimadd♭2, but get ValueError: invalid literal for int() with base 10: 'b2'

    return result


def get_sus4_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: suspended chord, mostly sus4
    """
    result = 'NC'
    if val == 'C': result = 'Csus4'
    if val == 'Dm': result = 'Dsus4'
    if val == 'Em': result = 'Esus4'
    if val == 'F': result = 'Fsus4'
    if val == 'G': result = 'Gsus4'
    if val == 'Am': result = 'Asus4'
    if val == 'Bm' or val == 'Bdim': result = 'Bsus4' #  should be Bsus4dim5 but get invalid literal for int() with base 10: 'sus4dim5'

    return result


def get_add4_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: add4 chord
    """
    result = 'NC'
    if val == 'C': result = 'Cadd4'
    if val == 'Dm': result = 'Dmadd4'
    if val == 'Em': result = 'Emadd4'
    if val == 'F': result = 'Fadd4' # should be Fadd#4, but ValueError: invalid literal for int() with base 10: '♯4' or '^#4' or 'F add #4'
    if val == 'G': result = 'Gadd4'
    if val == 'Am': result = 'Amadd4'
    if val == 'Bm' or val == 'Bdim': result = 'Bdimadd4'

    return result


def get_fifth_chord(val):
        """
        :param val: a simple chord e.g. C, Am etc
        :return: fifth (power) chord
        """
        # see music21.harmony.CHORD_TYPES for valid abbreviations or specify all alterations.
        # e.g. power

        result = 'NC'
        if val == 'C': result = 'Cpower'
        if val == 'Dm': result = 'Dpower'
        if val == 'Em': result = 'Epower'
        if val == 'F': result = 'Fpower'
        if val == 'G': result = 'Gpower'
        if val == 'Am': result = 'Apower'
        if val == 'Bm' or val == 'Bdim': result = 'Bpower'

        return result


def get_pedal_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: fifth (power) chord
    """
    # see music21.harmony.CHORD_TYPES for valid abbreviations or specify all alterations.
    # e.g. pedal

    result = 'NC'
    if val == 'C': result = 'Cpedal'
    if val == 'Dm': result = 'Dpedal'
    if val == 'Em': result = 'Epedal'
    if val == 'F': result = 'Fpedal'
    if val == 'G': result = 'Gpedal'
    if val == 'Am': result = 'Apedal'
    if val == 'Bm' or val == 'Bdim': result = 'Bpedal'

    return result


def get_sixth_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: sixth chord
    """

    result = 'NC'
    if val == 'C': result = 'C6'
    if val == 'Dm': result = 'Dm6'
    if val == 'Em': result = 'Em6'
    if val == 'F': result = 'F6'
    if val == 'G': result = 'G6'
    if val == 'Am': result = 'Am6'
    if val == 'Bm' or val == 'Bdim': result = 'Bdim'

    return result

def get_addsixth_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: addsixth chord
    """
    # print('get_addsixth_chord', val)
    result = 'NC'
    if val == 'C': result = 'Cadd6'
    if val == 'Dm': result = 'Dmadd6'
    if val == 'Em': result = 'Emadd6'  # 'Emaddb6' ValueError: invalid literal for int() with base 10: 'b6'
    if val == 'F': result = 'Fadd6'
    if val == 'G': result = 'Gadd6'
    if val == 'Am': result = 'Amadd6'  # 'Amaddb6' ValueError: invalid literal for int() with base 10: 'b6'
    if val == 'Bm' or val == 'Bdim': result = 'Bdimadd6' # 'Bmaddb6' ValueError: invalid literal for int() with base 10: 'b6'

    return result


def get_sus47_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: suspended-fourth-seventh chord # did not produce any chords in MuseScore
    """
    result = 'NC'
    if val == 'C': result = 'C7sus'
    if val == 'Dm': result = 'D7sus'
    if val == 'Em': result = 'E7sus'
    if val == 'F': result = 'F7sus'
    if val == 'G': result = 'G7sus'
    if val == 'Am': result = 'A7sus'
    if val == 'Bm' or val == 'Bdim': result = 'B7susdim5'


def chord_is_interval_range_from_prev(val, prev_value, int_low, int_high):
    """
    :param val: a simple chord e.g. C, Am etc
    :param prev_val: the previous chord
    :param int_low: the lowest interval in semitones
    :param int_high: the highest interval in semitones
    :return: True if the val is a fouth of fifth interval from prev_val
    if prev_val = 'NC' then do not compare interval just accept
    else compare interval
    """
    result = False
    if prev_value == 'NC' or val == 'NC':
        result = True
    else:
        h = harmony.ChordSymbol(val)
        prev_h = harmony.ChordSymbol(prev_value)

        n = music21.note.Note()
        n.nameWithOctave = str(h.root())

        note_prev = music21.note.Note()
        note_prev.nameWithOctave = str(prev_h.root())

        aInterval = interval.Interval(note_prev, n)
        AIntSemi = abs(aInterval.semitones)
        # chord in range if within supplied interval or same as previous chord
        if (AIntSemi >= int_low and AIntSemi <= int_high) or AIntSemi == 0:
            result = True

    return result


def get_descending_bass_tetra_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: descending bass chord e.g. C/B
    """
    if val == 'NC':
        result = 'NC'
    else:
        result = val + '/' + SongSectionValues.last_bass
        if SongSectionValues.last_bass == 'C': SongSectionValues.last_bass = 'B'
        elif SongSectionValues.last_bass == 'B': SongSectionValues.last_bass = 'A'
        elif SongSectionValues.last_bass == 'A': SongSectionValues.last_bass = 'G'
        elif SongSectionValues.last_bass == 'G': SongSectionValues.last_bass = 'C'

    return result

def get_descending_chromatic_bass_tetra_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: descending bass chord e.g. C/B
    """
    if val == 'NC':
        result = 'NC'
    else:
        result = val + '/' + SongSectionValues.last_bass
        if SongSectionValues.last_bass == 'C': SongSectionValues.last_bass = 'B'
        elif SongSectionValues.last_bass == 'B': SongSectionValues.last_bass = 'A#'
        elif SongSectionValues.last_bass == 'A#': SongSectionValues.last_bass = 'A'
        elif SongSectionValues.last_bass == 'A': SongSectionValues.last_bass = 'C'

    return result


def get_descending_bass_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: descending bass chord e.g. C/B
    """
    if val == 'NC':
        result = 'NC'
    else:
        result = val + '/' + SongSectionValues.last_bass
        if SongSectionValues.last_bass == 'C': SongSectionValues.last_bass = 'B'
        elif SongSectionValues.last_bass == 'B': SongSectionValues.last_bass = 'A'
        elif SongSectionValues.last_bass == 'A': SongSectionValues.last_bass = 'G'
        elif SongSectionValues.last_bass == 'G': SongSectionValues.last_bass = 'F'
        elif SongSectionValues.last_bass == 'F': SongSectionValues.last_bass = 'E'
        elif SongSectionValues.last_bass == 'E': SongSectionValues.last_bass = 'D'
        elif SongSectionValues.last_bass == 'D': SongSectionValues.last_bass = 'C'

    return result


def get_descending_chromatic_bass_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: descending bass chord e.g. C/B
    """
    if val == 'NC':
        result = 'NC'
    else:
        result = val + '/' + SongSectionValues.last_bass
        if SongSectionValues.last_bass == 'C': SongSectionValues.last_bass = 'B'
        elif SongSectionValues.last_bass == 'B': SongSectionValues.last_bass = 'A#'
        elif SongSectionValues.last_bass == 'A#': SongSectionValues.last_bass = 'A'
        elif SongSectionValues.last_bass == 'A': SongSectionValues.last_bass = 'G#'
        elif SongSectionValues.last_bass == 'G#': SongSectionValues.last_bass = 'G'
        elif SongSectionValues.last_bass == 'G': SongSectionValues.last_bass = 'F#'
        elif SongSectionValues.last_bass == 'F#': SongSectionValues.last_bass = 'F'
        elif SongSectionValues.last_bass == 'F': SongSectionValues.last_bass = 'E'
        elif SongSectionValues.last_bass == 'E': SongSectionValues.last_bass = 'D#'
        elif SongSectionValues.last_bass == 'D#': SongSectionValues.last_bass = 'D'
        elif SongSectionValues.last_bass == 'D': SongSectionValues.last_bass = 'C#'
        elif SongSectionValues.last_bass == 'C#': SongSectionValues.last_bass = 'C'
    return result

def get_ascending_bass_tetra_1_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: bass chord e.g. C/B
    """
    if val == 'NC':
        result = 'NC'
    else:
        result = val + '/' + SongSectionValues.last_bass
        if SongSectionValues.last_bass == 'C': SongSectionValues.last_bass = 'D'
        elif SongSectionValues.last_bass == 'D': SongSectionValues.last_bass = 'E'
        elif SongSectionValues.last_bass == 'E': SongSectionValues.last_bass = 'F'
        elif SongSectionValues.last_bass == 'F': SongSectionValues.last_bass = 'C'

    return result


def get_ascending_bass_tetra_2_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: bass chord e.g. C/B
    """
    if val == 'NC':
        result = 'NC'
    else:
        result = val + '/' + SongSectionValues.last_bass
        if SongSectionValues.last_bass == 'C': SongSectionValues.last_bass = 'D'
        elif SongSectionValues.last_bass == 'D': SongSectionValues.last_bass = 'F'
        elif SongSectionValues.last_bass == 'F': SongSectionValues.last_bass = 'G'
        elif SongSectionValues.last_bass == 'G': SongSectionValues.last_bass = 'C'

    return result


def get_ascending_bass_tetra_3_chord(val):
    """
    :param val: a simple chord e.g. C, Am etc
    :return: bass chord e.g. C/B
    """
    if val == 'NC':
        result = 'NC'
    else:
        result = val + '/' + SongSectionValues.last_bass
        if SongSectionValues.last_bass == 'C': SongSectionValues.last_bass = 'E'
        elif SongSectionValues.last_bass == 'E': SongSectionValues.last_bass = 'F'
        elif SongSectionValues.last_bass == 'F': SongSectionValues.last_bass = 'G'
        elif SongSectionValues.last_bass == 'G': SongSectionValues.last_bass = 'C'

    return result

def get_chord_output(chord_output, key, key_finder_offset_chords, prev_value):
    """
    :param chord_output: Chord_Output e.g. ON_KEY, MAJOR, MINOR etc
    :param key: the offset to use
    :param key_finder_offset_chords: list of offset_chord dicts for the different key finders
    :param prev_value : the previous chord value
    :return: the chord value e.g. 'Dm'
    """

    value = 'NC' # default is No Chord

    if chord_output == Chord_Output.ON_KEY_MOST:
        current_offset_chords = {}  # dictionary to hold the possible chords for the current offset
        key_inc = 1.0 # to avoid duplicate keys add the key_inc
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in key_finder_offset_chords:
            # construct a dict of the possible chords
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                val = force_B_chord_on_key(val)
                current_offset_chords[(key + key_inc)] = val
                key_inc = key_inc + 1
        # print('ON_KEY_MOST current_offset_chords',current_offset_chords)
        if current_offset_chords != {}:
            # find-most-frequent-value-in-python-dictionary-value-with-maximum-count
            value, count = Counter(current_offset_chords.values()).most_common(1)[0]
            # print('most-frequent-value, maximum-count ', value, count)
        if value == 'NC':
            # search for most-frequent off-key chord
            current_offset_chords = {}  # dictionary to hold the possible chords for the current offset
            key_inc = 1.0  # to avoid duplicate keys add the key_inc
            # for each key finder (A, B, K, S, T)
            for key_finder_offset_chord in key_finder_offset_chords:
                # construct a dict of the possible chords
                val = key_finder_offset_chord.get(key)
                current_offset_chords[(key + key_inc)] = val
                key_inc = key_inc + 1
            # print('OFF_KEY_MOST current_offset_chords',current_offset_chords)
            if current_offset_chords != {}:
                # find-most-frequent-value-in-python-dictionary-value-with-maximum-count
                value, count = Counter(current_offset_chords.values()).most_common(1)[0]
                # print('most-frequent-value, maximum-count ', value, count)

    if chord_output == Chord_Output.ON_KEY_LEAST:
        current_offset_chords = {}  # dictionary to hold the possible chords for the current offset
        key_inc = 1.0 # to avoid duplicate keys add the key_inc
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in key_finder_offset_chords:
            # construct a dict of the possible chords
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                val = force_B_chord_on_key(val)
                current_offset_chords[(key + key_inc)] = val
                key_inc = key_inc + 1
        # print('ON_KEY_LEAST current_offset_chords',current_offset_chords)
        if current_offset_chords != {}:
            # find-least-frequent-value-in-python-dictionary
            # most_common without any argument returns all the entries, ordered from most common to least.
            # So to find the least common, just start looking at it from the other end.
            value = Counter(current_offset_chords.values()).most_common()[-1][0]
            # print('least-frequent-value', value)
        if value == 'NC':
            current_offset_chords = {}  # dictionary to hold the possible chords for the current offset
            key_inc = 1.0  # to avoid duplicate keys add the key_inc
            # for each key finder (A, B, K, S, T)
            for key_finder_offset_chord in key_finder_offset_chords:
                # construct a dict of the possible chords
                val = key_finder_offset_chord.get(key)
                current_offset_chords[(key + key_inc)] = val
                key_inc = key_inc + 1
            # print('OFF_KEY_LEAST current_offset_chords',current_offset_chords)
            if current_offset_chords != {}:
                # find-least-frequent-value-in-python-dictionary
                # So to find the least common, just start looking at it from the other end.
                value = Counter(current_offset_chords.values()).most_common()[-1][0]
                # print('least-frequent-value', value)

    if chord_output == Chord_Output.ON_KEY_LAST:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = force_B_chord_on_key(val)
                break
        if value == 'NC':
            # get an offset_chord which is not on key
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = val
                break

    if chord_output == Chord_Output.ON_KEY_FIRST:
        for key_finder_offset_chord in key_finder_offset_chords:
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = force_B_chord_on_key(val)
                break
        if value == 'NC':
            for key_finder_offset_chord in key_finder_offset_chords:
                val = key_finder_offset_chord.get(key)
                value = val
                break


    if chord_output == Chord_Output.PEDAL:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_pedal_chord(val)
                break
        if value == 'NC':
            # get an offset_chord which is not on key
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = val
                break


    if chord_output == Chord_Output.SUSPENDED2:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_suspended2_chord(val)
                break
        if value == 'NC':
            # get an offset_chord which is not on key
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = val
                break


    if chord_output == Chord_Output.ADD2:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_add2_chord(val)
                break
        if value == 'NC':
            # get an offset_chord which is not on key
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = val
                break


    if chord_output == Chord_Output.SUSPENDED4:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_sus4_chord(val)
                break
        if value == 'NC':
            # get an offset_chord which is not on key
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = val
                break


    if chord_output == Chord_Output.ADD4:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_add4_chord(val)
                break
        if value == 'NC':
            # get an offset_chord which is not on key
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = val
                break

    if chord_output == Chord_Output.FIFTH:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_fifth_chord(val)
                break
        if value == 'NC':
            # get an offset_chord which is not on key
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = val
                break

    if chord_output == Chord_Output.SIXTH:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_sixth_chord(val)
                break
        if value == 'NC':
            # get an offset_chord which is not on key
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = val
                break

    if chord_output == Chord_Output.ADDSIXTH:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_addsixth_chord(val)
                break
        if value == 'NC':
            # get an offset_chord which is not on key
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = val
                break

    if chord_output == Chord_Output.SEVENTH:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_seventh_chord(val)
                break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = val
                break

    if chord_output == Chord_Output.NINTH:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_ninth_chord(val)
                break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                value = key_finder_offset_chord.get(key)
                break

    if chord_output == Chord_Output.ELEVENTH:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_eleventh_chord(val)
                break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                value = key_finder_offset_chord.get(key)
                break

    if chord_output == Chord_Output.THIRTEENTH:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_thirteenth_chord(val)
                break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                value = key_finder_offset_chord.get(key)
                break

    if chord_output == Chord_Output.MAJOR:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is MAJOR key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_major(val):
                value = val
                break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                if not val.endswith('m'):
                    value = val
                    break

    if chord_output == Chord_Output.MINOR:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is MINOR key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_minor(val):
                value = val
                break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                if val.endswith('m'):
                    value = val
                    break

    if chord_output == Chord_Output.NEXT_INTERVAL_SECOND_OR_THIRD:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                if chord_is_interval_range_from_prev(val, prev_value, 1, 4):
                    value = val
                    break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                if chord_is_interval_range_from_prev(val, prev_value, 1, 4):
                    value = val
                    break


    if chord_output == Chord_Output.NEXT_INTERVAL_FOURTH_OR_FIFTH:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                if chord_is_interval_range_from_prev(val, prev_value, 5, 7):
                    value = val
                    break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                if chord_is_interval_range_from_prev(val, prev_value, 5, 7):
                    value = val
                    break


    if chord_output == Chord_Output.NEXT_INTERVAL_SIXTH_OR_SEVENTH:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                if chord_is_interval_range_from_prev(val, prev_value, 8, 11):
                    value = val
                    break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                if chord_is_interval_range_from_prev(val, prev_value, 8, 11):
                    value = val
                    break


    if chord_output == Chord_Output.DESCENDING_BASS_TETRA:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_descending_bass_tetra_chord(val)
                break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = get_descending_bass_tetra_chord(val)
                break


    if chord_output == Chord_Output.DESCENDING_CHROMATIC_BASS_TETRA:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_descending_chromatic_bass_tetra_chord(val)
                break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = get_descending_chromatic_bass_tetra_chord(val)
                break

    if chord_output == Chord_Output.DESCENDING_BASS:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_descending_bass_chord(val)
                break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = get_descending_bass_chord(val)
                break

    if chord_output == Chord_Output.DESCENDING_CHROMATIC_BASS:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_descending_chromatic_bass_chord(val)
                break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = get_descending_chromatic_bass_chord(val)
                break


    if chord_output == Chord_Output.ASCENDING_BASS_TETRA_1:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_ascending_bass_tetra_1_chord(val)
                break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = get_ascending_bass_tetra_1_chord(val)
                break

    if chord_output == Chord_Output.ASCENDING_BASS_TETRA_2:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_ascending_bass_tetra_2_chord(val)
                break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = get_ascending_bass_tetra_2_chord(val)
                break

    if chord_output == Chord_Output.ASCENDING_BASS_TETRA_3:
        # for each key finder (A, B, K, S, T)
        for key_finder_offset_chord in reversed(key_finder_offset_chords):
            # if offset_chord(key_finder, element) is on key use value
            val = key_finder_offset_chord.get(key)
            if chord_is_on_key(val):
                value = get_ascending_bass_tetra_3_chord(val)
                break
        if value == 'NC':
            for key_finder_offset_chord in reversed(key_finder_offset_chords):
                val = key_finder_offset_chord.get(key)
                value = get_ascending_bass_tetra_3_chord(val)
                break

    return value

def get_offset_chord(chord_output, harmonic_rhythm):
    """
    :param chord_output: Chord_Output e.g. ON_KEY, MAJOR, MINOR etc
    :param harmonic_rhythm: Harmonic_Rhythm e.g. BEAT1, BEAT2, BAR1 etc
    :return: offset_chord: the dictionary of offsets and chords for the input chord_output and harmonic_rhythm
    """
    # print('get_offset_chord: chord_output.name, harmonic_rhythm.name =', chord_output.name, harmonic_rhythm.name )

    # for each element in the first offset_chord dictionary for the requested harmonic_rhythm
    # get the requested harmonic rhythm guide
    if harmonic_rhythm == Harmonic_Rhythm.BEAT1:
        guide_offset_chord = SongSectionValues.song_offset_chord_1_beat
        key_finder_offset_chords = SongSectionValues.key_finder_offset_chords_1_beat
    if harmonic_rhythm == Harmonic_Rhythm.BEAT2:
        guide_offset_chord = SongSectionValues.song_offset_chord_2_beat
        key_finder_offset_chords = SongSectionValues.key_finder_offset_chords_2_beat
    if harmonic_rhythm == Harmonic_Rhythm.BAR1:
        guide_offset_chord = SongSectionValues.song_offset_chord_1_bar
        key_finder_offset_chords = SongSectionValues.key_finder_offset_chords_1_bar
    if harmonic_rhythm == Harmonic_Rhythm.BAR2:
        guide_offset_chord = SongSectionValues.song_offset_chord_2_bar
        key_finder_offset_chords = SongSectionValues.key_finder_offset_chords_2_bar
    if harmonic_rhythm == Harmonic_Rhythm.BAR4:
        guide_offset_chord = SongSectionValues.song_offset_chord_4_bar
        key_finder_offset_chords = SongSectionValues.key_finder_offset_chords_4_bar

    # construct the new offset_chord_dictionary for the requested chord_output style
    new_offset_chord = {}
    prev_value = 'NC'
    for key, value in sorted(guide_offset_chord.items()):
        new_value = get_chord_output(chord_output, key, key_finder_offset_chords, prev_value)
        new_offset_chord[key] = new_value
        prev_value = new_value

    return new_offset_chord



def add_TextExpression(input_song):
    """
    :param input_song:
    :return: output_song
    """
    first_note = True
    output_song = stream.Score()
    p0 = stream.Part()

    for n in input_song.flatten():
        # if not note:
        if type(n) != music21.note.Note and type(n) != music21.note.Rest:
                p0.append(n)
        # else is note or rest
        else:
            if first_note == True:
                # n_text = music21.expressions.TextExpression
                # # add the section name text to the score.
                te = expressions.TextExpression('intro')
                # # place TextExpression above the stave
                te.placement = 'above'
                p0.append(te)
                # n.content = 'intro'
                first_note = False
            # append note/rest
            p0.append(n)

    output_song.insert(0, p0)
    return output_song

def get_offset_section(input_song):
    """
    :param input_song:
    :return: offset_section dictionary to hold offset to section mapping e.g. {0.0: 'intro 1'}
    """
    print('get_offset_section(input_song)', input_song)

    offset_section = {}
    the_offset = 0.0

    for n in input_song.flatten():
        if type(n) == music21.expressions.TextExpression:
            if is_section(n.content):
                # print('the_offset, TextExpression =', the_offset, n.content)
                offset_section[the_offset] = n.content
        # if note or rest then set the_offset
        if type(n) == music21.note.Note or type(n) == music21.note.Rest:
                the_offset = n.offset + n.duration.quarterLength

    print('offset_section', offset_section)

    return offset_section

def normalise_song(input_song, input_filename):
    """
    normalise means: set instrument to piano, set key signature to C / Am
    :param input_song:
    :return: output_song
    """
    output_song = stream.Score()

    # metadata
    # output_song.insert(0, metadata.Metadata())
    # filename = Path(input_filename)
    # output_song.metadata.title = filename.with_suffix('')
    # output_song.metadata.composer = 'VeeHarmGen ' + __version__ + '\n' + input_filename + '\n'

    output_song.append(key.Key('C'))

    p0 = stream.Part()
    the_instrument = music21.instrument.Instrument(instrumentName='Piano')
    p0.insert(0, the_instrument)

    # for each element
    for n in input_song.flatten():
        # if not note:
        if type(n) != music21.note.Note and type(n) != music21.note.Rest:
            # copy to output stream unless instrument
            if issubclass(n.__class__, music21.instrument.Instrument):
                # do not copy an Instrument
                pass
            else:
                if type(n) != music21.key.KeySignature:
                    p0.append(n)
        # else is note or rest
        else:
            # append note/rest
            p0.append(n)

    output_song.insert(0, p0)
    return output_song


def get_accidental_count(a_song):
    """
    :param a_song: stream
    :return: acc_count: number of accidentals in the stream
    """
    acc_count = 0
    acc_disp_status_count = 0

    a_song.makeAccidentals(inPlace=True)

    for n in a_song.flatten():
        # if note update acc_count
        if type(n) == music21.note.Note:
            if n.pitch.accidental != None:
                acc_count = acc_count + 1
                if n.pitch.accidental.displayStatus == True:
                    acc_disp_status_count = acc_disp_status_count + 1

    # print ('acc_count, acc_disp_status_count', acc_count, acc_disp_status_count)
    return acc_count


def get_key_signature(a_stream):
    """
    :param a_stream: a stream
    :return: the first key signature in the stream
    """
    # print('get_key_signature()')
    first_KS = None
    # for n in a_stream.flatten():
    for n in a_stream:
        if type(n) == music21.key.KeySignature:
            # print('music21.key.KeySignature', song.tonic.name, song.mode)
            print('music21.key.KeySignature', a_stream.tonic.name, a_stream.mode)

            # print('music21.key.KeySignature', n)
            first = True
            for sKS in a_stream.flatten().getElementsByClass('KeySignature'):
                if first:
                    a_stream.KeySignature = sKS
                    # first_KS = sKS
                    first_KS = key.KeySignature(a_stream.KeySignature.sharps)
                    # kd = key.Key('D', 'minor')
                    print('First KeySignature:', a_stream.KeySignature,'.sharps:', a_stream.KeySignature.sharps)  # e.g. <music21.key.KeySignature of 1 flat>
                    print('.getScale(major):',
                          a_stream.KeySignature.getScale('major'))  # e.g. <music21.scale.MajorScale F major>
                    major_scale_string = sKS.getScale('major')
                    print('major_scale_string',major_scale_string)
                    first = False
                else:
                    print('other KeySignature:', sKS)
                    pass
    if first_KS == None:
        first_KS = key.KeySignature(0)
    return first_KS


def get_first_time_sig(a_stream):
    """
    :param a_stream: of music
    :return: the first time signature
    """
    # may have to get first part
    # myPart[music21.meter.TimeSignature][0]

    return a_stream[music21.meter.TimeSignature][0]

    pass


def get_first_key_signature(a_stream):
    """
    :param a_stream:
    :return: first key signature or if None return a key.KeySignature with zero sharps (C)
    """
    ks = key.KeySignature(0)
    try:
        ks = a_stream[music21.key.KeySignature][0]
    except IndexError as error:
        ks = key.KeySignature(0)

    return ks


def get_first_instrument(a_stream):
    """
    :param a_stream:
    :return: the first instrument in the stream
    """
    first_inst = None
    # for each element
    for n in a_stream.flatten():
        # if not note:
        if type(n) != music21.note.Note and type(n) != music21.note.Rest:
            if issubclass(n.__class__, music21.instrument.Instrument):
                if first_inst == None:
                    first_inst = n
                else:
                    print('other inst',n)

    return first_inst




def get_transpose_information(stream_title, a_stream):
    """
    print key sig , instrument, # accidentals,
    time sig, first/last note,
    analyze key, interval to Transpose Chromatically to key of C Major
    :param stream_title:
    :param a_stream:
    :return: transpose interval
    """
    print('')
    print('--- key information for', stream_title,' ----------------------------------------------------------------')
    # copy stream
    stream_copy = copy.deepcopy(a_stream)
    first_key_sig = get_first_key_signature(stream_copy)
    print('first key signature',first_key_sig)
    print([str(p) for p in first_key_sig.alteredPitches])
    print('key (mode=major)', first_key_sig.asKey())
    print('key (mode=minor)', first_key_sig.asKey(mode='minor'))
    accidental_count = get_accidental_count(stream_copy)
    print('accidental_count',accidental_count)

    print('')
    first_time_sig = get_first_time_sig(stream_copy)
    print('first time sig',first_time_sig)
    first_inst = get_first_instrument(stream_copy)
    print('first instrument',first_inst)
    first_note = get_first_note(stream_copy)
    print('first note',first_note)
    last_note = get_last_note(stream_copy)
    print('last note',last_note)

    print('')
    k = stream_copy.analyze('key')
    print('analyzed key & mode', k)

    # if minor find interval to A
    if k.mode == 'minor':
        i = interval.Interval(k.tonic, pitch.Pitch('A'))
    else:  # song is major, find interval to C
        i = interval.Interval(k.tonic, pitch.Pitch('C'))

    print('interval to C major/A minor from analysed key', i)

    print('--- end of key information for', stream_title,' ---------------------------------------------------------')
    return i


# def normalise_instrument_song(input_song):
#     """
#     normalise instrument means: set instrument to piano
#     :param input_song:
#     :return: output_song
#     """
#     output_song = stream.Score()
#
#     p0 = stream.Part()
#     the_instrument = music21.instrument.Instrument(instrumentName='Piano')
#     p0.insert(0, the_instrument)
#
#     # for each element
#     for n in input_song.flatten():
#         # if not note:
#         if type(n) != music21.note.Note and type(n) != music21.note.Rest:
#             # copy to output stream unless instrument
#             if issubclass(n.__class__, music21.instrument.Instrument):
#                 # do not copy an Instrument
#                 pass
#             else:
#                 # if type(n) != music21.key.KeySignature:
#                 p0.append(n)
#         # else is note or rest
#         else:
#             # append note/rest
#             p0.append(n)
#
#     output_song.insert(0, p0)
#     return output_song

def generate_from_placeholder_chords(a_song, song_key, instrument, mxlfile_basename, chord_choice, number, style ):
    """
    given a_song with a melody and placeholder chords,
    populate song_offset_placeholder_chords with offset and pitch classes in melody key e.g.
    {3.0: '1000 0000 0000', 4.0: '1000 0000 0000', 5.0: '0010 0000 0000', .... etc

    for each style, generate chords in placeholders and
    write to the output folder
    :param a_song:
    :param song_key:
    :param instrument:
    :param mxlfile_basename:
    :param chord_choice:
    :param number:
    """
    print('generate_from_placeholder_chords', a_song, song_key, instrument, mxlfile_basename,  chord_choice, number, style)
    # input('Press Enter to continue...')

    found_time_signature = False
    # first_section_found = False
    # first_note_of_section = True
    first_TimeSig = True
    songTimeSig = None

    song_section_values = SongSectionValues(song_key, a_song)
    # song_section_values.set_analyze_choice(analysis_choice)
    analysis_choice = song_section_values.get_analyze_choice()

    song_section_values.set_instrument(instrument)
    print('song_section_values.analyze_choice', song_section_values.analyze_choice)

    # before calling print_placeholder_chords populate stream1 with just notes and rests

    first_note_of_section = True
    first_TimeSig = True

    # for each element in stream
    for n in song_section_values.song_stream.flatten():
        if type(n) == music21.meter.TimeSignature:
            if first_TimeSig:
                song_section_values.set_time_sig(n)
                first_TimeSig = False
        # if note: update song_section_values
        if type(n) == music21.note.Note:
            # if type(n) != music21.note.Rest:
            song_section_values.update(n, first_note_of_section)
            if first_note_of_section == True: first_note_of_section = False

        if type(n) == music21.note.Rest:
            song_section_values.update_rest(n)

    song_section_values.print_placeholder_chords()

    # at end of song strip final comma and add }
    SongSectionValues.song_offset_placeholder_chords = remove_suffix(SongSectionValues.song_offset_placeholder_chords, ',') + '}'

    # convert string to dictionary using ast.literal_eval() method
    # ast.literal_eval: Safely evaluate an expression node or a string containing a Python literal or container display.
    # The string or node provided may only consist of the following Python literal structures:
    # strings, bytes, numbers, tuples, lists, dicts, sets, booleans, None, bytes and sets.
    try:
        SongSectionValues.song_offset_placeholder_chords = ast.literal_eval(
            SongSectionValues.song_offset_placeholder_chords)
    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print('exit: Error ast.literal_eval song_offset_placeholder_chords',
              SongSectionValues.song_offset_placeholder_chords)
        sys.exit()

    # print('after strip final comma and add } and convert to dict')
    # print('SongSectionValues.song_offset_placeholder_chords', SongSectionValues.song_offset_placeholder_chords)

    # for each style, generate chords in placeholders and write to the output folder

    # for each style in input\style\pitch_to_chord
    # for each style in input\style

    pitch_to_chord_files = [f for f in os.listdir(INPUT_STYLE_PATH) if f.endswith('.json')]

    print('pitch_to_chord_files in', INPUT_STYLE_PATH,  pitch_to_chord_files)

    if pitch_to_chord_files == []:
        print('exit: Error no pitch_to_chord_files in', INPUT_STYLE_PATH)
        sys.exit()

    # dt = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S_%f")
    dt = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
    print('')

    for pitch_to_chord_file in pitch_to_chord_files:
        if style in pitch_to_chord_file:
            # print('pitch_to_chord_file ',pitch_to_chord_file )
            input_pitch_to_chord_fully_qualified = INPUT_STYLE_PATH + pitch_to_chord_file
            print('Processing', input_pitch_to_chord_fully_qualified)
            output_filename = os.path.splitext(mxlfile_basename)[0]

            # output_filename = output_filename + '-' + str(
            #         os.path.splitext(pitch_to_chord_file)[0]) + '-R' + str(rank) + '-' + dt + '.mxl'
            # remove -_-ptc from output filename
            output_filename = output_filename + '-' + str(
                    os.path.splitext(pitch_to_chord_file)[0]).replace('-_-ptc', '') + '-' + str(chord_choice) + '-' + str(number) + '.mxl'
            print('output_filename', output_filename)
            # input('Press Enter to continue...')
            pitch_to_chord = load_json(input_pitch_to_chord_fully_qualified)
            # print('pitch_to_chord', pitch_to_chord)
            song_section_values.write_placeholder_chords(pitch_to_chord, output_filename, chord_choice, number)
            print('')
    return None


def main():
    """
    parse command line arguments
    read mxl
    normalise stream
    write normalised stream

    for each stream element
        if time sig: read time sig
        if text: read section name
            if not first section:
                song_section_values.print()
            init SongSectionValues
        if note: read note: song_section_values.update()
    song_section_values.print()
    """

    # Specify command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mxlfile',
                        help='MusicXML input file with the extension .mxl (compressed) relative to current working directory.  '
                            'Example 1: input/music/music.mxl (without placeholder chords, outputs files with placeholder chords at offsets beat1 beat2 bar1 bar2 bar4)'
                            '   '
                            'Example 2: input/music/placeholder_chords/music.mxl (with placeholder chords, outputs a file with chords in placeholders for each input/style).  '
                            'To manually add placeholders for where chords are desired, in MuseScore, to create a Chord Symbol: select start note and then use the menu option'
                            'Add > Text > Chord Symbol (shortcut Ctrl+K) e.g. C or the song key.',
                        # default='input/music/music.mxl',
                        default='input/music/placeholder_chords/music.mxl',
                        type=str)

    # parser.add_argument('-a','--analyze',
    #                     help='analyze default is Krumhansl, alternatively enter Aarden or Bellman or Krumhansl or Simple or Temperley, '
    #                         ' see https://web.mit.edu/music21/doc/moduleReference/moduleAnalysisDiscrete.html',
    #                     default='Krumhansl',
    #                     type=str)

    # BooleanOptionalAction needs Python 3.9
    # parser.add_argument('-d','--demo',
    #                    help='demonstrate some different commonly used chords and harmonic rhythms.',
    #                    default=False,
    #                    action=argparse.BooleanOptionalAction)

    parser.add_argument('-c','--chord_choice', 
                        help='chord_choice may be rank which uses a nearest-rank ordered list of possible chords '
                            'or nth_outcome where number is the number of outcomes away from the most popular outcome, ',
                        default= 'rank',
                        type=Chord_Choice, choices=list(Chord_Choice))  
                        
    parser.add_argument('-n','--number',
                        help='number used with the chord_choice e.g. '
                            'if chord_choice is rank then number 1 is least frequent and 100 is the most frequent in the nearest-rank ordered list of possible chords, '
                            'if chord_choice is nth_outcome then number is outcomes away from the most popular outcome. ',
                        default= 100,
                        type=int, 
                        choices=range(0, 101))                          
                    
    parser.add_argument('-d','--demo',
                        help='demonstrate some different commonly used chords and harmonic rhythms.',
                        default=False)
    #                    action=argparse.BooleanOptionalAction)
                        
    parser.add_argument('-i','--instrument',
                        help='medlody instrument default is Piano, alternatively enter one of: '
                            'Accordion, "Acoustic Bass", "Acoustic Guitar", Alto, "Alto Saxophone", Banjo, Baritone, "Baritone Saxophone", Bass, Bassoon, "Bass Trombone", Brass, Celesta, Clarinet, Clavichord, Contrabass, Contrabassoon, '
                            'Dulcimer, "Electric Bass", "Electric Guitar", "Electric Piano", "English Horn", Flute, Glockenspiel, Guitar, Harmonica, Harp, Kalimba, Koto, Lute, Marimba, Oboe, Ocarina, "Pan Flute", Piccolo, Recorder, "Reed Organ", Saxophone, '
                            'Shamisen, Sitar, Soprano, "Soprano Saxophone", Tenor, "Tenor Saxophone", Timpani, Trombone, Trumpet, Tuba, "Tubular Bells", Ukulele, Vibraphone, Violin, Violoncello, Voice, Xylophone',
                        default='Piano',
                        type=str)                               
    
    parser.add_argument('-o','--offsets',
                        nargs=5,
                        metavar=('beat1', 'beat2', 'bar1', 'bar2', 'bar4'),
                        help='override the offset increments for beat1, beat2, bar1, bar2, bar4 e.g. -o 0.5 1.0 1.5 2.0 3.0',
                        default=None,
                        type=float)

    parser.add_argument('-s','--style',
                        help='style filter string on files in input/style directory e.g. -s jazz only includes style names containing the string jazz',
                        default='ptc',
                        type=str)

    parser.add_argument('-t','--transpose',
                        help='transpose input file down or up t semitones (to override default "analyze" transpose to C / a minor)',
                        default= None,
                        type=int, choices=range(-12, 13))

    parser.add_argument('-v','--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))


                      
                        
    # Parse command line arguments.
    args = parser.parse_args()
    print('')
    print('VeeHarmGen - Vertical Harmony Generator v', __version__)
    print('')
    print('It is assumed that the input file contains one melody with one key and one time signature.')
    print('')
    print('In MuseScore to create placeholder chords')
    print('then use the menu option Add > Text > Staff Text, or use the shortcut Ctrl+T. ')
    print('')
    print("Input file fully qualified      :", args.mxlfile)

    # show all args
    print('vars(args)', vars(args))
    # show demo args
    print('args.chord_choice', args.chord_choice)
    print('args.number', args.number)
    print('args.demo', args.demo)
    # print('args.nth_outcome', args.nth_outcome)
    # print('args.rank', args.rank)
    print('args.style', args.style)
               
    # input('Press Enter to continue...')

    args.analyze = 'all'

    print("Output instrument:", args.instrument)

    # offsets
    SongSectionValues.offsets = args.offsets
    if SongSectionValues.offsets != None:
        print('offsets : -o',SongSectionValues.offsets)

    # print("transpose:", args.transpose)
    SongSectionValues.transpose = args.transpose
    if SongSectionValues.transpose != None:
        print('Transpose : -t',SongSectionValues.transpose)

    # read mxl
    raw_song = music21.converter.parse(args.mxlfile)
    # raw_song.show('text')
    # raw_song.show()
    # measureStack = raw_song.measures(0, 2)
    # measureStack.show()

    if SongSectionValues.transpose != None:
        # transpose with supplied
        transposed_song = raw_song.transpose(SongSectionValues.transpose)
    else:
        # use analyze transpose

        the_interval = get_transpose_information('raw input file', raw_song)
        transposed_song = raw_song.transpose(the_interval)

    the_interval2 = get_transpose_information('transposed after analysis', transposed_song)

    # remove file extension from filename, normalise filename and add file extension
    mxlfile_basename = os.path.basename(args.mxlfile)
    mxlfile_normalised_name = os.path.splitext(mxlfile_basename)[0] + '_transposed.mxl'

    # get path without filename e.g.
    # 1. blank if no path (file in cwd) mxlfile_path               :
    # 2. if has path                    mxlfile_path               : private/input/music/sectioned
    mxlfile_path = os.path.dirname(args.mxlfile)
    # print("mxlfile_path                 :", mxlfile_path)
    mxlfile_normalised_name_path = os.curdir + os.sep + mxlfile_path + os.sep + mxlfile_normalised_name
    print("Normalised input file:", mxlfile_normalised_name_path)

    # Handle a file without sections by adding one on the first note
    if not has_section(transposed_song):
        print('No section found then add intro section name on beat 1.')
        transposed_song = add_TextExpression(transposed_song)

    a_song = normalise_song(transposed_song, mxlfile_normalised_name)
    the_interval3 = get_transpose_information('normalised_song_from_analysis', a_song)

    song_key = a_song.analyze('key')

    # write normalised stream
    a_song.write(fp=mxlfile_normalised_name_path) # write normalised score to musicxml file

    print('Reading mxlfile_normalised...')
    print('Looking for sections: intro, verse, prechorus, chorus, solo, bridge, or outro... ')
    print('')

    print('ANALYZE_CHOICE =', args.analyze)

    analysis_list = [
        'Aarden',
        'Bellman',
        'Krumhansl',
        'Simple',
        'Temperley',
    ]

    if args.analyze == 'all':
        chosen_analysis = analysis_list
    else:
        chosen_analysis = [ args.analyze ]

    if not args.demo:
        print('if not demo')
        if has_chord_symbols(a_song):
            print('    if has_chord_symbols')
            print('        input music has placeholder chords ......................................................................')
            print('')

            generate_from_placeholder_chords(a_song, song_key, args.instrument, mxlfile_basename, args.chord_choice, args.number, args.style)

        else: # not has_chord_symbols

            print('    not has_chord_symbols')
            print('    input music has no placeholder chords .............................................................')

            analysis_choice = 'Krumhansl'
            print('analysis_choice', analysis_choice)

            found_time_signature = False
            first_section_found = False
            first_note_of_section = True
            first_TimeSig = True
            songTimeSig = None

            song_section_values = SongSectionValues(song_key, a_song)
            song_section_values.set_analyze_choice(analysis_choice)
            song_section_values.set_instrument(args.instrument)
            print('song_section_values.analyze_choice', song_section_values.analyze_choice)
            # for each element in stream
            for n in a_song.flatten():

                if type(n) == music21.meter.TimeSignature:
                    if first_TimeSig:
                        song_section_values.set_time_sig(n)
                        first_TimeSig = False

                if type(n) == music21.expressions.TextExpression:
                    # print('music21.expressions.TextExpression')
                    if is_section(n.content):
                        first_note_of_section = True
                        if first_section_found:
                            song_section_values.print()

                        # song_section_values = SongSectionValues(song_key, a_song)

                        song_section_values.set_section(n.content)

                        if not first_section_found:
                            first_section_found = True

                # if note: update song_section_values
                if type(n) == music21.note.Note:
                    # if type(n) != music21.note.Rest:
                    song_section_values.update(n, first_note_of_section)
                    if first_note_of_section == True: first_note_of_section = False

                if type(n) == music21.note.Rest:
                    song_section_values.update_rest(n)

            # print data for last section
            if first_section_found:
                song_section_values.print()
            # if (number_of_sections_found) == 0:
            if not first_section_found:
                print('')
                print(
                    'Warning: Error number_of_sections_found = 0 ##########################################################')
                print('')
                print('MusicXML files are .mxl for compressed files')
                print('The MusicXML melody file must contain staff text words to identify the section start point: ')
                print('intro, verse, prechorus, chorus, solo, bridge or outro. ')
                print(
                    'In MuseScore, to create staff text choose a location by selecting a note or rest and then use the menu option Add > Text > Staff Text, or use the shortcut Ctrl+T.')

            else:
                # at end of song strip final comma and add }
                SongSectionValues.song_offset_chord_1_beat = remove_suffix(SongSectionValues.song_offset_chord_1_beat, ',') + '}'
                SongSectionValues.song_offset_chord_2_beat = remove_suffix(SongSectionValues.song_offset_chord_2_beat, ',') + '}'
                SongSectionValues.song_offset_chord_1_bar = remove_suffix(SongSectionValues.song_offset_chord_1_bar, ',') + '}'
                SongSectionValues.song_offset_chord_2_bar = remove_suffix(SongSectionValues.song_offset_chord_2_bar, ',') + '}'
                SongSectionValues.song_offset_chord_4_bar = remove_suffix(SongSectionValues.song_offset_chord_4_bar, ',') + '}'

                song_section_values.print_class_variable()

                try:
                    SongSectionValues.song_offset_chord_1_beat = ast.literal_eval(SongSectionValues.song_offset_chord_1_beat)
                except BaseException as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    print('exit: Error song_offset_chord_1_beat', SongSectionValues.song_offset_chord_1_beat)
                    sys.exit()

                try:
                    SongSectionValues.song_offset_chord_2_beat = ast.literal_eval(SongSectionValues.song_offset_chord_2_beat)
                except BaseException as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    print('exit: Error song_offset_chord_2_beat', SongSectionValues.song_offset_chord_2_beat)
                    sys.exit()

                try:
                    SongSectionValues.song_offset_chord_1_bar = ast.literal_eval(
                        SongSectionValues.song_offset_chord_1_bar)
                except BaseException as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    print('exit: Error song_offset_chord_1_bar', SongSectionValues.song_offset_chord_1_bar)
                    sys.exit()

                try:
                    SongSectionValues.song_offset_chord_2_bar = ast.literal_eval(SongSectionValues.song_offset_chord_2_bar)
                except BaseException as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    print('exit: Error song_offset_chord_2_bar', SongSectionValues.song_offset_chord_2_bar)
                    sys.exit()

                try:
                    SongSectionValues.song_offset_chord_4_bar = ast.literal_eval(SongSectionValues.song_offset_chord_4_bar)
                except BaseException as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    print('exit: Error song_offset_chord_4_bar', SongSectionValues.song_offset_chord_4_bar)
                    sys.exit()

                # append to lists of the key finder offset chord dictionaries
                SongSectionValues.key_finder_offset_chords_1_beat.append(SongSectionValues.song_offset_chord_1_beat)
                SongSectionValues.key_finder_offset_chords_2_beat.append(SongSectionValues.song_offset_chord_2_beat)
                SongSectionValues.key_finder_offset_chords_1_bar.append(SongSectionValues.song_offset_chord_1_bar)
                SongSectionValues.key_finder_offset_chords_2_bar.append(SongSectionValues.song_offset_chord_2_bar)
                SongSectionValues.key_finder_offset_chords_4_bar.append(SongSectionValues.song_offset_chord_4_bar)

                # dt = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S_%f")
                dt = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
                print('')

            # produce chord output
            print('produce chord output with placeholder chords 1 per bar ON_KEY_MOST')
            chord_output = Chord_Output.ON_KEY_MOST

            # harmonic_rhythm = Harmonic_Rhythm.BAR1
            for harmonic_rhythm in Harmonic_Rhythm:  # e.g. BEAT1, BEAT2, BAR1 etc

                output_filename = os.path.splitext(mxlfile_basename)[0]
                # output_filename = output_filename + '-' + str(chord_output.value) + '-' + chord_output.name + '-' + harmonic_rhythm.name + '-' + dt + '.mxl'
                # output_filename = output_filename + '-chord' + '.mxl'
                output_filename = output_filename + '-' + harmonic_rhythm.name + '.mxl'

                print('song_title, output_filename',mxlfile_basename, output_filename)

                offset_chord = get_offset_chord(chord_output, harmonic_rhythm)
                # print('offset_chord', offset_chord)
                SongSectionValues.last_bass = 'C'
                song_section_values.write_chords(mxlfile_basename, offset_chord, output_filename)

            print('')
            print('Now in Musescore, open output file', output_filename)
            print('This may be manually edited to add or remove placeholder chords.')
            print('')
            print('To enter a chord symbol:')
            print('     Select a start note or rest; Press Ctrl + K (Mac: Cmd + K );')
            print('     Enter chord symbol e.g. C  Exit chord symbol mode by pressing Esc.')
            print('')


    else: # demonstrate the different types of chords
        print('demonstrate the different types of chords')
        for analysis_choice in chosen_analysis:
            print('analysis_choice', analysis_choice)

            found_time_signature = False
            first_section_found = False
            first_note_of_section = True
            first_TimeSig = True
            songTimeSig = None

            song_section_values = SongSectionValues(song_key, a_song)
            song_section_values.set_analyze_choice(analysis_choice)
            song_section_values.set_instrument(args.instrument)
            print('song_section_values.analyze_choice',song_section_values.analyze_choice)
            # for each element in stream
            for n in a_song.flatten():

                if type(n) == music21.meter.TimeSignature:
                    if first_TimeSig:
                        song_section_values.set_time_sig(n)
                        first_TimeSig = False

                if type(n) == music21.expressions.TextExpression:
                    # print('music21.expressions.TextExpression')
                    if is_section(n.content):
                        first_note_of_section = True
                        if first_section_found:
                            song_section_values.print()

                        # song_section_values = SongSectionValues(song_key, a_song)

                        song_section_values.set_section(n.content)

                        if not first_section_found:
                            first_section_found = True

                # if note: update song_section_values
                if type(n) == music21.note.Note:
                    # if type(n) != music21.note.Rest:
                    song_section_values.update(n, first_note_of_section)
                    if first_note_of_section == True: first_note_of_section = False

                if type(n) == music21.note.Rest:
                    song_section_values.update_rest(n)

            # print data for last section
            if first_section_found:
                song_section_values.print()
            # if (number_of_sections_found) == 0:
            if not first_section_found:
                print('')
                print('Warning: Error number_of_sections_found = 0 ##########################################################')
                print('')
                print('MusicXML files are .mxl for compressed files')
                print('The MusicXML melody file must contain staff text words to identify the section start point: ')
                print('intro, verse, prechorus, chorus, solo, bridge or outro. ')
                print('In MuseScore, to create staff text choose a location by selecting a note or rest and then use the menu option Add > Text > Staff Text, or use the shortcut Ctrl+T.')

            else:
                # at end of song strip final comma and add }
                SongSectionValues.song_offset_chord_1_beat = remove_suffix(SongSectionValues.song_offset_chord_1_beat, ',') + '}'
                SongSectionValues.song_offset_chord_2_beat = remove_suffix(SongSectionValues.song_offset_chord_2_beat, ',') + '}'
                SongSectionValues.song_offset_chord_1_bar = remove_suffix(SongSectionValues.song_offset_chord_1_bar, ',') + '}'
                SongSectionValues.song_offset_chord_2_bar = remove_suffix(SongSectionValues.song_offset_chord_2_bar, ',') + '}'
                SongSectionValues.song_offset_chord_4_bar = remove_suffix(SongSectionValues.song_offset_chord_4_bar, ',') + '}'

                song_section_values.print_class_variable()

                # convert string to dictionary using ast.literal_eval() method
                # ast.literal_eval: Safely evaluate an expression node or a string containing a Python literal or container display.
                # The string or node provided may only consist of the following Python literal structures:
                # strings, bytes, numbers, tuples, lists, dicts, sets, booleans, None, bytes and sets.
                try:
                    SongSectionValues.song_offset_chord_1_beat = ast.literal_eval(SongSectionValues.song_offset_chord_1_beat)
                except BaseException as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    print('exit: Error song_offset_chord_1_beat', SongSectionValues.song_offset_chord_1_beat)
                    sys.exit()

                try:
                    SongSectionValues.song_offset_chord_2_beat = ast.literal_eval(SongSectionValues.song_offset_chord_2_beat)
                except BaseException as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    print('exit: Error song_offset_chord_2_beat', SongSectionValues.song_offset_chord_2_beat)
                    sys.exit()

                try:
                    SongSectionValues.song_offset_chord_1_bar = ast.literal_eval(SongSectionValues.song_offset_chord_1_bar)
                except BaseException as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    print('exit: Error song_offset_chord_1_bar', SongSectionValues.song_offset_chord_1_bar)
                    sys.exit()

                try:
                    SongSectionValues.song_offset_chord_2_bar = ast.literal_eval(SongSectionValues.song_offset_chord_2_bar)
                except BaseException as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    print('exit: Error song_offset_chord_2_bar', SongSectionValues.song_offset_chord_2_bar)
                    sys.exit()

                try:
                    SongSectionValues.song_offset_chord_4_bar = ast.literal_eval(SongSectionValues.song_offset_chord_4_bar)
                except BaseException as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    print('exit: Error song_offset_chord_4_bar', SongSectionValues.song_offset_chord_4_bar)
                    sys.exit()

                # append to lists of the key finder offset chord dictionaries for each harmonic rhythm
                SongSectionValues.key_finder_offset_chords_1_beat.append(SongSectionValues.song_offset_chord_1_beat)
                SongSectionValues.key_finder_offset_chords_2_beat.append(SongSectionValues.song_offset_chord_2_beat)
                SongSectionValues.key_finder_offset_chords_1_bar.append(SongSectionValues.song_offset_chord_1_bar)
                SongSectionValues.key_finder_offset_chords_2_bar.append(SongSectionValues.song_offset_chord_2_bar)
                SongSectionValues.key_finder_offset_chords_4_bar.append(SongSectionValues.song_offset_chord_4_bar)


                # dt = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S_%f")
                # dt = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
                print('')

                output_filename = os.path.splitext(mxlfile_basename)[
                                      0] + '-' + analysis_choice + '-' + 'chords_1_beat' + '.mxl'

                # Do not write key finder chords (Aarden ... Simple etc) to file as they have not been filtered for on key

                output_filename = os.path.splitext(mxlfile_basename)[
                                      0] + '-' + analysis_choice + '-' + 'chords_2_beat' + '.mxl'
                # song_section_values.write_chords(mxlfile_basename, song_section_values.song_offset_chord_2_beat, output_filename)

                output_filename = os.path.splitext(mxlfile_basename)[
                                      0] + '-' + analysis_choice + '-' + 'chords_bar_1' + '.mxl'

                # song_section_values.write_chords(mxlfile_basename, song_section_values.song_offset_chord_1_bar, output_filename)

                output_filename = os.path.splitext(mxlfile_basename)[
                                      0] + '-' + analysis_choice + '-' + 'chords_bar_2' + '.mxl'

                # song_section_values.write_chords(mxlfile_basename, song_section_values.song_offset_chord_2_bar, output_filename)

                output_filename = os.path.splitext(mxlfile_basename)[
                                      0] + '-' + analysis_choice + '-' + 'chords_bar_4'  + '.mxl'
                # song_section_values.write_chords(mxlfile_basename, song_section_values.song_offset_chord_4_bar, output_filename)

                print('')

        # produce chord output
        for chord_output in Chord_Output: # e.g. on_key, major, minor etc.
            # print('chord_output, name, value =',chord_output, chord_output.name, chord_output.value )
            for harmonic_rhythm in Harmonic_Rhythm:     # e.g. BEAT1, BEAT2, BAR1 etc
                # print('chord_output.name, harmonic_rhythm.name =', chord_output.name, harmonic_rhythm.name )
                output_filename = os.path.splitext(mxlfile_basename)[0]
                # output_filename = output_filename + '-' + str(chord_output.value) + '-' + chord_output.name + '-' + harmonic_rhythm.name + '-' + dt + '.mxl'
                output_filename = output_filename + '-' + str(chord_output.value) + '-' + chord_output.name + '-' + harmonic_rhythm.name + '.mxl'

                # print('song_title, output_filename',mxlfile_basename, output_filename)
                offset_chord = get_offset_chord(chord_output, harmonic_rhythm)
                # print('offset_chord', offset_chord)
                SongSectionValues.last_bass = 'C'
                song_section_values.write_chords(mxlfile_basename, offset_chord, output_filename)

        print('')
        print('Now in Musescore, open desired output files, play and choose favourite file.')
        print('This may be manually edited to add or substitute other chords from other output files.')
        print('')
        print('In your favourite file:')
        print('To edit a chord symbol double click on it.')
        print('To enter a chord symbol:')
        print('     Select a start note or rest; Press Ctrl + K (Mac: Cmd + K );')
        print('     Enter chord symbol e.g. Am7. Exit chord symbol mode by pressing Esc.')
        print('')

    print('VeeHarmGen - Vertical Harmony Generator v', __version__)


if __name__ == '__main__':

    main()
