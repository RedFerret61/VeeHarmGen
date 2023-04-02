#!/usr/bin/env python
# -*- coding: utf-8 -*-
# fix_musicxml_chord_symbols.py

# given a folder with mxl files,
# for each mxl file
#     convert to uncompressed
#     for each line
#         readline
#         correct chord
#     write file to uncompressed
#     convert uncompressed to compressed musicxml

# This converts harmony kind to one in music21 CHORD_TYPES:
# https://github.com/cuthbertLab/music21/blob/master/music21/harmony.py
#
# CHORD_TYPES = collections.OrderedDict([
#     ('major', ['1,3,5', ['', 'M', 'maj']]),  # Y
#     ('minor', ['1,-3,5', ['m', 'min']]),  # Y
#     ('augmented', ['1,3,#5', ['+', 'aug']]),  # Y
#     ('diminished', ['1,-3,-5', ['dim', 'o']]),  # Y
#     # sevenths
#     ('dominant-seventh', ['1,3,5,-7', ['7', 'dom7', ]]),  # Y: 'dominant'
#     ('major-seventh', ['1,3,5,7', ['maj7', 'M7']]),  # Y
#     ('minor-major-seventh', ['1,-3,5,7', ['mM7', 'm#7', 'minmaj7']]),  # Y: 'major-minor'
#     ('minor-seventh', ['1,-3,5,-7', ['m7', 'min7']]),  # Y
#     ('augmented-major-seventh', ['1,3,#5,7', ['+M7', 'augmaj7']]),  # N
#     ('augmented-seventh', ['1,3,#5,-7', ['7+', '+7', 'aug7']]),  # Y
#     ('half-diminished-seventh', ['1,-3,-5,-7', ['ø7', 'm7b5']]),  # Y: 'half-diminished'
#     ('diminished-seventh', ['1,-3,-5,--7', ['o7', 'dim7']]),  # Y
#     ('seventh-flat-five', ['1,3,-5,-7', ['dom7dim5']]),  # N
#
#     # sixths
#     ('major-sixth', ['1,3,5,6', ['6']]),  # Y
#     ('minor-sixth', ['1,-3,5,6', ['m6', 'min6']]),  # Y
#
#     # ninths
#     ('major-ninth', ['1,3,5,7,9', ['M9', 'Maj9']]),  # Y
#     ('dominant-ninth', ['1,3,5,-7,9', ['9', 'dom9']]),  # Y
#     ('minor-major-ninth', ['1,-3,5,7,9', ['mM9', 'minmaj9']]),  # N
#     ('minor-ninth', ['1,-3,5,-7,9', ['m9', 'min9']]),  # N
#     ('augmented-major-ninth', ['1,3,#5,7,9', ['+M9', 'augmaj9']]),  # Y
#     ('augmented-dominant-ninth', ['1,3,#5,-7,9', ['9#5', '+9', 'aug9']]),  # N
#     ('half-diminished-ninth', ['1,-3,-5,-7,9', ['ø9']]),  # N
#     ('half-diminished-minor-ninth', ['1,-3,-5,-7,-9', ['øb9']]),  # N
#     ('diminished-ninth', ['1,-3,-5,--7,9', ['o9', 'dim9']]),  # N
#     ('diminished-minor-ninth', ['1,-3,-5,--7,-9', ['ob9', 'dimb9']]),  # N
#
#     # elevenths
#     ('dominant-11th', ['1,3,5,-7,9,11', ['11', 'dom11']]),  # Y
#     ('major-11th', ['1,3,5,7,9,11', ['M11', 'Maj11']]),  # Y
#     ('minor-major-11th', ['1,-3,5,7,9,11', ['mM11', 'minmaj11']]),  # N
#     ('minor-11th', ['1,-3,5,-7,9,11', ['m11', 'min11']]),  # Y
#     ('augmented-major-11th', ['1,3,#5,7,9,11', ['+M11', 'augmaj11']]),  # N
#     ('augmented-11th', ['1,3,#5,-7,9,11', ['+11', 'aug11']]),  # N
#     ('half-diminished-11th', ['1,-3,-5,-7,9,11', ['ø11']]),  # N
#     ('diminished-11th', ['1,-3,-5,--7,9,11', ['o11', 'dim11']]),  # N
#
#     # thirteenths
#     ('major-13th', ['1,3,5,7,9,11,13', ['M13', 'Maj13']]),  # Y
#     ('dominant-13th', ['1,3,5,-7,9,11,13', ['13', 'dom13']]),  # Y
#     ('minor-major-13th', ['1,-3,5,7,9,11,13', ['mM13', 'minmaj13']]),  # N
#     ('minor-13th', ['1,-3,5,-7,9,11,13', ['m13', 'min13']]),  # Y
#     ('augmented-major-13th', ['1,3,#5,7,9,11,13', ['+M13', 'augmaj13']]),  # N
#     ('augmented-dominant-13th', ['1,3,#5,-7,9,11,13', ['+13', 'aug13']]),  # N
#     ('half-diminished-13th', ['1,-3,-5,-7,9,11,13', ['ø13']]),  # N
#
#     # other
#     ('suspended-second', ['1,2,5', ['sus2']]),  # Y
#     ('suspended-fourth', ['1,4,5', ['sus', 'sus4']]),  # Y
#     ('suspended-fourth-seventh', ['1,4,5,-7', ['7sus', '7sus4']]),  # Y
#     ('Neapolitan', ['1,2-,3,5-', ['N6']]),  # Y
#     ('Italian', ['1,#4,-6', ['It+6', 'It']]),  # Y
#     ('French', ['1,2,#4,-6', ['Fr+6', 'Fr']]),  # Y
#     ('German', ['1,-3,#4,-6', ['Gr+6', 'Ger']]),  # Y
#     ('pedal', ['1', ['pedal']]),  # Y
#     ('power', ['1,5', ['power']]),  # Y
#     ('Tristan', ['1,#4,#6,#9', ['tristan']]),  # Y
# ])

# see
# https://stackoverflow.com/questions/1591579/how-to-update-modify-an-xml-file-in-python

# standard libraries
import contextlib
import music21
import os

from music21.musicxml.archiveTools import compressXML
from music21.musicxml.archiveTools import uncompressMXL

print('Uncompressing musicxml .mxl to .musicxml')
# delete any existing musicxml
if os.path.exists("private/input/music/placeholder_chords/input.musicxml"):
  os.remove("private/input/music/placeholder_chords/input.musicxml")
else:
  print("The input.musicxml does not exist")

with contextlib.redirect_stderr(open(os.devnull, 'w')):
    uncompressMXL("private/input/music/placeholder_chords/input.mxl")

in_file = open("private/input/music/placeholder_chords/input.musicxml", "r")
lines_of_in_file = in_file.readlines()
in_file.close()

lines_of_out_file = []

# do some processing to allow Music21 to correctly parse the chord symbol
# music21 writes:
# <kind>minor</kind>
# <kind>major-seventh</kind>
# <kind>minor-seventh</kind>
        
for idx, x in enumerate(lines_of_in_file):

    # if chord harmony kind then
    if '<kind' in x:

        if '<kind> </kind>' in x:    # 'major'
            print('before', idx, x)
            x = x.replace("<kind> </kind>", "<kind>major</kind>")
            print('after    ', idx, x)

        elif '>min<' in x:    # 'minor'
            print('before', idx, x)
            x = x.replace("<kind>min</kind>", "<kind>minor</kind>")
            print('after    ', idx, x)

        elif '<kind>dim</kind>' in x:    # 'diminished'
            print('before', idx, x)
            x = x.replace("<kind>dim</kind>", "<kind>diminished</kind>")
            print('after    ', idx, x)

        elif '<kind>7</kind>' in x: # dominant-seventh
            print('before', idx, x)
            x = x.replace("<kind>7</kind>", "<kind>dominant-seventh</kind>")
            print('after    ', idx, x)

        elif '<kind>min7</kind>' in x: # minor-seventh
            print('before', idx, x)
            x = x.replace("<kind>min7</kind>", "<kind>minor-seventh</kind>")
            print('after    ', idx, x)

        else:  # else print unknown chord
            print('WARNING unknown harmony kind', idx, x)

    # Following could not get major chord output from from John_Lennon-1964-If_I_Fell got pedal instead
    # if space at end of major remove space
    # if '<kind />' in x:
    #     print('before', idx, x)
    #     x = x.replace("<kind />", "<kind/>")
    #     print('after    ', idx, x)

    lines_of_out_file.append(x)

# debug output
# out0_file = open("private/input/music/placeholder_chords/output0.musicxml", "w")
# out0_file.writelines(lines_of_out_file)
# out0_file.close()

out_file = open("private/input/music/placeholder_chords/output.musicxml", "w")
out_file.writelines(lines_of_out_file)
out_file.close()

print('Writing compressed musicxml')
# parse output in music21
m21_ready_stream = music21.converter.parse("private/input/music/placeholder_chords/output.musicxml")

# write compressed musicxml output
with contextlib.redirect_stderr(open(os.devnull, 'w')):
    # debug output
    # compressXML("private/input/music/placeholder_chords/output0.musicxml", deleteOriginal=False)

    m21_ready_stream.write("xml", "private/input/music/placeholder_chords/output.musicxml")
    compressXML("private/input/music/placeholder_chords/output.musicxml", deleteOriginal=False)


