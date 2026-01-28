#!/usr/bin/env python
# -*- coding: utf-8 -*-
# VeeHarmGen_utilities.py
#
# common data and functions for VeeHarmGen
#
# free and open-source software, Paul Wardley Davies, see license.txt

import json
import music21
import os
import sys

from enum import Enum
from music21 import *

INPUT_STYLE_PATH = 'input/style/'
INPUT_STYLE_PITCH_TO_CHORD_PATH = 'input/style/pitch_to_chord/'
NO_CHORD_DISPLAY_PITCH_CLASSES = '0000 0000 0000'
PITCH_TO_CHORD_PRE_EXTENSION = '-_-ptc'
JSON_EXTENSION = '.json'
PITCH_TO_CHORD_FILENAME_ENDING = PITCH_TO_CHORD_PRE_EXTENSION + JSON_EXTENSION
# MIN_PITCH_CLASSES_PER_SLICE = 3

class Chord_Choice(Enum):
    RANK = 'rank'
    NTH_OUTCOME = 'nth_outcome'
    INFER = 'infer'
    
    def __str__(self):
        return self.value
        
def calculate_pitch_class_match(pc1, pc2):
    """
    given two pitch_classes
    calculate an integer of how many bits match
    and return match int
    :param pc1 pitch_class: e.g. 1010 1000 0001
    :param pc2 pitch_class: e.g. 0010 0100 0001
    :return: matching_bits  e.g. 9
    """
    matching_bits = 0
    for i in range(len(pc1)):
        if pc1[i] != ' ':
            if pc1[i] == pc2[i]:
                matching_bits += 1
    print ('calculate_pitch_class_match matching_bits, pc1, pc2', matching_bits, pc1,':+', pc2)

    return matching_bits

def calculate_pitch_class_match_pc2_1s_only(pc1, pc2):
    """
    given two pitch_classes
    calculate an integer of how many bits match
    comparing only the 1's in pc2
    and return match int
    :param pc1 pitch_class: e.g. 1010 1000 0001
    :param pc2 pitch_class: e.g. 0010 0100 0001
    :return: matching_bits  e.g. 2
    """
    matching_bits = 0
    for i in range(len(pc1)):
        if pc1[i] != ' ':
            if pc2[i] == '1':
                if pc1[i] == pc2[i]:
                    matching_bits += 1
    print ('calculate_pitch_class_match_pc2_1s_only matching_bits, pc1, pc2', matching_bits, pc1,':+', pc2)

    return matching_bits


def calculate_pitch_class_matches(pc1, pc2):
    """
    given two pitch_classes
    calculate an integer of how many bits match
    comparing all pitch classes and
    comparing only the 1's in pc2
    and return match int
    :param pc1 pitch_class: e.g. 1010 1000 0001
    :param pc2 pitch_class: e.g. 0010 0100 0001
    :return: matching_bits  e.g. 9, 2
    """
    matching_bits = 0
    matching_pc2_one_bits = 0
    for i in range(len(pc1)):
        if pc1[i] != ' ':
            if pc1[i] == pc2[i]:
                matching_bits += 1
            if pc2[i] == '1':
                if pc1[i] == pc2[i]:
                    matching_pc2_one_bits += 1
    # print ('calculate_pitch_class_matches, matching_bits, matching_pc2_one_bits, pc1, pc2', matching_bits, matching_pc2_one_bits, pc1,':+', pc2)

    return matching_bits, matching_pc2_one_bits


def display_pitch_classes(pitch_classes):
    """
    add spaces to pitch_classes for a more readable display eg  C
    input  100010010000
    return 1000 1001 0000
    """

    new_character = ' '

    pitch_classes_display = pitch_classes[:4] + new_character + pitch_classes[4:8] + new_character + pitch_classes[8:12]

    print(pitch_classes, ' bit map C#D# EF#G #A#B')
    print('pitch_classes_display', pitch_classes_display)

    return pitch_classes_display

def get_nearest_chord_for_pitch_class(pitch_class, pitch_to_chord, output_filename):
    """
    given pitch_class and pitch_to_chord dictionary, return short chord (e.g. Am or C) at offset
    :param pitch_class: e.g. 1010 1000 0001
    :param pitch_to_chord : e.g. {1010 0000 0001': {'G': 1}, '0000 1100 0000': {'F': 1}, '1000 0000 0001': {'G': 1}, '1010 1100 0000': {'C': 1}, '0010 1100 0000': {'G': 1}, '1010 1101 0000': {'C': 1}, '0000 0100 0100': {'F': 1}, '0010 1000 0000': {'G': 1}}
    :param output_filename (used in printed warnings)
    :return: short_chord e.g. 'E'
    last_match = 0
    short_chord = None
    for each value in pitch_to_chord
        calculate match
        if match > last_match:
            short_chord = value
    return short_chord
    """

    # print('get_nearest_chord_for_pitch_class(pitch_class, pitch_to_chord, output_filename)', pitch_class,
    #       pitch_to_chord, output_filename)
    last_matching_bits = 0
    last_matching_pc2_one_bits = 0
    last_f = 0
    short_chord = None
    for k, v in pitch_to_chord.items():
        ch, f = next(iter(v.items()))
        # print(k, v)
        # print('k, chord, freq', k, ch, f)
        # v1
        # matching_bits = calculate_pitch_class_match(k, pitch_class)
        # v2
        # matching_bits = calculate_pitch_class_match_pc2_1s_only(k,pitch_class )
        # v3
        matching_bits, matching_pc2_one_bits = calculate_pitch_class_matches(k, pitch_class)
        if matching_pc2_one_bits > last_matching_pc2_one_bits:
            print('k, chord, freq, matching_pc2_one_bits > last_matching_pc2_one_bits             ', k, ch, f, matching_pc2_one_bits, '>', last_matching_pc2_one_bits)
            last_matching_pc2_one_bits = matching_pc2_one_bits
            last_matching_bits = matching_bits
            last_f = f
            short_chord = v
        if matching_pc2_one_bits == last_matching_pc2_one_bits:
            if matching_bits > last_matching_bits:
                print('k, chord, freq, matching_bits > last_matching_bits                             ', k, ch, f, matching_bits, '>', last_matching_bits)
                last_matching_pc2_one_bits = matching_pc2_one_bits
                last_matching_bits = matching_bits
                last_f = f
                short_chord = v
        if matching_pc2_one_bits == last_matching_pc2_one_bits:
            if matching_bits == last_matching_bits:
                if f > last_f:
                    print('k, chord, freq, f > last_f                                                     ', k, ch, f, '>', last_f)
                    last_matching_pc2_one_bits = matching_pc2_one_bits
                    last_matching_bits = matching_bits
                    last_f = f
                    short_chord = v

    return short_chord

def get_different_pitch_classes_in_stream(a_stream):
    """
    for each note in the stream: set the_pitch_classes True
    Count and return the number of different_pitch_classes
    """
    different_pitch_classes = 0
    the_pitch_classes = [0,0,0,0,0,0,0,0,0,0,0,0]

    # for each note in the stream: set the_pitch_classes True
    for n in a_stream.flat:
        if type(n) == music21.note.Note:
            a = pitch.Pitch(n.name)
            the_pitch_classes[a.pitchClass] = 1

    # Count and return the number of different_pitch_classes
    for x in the_pitch_classes:
        if x > 0: different_pitch_classes += 1

    print('the_pitch_classes', the_pitch_classes)
    print('different_pitch_classes =',different_pitch_classes)

    return different_pitch_classes


def get_pitch_classes_in_stream(a_stream):
    """
    for each note in the stream: set the_pitch_classes True
    convert the_pitch_classes into pitch_classes_string and return
    """

    the_pitch_classes = list("000000000000")

    # for each note in the stream: set the_pitch_classes True
    for n in a_stream.flat:
        if type(n) == music21.note.Note:
            a = pitch.Pitch(n.name)
            the_pitch_classes[a.pitchClass] = '1'

    # convert the_pitch_classes into pitch_classes_string and return
    pitch_classes_string = "".join(the_pitch_classes)

    # print('the_pitch_classes', the_pitch_classes)
    # print('pitch_classes_string =', pitch_classes_string)

    return pitch_classes_string

def load_json(fully_qualified_filename):
    """
    load a json file and return the object
    :param fully_qualified_filename: the file to load
    :return: json_object
    """
    # Opening JSON file
    with open(fully_qualified_filename, 'r') as openfile:
        # Reading from json file
        json_object = json.load(openfile)

    # print(json_object)
    # print(type(json_object))

    # e.g. input_pitch_to_chord
    # {'1000 0000 0000': {'C': 2, 'Am7': 1, 'Am': 1}, '0010 0000 0000': {'F': 2, 'G': 1}, '1010 0000 0001': {'G': 1}, '0000 1000 0000': {'C': 1, 'Am': 1}, '0000 1100 0000': {'F': 1}, '1000 0000 0001': {'G': 1}, '1010 1100 0000': {'C': 1}, '0010 1100 0000': {'G': 1}, '1010 1101 0000': {'C': 1}, '0000 0100 0100': {'F': 1}, '0010 1000 0000': {'G': 1}}
    # chord_mapping_json_load.py
    # {'C': {'C7': 2, 'Cmaj7': 1}, 'Dm': {'D': 2, 'Dm7': 1}}
    # <class 'dict'>
    return json_object

#
# def filter_output_stream_for_MuseScore(a_stream, ts, *,
#             inPlace=False,
#             classesToMove=(note.Note, note.Rest, expressions.TextExpression, tempo.MetronomeMark, key.KeySignature, meter.TimeSignature, clef.Clef,
#                            metadata.Metadata, instrument.Instrument, layout.SystemLayout),
#             makeNotation=False):
#     """
#     filter a stream for MuseScore 3.6.2
#     (inPlace is True is not yet written)
#     the elements are filtered in the current stream.
#     if inPlace is False then a new stream is returned.
#
#     all elements of class classesToMove get moved.
#     This puts the clefs, TimeSignatures, etc. in their proper locations.
#     """
#
#     if inPlace is True:
#         returnObj = self
#         raise Exception("Whoops haven't written inPlace=True yet for filter_output_stream_for_MuseScore")
#     else:
#         returnObj = stream.Part()
#
#     # strip ties, flatten, make measures, make ties
#     stripped = a_stream.stripTies().flatten()
#     # out1 = stripped.makeVoices()
#     out2 = stripped.makeNotation()
#     returnObj = out2.makeTies()
#
#     return returnObj
#
#

def remove_files_ending_with_from_dir(ends_with, from_dir):
    """
    delete files that end with a string from a directory
    :param ends_with: string the file ends with
    :param from_dir: the path to the files
    :return: void
    """
    print('remove_files_ending_with_from_dir', ends_with, from_dir)

    # check ends_with not blank
    if ends_with == '':
        print('remove_files_ending_with_from_dir exit: ends_with blank')
        sys.exit()
    # Check whether the specified path exists or not
    isExist = os.path.exists(from_dir)
    if not isExist:
        print('remove_files_ending_with_from_dir exit: path does not exist')
        sys.exit()
    # list the files in the directory
    for filename in os.listdir(from_dir):
        # if the filename is a file and ending with ends_with
        if os.path.isfile(os.path.join(from_dir, filename)):
            if filename.endswith(ends_with):
                print('Deleting', filename)
                os.remove(os.path.join(from_dir, filename))

    return