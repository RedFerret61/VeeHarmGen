#!/usr/bin/env python
# -*- coding: utf-8 -*-
# create_styles.py
#
# for each sub-directory in input/styles
# merges the .json files in the sub-directory and writes
# the style data in parent including the name of sub-directory in the output file name.
# e.g. traditional-1-_-ptc.json
#
# Normal run (which looks for populated style directories under input/styles) :
#
#     create_styles.py
#
# Run specifying a different directory:
#
#     create_styles -i private/input/style
#
# free and open-source software, Paul Wardley Davies, see license.txt

# usage: create_styles.py [-h] [-i INPUTDIR]
#
# optional arguments:
#   -h, --help            show this help message and exit
#   -i INPUTDIR, --inputdir INPUTDIR
#                         input file path, relative to current working directory. Default is input/styles


# standard libraries
import argparse
import ast
import bisect
import json
import math
import music21
import os
import re
import sys
import VeeHarmGen_utilities

from fractions import Fraction
from json import dumps
from music21 import *
from music21.harmony import ChordSymbol, NoChord
from VeeHarmGen_utilities import *

CREATE_STYLES_VERSION = '1.0.0'

def get_immediate_subdirectories(a_dir):
    """
    get the list of subdirectories for a directory
    :param a_dir: a directory
    :return: a list of the immediate_subdirectories
    """
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def main():
    """
    get command line arguments
    for each sub-directory in input/styles
    merges the .json files in the sub-directory and writes
    the style data in parent including the name of sub-directory in the output file name.
    e.g. traditional-1-_-ptc.json
    """

    # Specify command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputdir',
                        help='input directory relative to current working directory e.g. private/input/style '
                            'The default is input/style '
                            'This merges the .json files in each sub-directory and outputs to the parent directory.',
                        default='input/style',
                        type=str)

    # Parse command line arguments.
    args = parser.parse_args()
    print('create_styles.py', CREATE_STYLES_VERSION)
    print('')
    # show all args
    print('vars(args)', vars(args))
    # show particular args
    print('args.inputdir', args.inputdir)
    # input('Press Enter to continue...')

    # for each sub-directory in input/styles
    input_path = args.inputdir
    output_path = args.inputdir

    style_dirs = get_immediate_subdirectories(input_path)
    print('style_dirs', style_dirs)
    print('')
    # input('Press Enter to continue...')

    pitch_to_chord = {}

    for style in style_dirs:
        merged_pitch_to_chord = {}
        print('style', style)
        # merge the .json files in sub-directory

        # for each file in subdir
        input_style_dir = input_path + os.sep + style
        for file in os.listdir(input_style_dir):
            if file.endswith(PITCH_TO_CHORD_FILENAME_ENDING):

                print('    file', file)
                input_pitch_to_chord_fully_qualified = os.path.join(input_style_dir, file)
                # print('input_pitch_to_chord_fully_qualified', input_pitch_to_chord_fully_qualified)

                #       read file
                pitch_to_chord = load_json(input_pitch_to_chord_fully_qualified)
                print('    pitch_to_chord', pitch_to_chord)

                #       merge file to merged_pitch_to_chord
                for k, map_chord in pitch_to_chord.items():
                    print(' type(k), k, type(map_chord), map_chord', type(k), k, type(map_chord), map_chord)
                    if k in merged_pitch_to_chord:
                        # print('     k in merged_pitch_to_chord')
                        print('     k, type(merged_pitch_to_chord[k]), merged_pitch_to_chord[k]', k, type(merged_pitch_to_chord[k]), merged_pitch_to_chord[k])    # e.g. 0000 0000 0100 {'A9': 1}
                        # print('     merged_pitch_to_chord', merged_pitch_to_chord)    # e.g.  {'1010 1001 0101': {'A9': 1, 'D9': 1}, '0000 1001 0100': {'A9': 1}, '0000 1000 0000': {'E9': 3, 'C#m7': 2}, '1010 0000 0100': {'D9': 2}, '0000 0000 0100': {'A9': 1}, '0000 1000 0100': {'A9': 2}, '0100 0000 0000': {'F#m7': 2}, '1000 0000 0101': {'Am7': 1}, '0000 0000 0101': {'D9': 1}, '0010 0000 0001': {'Bm7': 1}, '0101 1010 0000': {'C#m7': 1, 'D-m7': 1}, '1010 1010 0000': {'C': 2}, '0000 0000 0001': {'B': 1, 'Em': 8}, '0101 0000 1010': {'A-m': 1}, '0010 1101 0000': {'Dm7': 1}, '0000 0001 0101': {'G7': 1}, '1000 0000 0000': {'C': 9, 'Fm': 1}, '0010 0000 0000': {'Dm': 6, 'Dm7': 2, 'G': 1}}

                        # for each key value in map_chord
                        for mpk, mpv in map_chord.items():
                            # print('         mpk, mpv in map_chord.items()', mpk, mpv, map_chord.items())
                            # if k in merged_pitch_to_chord[k]:
                            if mpk in merged_pitch_to_chord[k]:
                                print('             mpk in merged_pitch_to_chord[k]:', mpk, 'in', merged_pitch_to_chord[k] )
                                # add value to merged_pitch_to_chord[k].value
                                # print('             merged_pitch_to_chord[k][mpk] + mpv', merged_pitch_to_chord[k][mpk],  ' + ',  mpv)
                                merged_pitch_to_chord[k][mpk] = merged_pitch_to_chord[k][mpk] + mpv
                                # print('             = merged_pitch_to_chord[k][mpk] ',merged_pitch_to_chord[k][mpk] )

                            else:
                                print('             mpk not in merged_pitch_to_chord[k]:', mpk, 'NOT in', merged_pitch_to_chord[k]  )
                                # add new mpk, mpv to merged_pitch_to_chord[k]
                                # print('             add ', mpk, mpv, ' to ', merged_pitch_to_chord[k])
                                # print('             merged_pitch_to_chord[k] [mpk] = mpv', merged_pitch_to_chord[k], mpk, ' = ', mpv)
                                merged_pitch_to_chord[k][mpk] = mpv
                        print('     new merged_pitch_to_chord[k]', merged_pitch_to_chord[k])

                        # if map_chord in merged_pitch_to_chord[k]:   # TypeError: unhashable type: 'dict'
                        #     # e.g. 0000 0000 0100 already in merged_pitch_to_chord
                        #     # merge map_chords
                        #     print('merged_pitch_to_chord[k]', merged_pitch_to_chord[k])
                        #     pass
                        #     merged_pitch_to_chord[k][str(map_chord)] += 1
                        # else:
                        #     merged_pitch_to_chord[k][str(map_chord)] = 1

                    else:
                        # print('k not in merged_pitch_to_chord.')
                        # key = frozenset(pitch_to_chord.items())
                        # merged_pitch_to_chord[k] = {dumps(map_chord)}
                        s = '{ '
                        for k2, v2 in map_chord.items():
                            s = s + "'" + k2 + "'" +  ' : ' + str(v2) + ', '
                        s = s.rstrip(', ')
                        s = s + ' }'
                        # print('s',s)
                        merged_pitch_to_chord[k] = ast.literal_eval(s)

        # write the style data in parent including the name of sub-directory in the output file name. e.g. traditional-1-_-ptc.json
        output_pitch_to_chord_fully_qualified = output_path + os.sep + style + PITCH_TO_CHORD_FILENAME_ENDING

        print('Writing ',output_pitch_to_chord_fully_qualified)

        # Serializing json
        print('merged_pitch_to_chord', merged_pitch_to_chord)
        json_object = json.dumps(merged_pitch_to_chord, indent=4)
        with open(output_pitch_to_chord_fully_qualified, "w") as outfile:
            outfile.write(json_object)

if __name__ == '__main__':

    main()
