# VeeHarmGen
VeeHarmGen adds chords to a melody using style files. It is a **Ve**rtical **Harm**ony **Gen**eration program that 
takes an **input** musicxml file containing a **melody** and 
creates **output** musicxml files with added **Chord Symbols**.
These can be played back and edited in scorewriter programs
such as MuseScore 3.6.2.

There is a VeeHarmGen demonstration video on youtube: https://www.youtube.com/watch?v=3fv-eC-yg7I

[![Add chords to a melody using styles in VeeHarmGen 2](assets/images/youtube1.png)](https://www.youtube.com/watch?v=3fv-eC-yg7I "Add chords to a melody using styles in VeeHarmGen 2")

The latest release has been tested on: 
* Windows 10.0.19044 with 
  - MuseScore 3.6.2,    Python 3.10.8,  music21 v 8.1.0 
* macOS Ventura 13.1 with
  - MuseScore 3.6.2,    Python 3.9.6,   music21 v 8.1.0
* Ubuntu 20.04 with 
  - MuseScore 3.2.3,    Python 3.8.10,  music21 v 8.1.0

Note: MuseScore 4.0.2 has chord symbol display bug, Format Style, Chord Symbols, toggle to Jazz then back to standard.

**Table of Contents**

1. [QuickStart](#QuickStart)
2. [Introduction](#Introduction)
3. [Prerequisites](#Prerequisites)
4. [WindowsInstall](#WindowsInstall)
5. [macOSInstall](#macOSInstall)
6. [UbuntuInstall](#UbuntuInstall)
7. [Input_Music](#Input_Music)
8. [Output](#Output)
9. [ToolsForStyleCreation](#ToolsForStyleCreation)

*Note: GitHub has a full table of contents with links in the header icon (top left of the readme.md).*

---
## QuickStart

Assuming you have:
* the pre-requisites (MuseScore, Python, and Music21)
* performed the VeeHarmGen install for your platform
* a music.mxl file in the input/music directory with a single stave monophonic melody, e.g.

![e.g. Music](assets/images/music.png)

### Windows
Start cmd

    cd <install folder>
    run music

Start explorer, goto the output folder under VeeHarmGen, double click on a .mxl file to view in MuseScore.

### macOS / Ubuntu
Start a terminal

    cd ~/VeeHarmGen
    chmod a+x run*
    
    ./run.sh music

Use finder / file manager to goto the output directory under VeeHarmGen, double click on a .mxl file to view in MuseScore.

e.g. this uses **tune slice key analysis** to add chords:

![e.g. Music](assets/images/music-BAR1.png)

e.g. this uses the **all_jazz chord style** to add chords:

![e.g. Music](assets/images/music-BAR1-all_jazz-R100.png)


---
## Introduction

VeeHarmGen is a Vertical Harmony Generation program that 
takes an input musicxml file containing a melody and 
creates output musicxml files with added Chord Symbols.

VeeHarmGen expects two types of input files : 

* tunes **without sections** where the generated harmonic rhythm (beats or bars per chord ) will be continous throughout the song.
For example music with a generated 2 bar harmonic rhythm:

![e.g. Music](assets/images/music-BAR2.png)

* tunes **with sections** (from MarkMelGen https://github.com/RedFerret61/MarkMelGen ) where the generated harmonic rhythm will restart on each section (denoted by staff text to identify the section start point: 
                intro, verse, prechorus, chorus, solo, bridge or outro). For example 
the previous section to the PRECHORUS ends with a 1 bar chord, and the PRECHORUS restarts the 2 bar chord rhythm.

![e.g. Cairo-BAR2-folk_1-R100](assets/images/Cairo-BAR2-folk_1-R100.png)


VeeHarmGen version 1 used the **tune slice key analysis** feature in Music21 to add chords. 
(see https://web.mit.edu/music21/doc/usersGuide/usersGuide_15_key.html ).
However instead of analysing the whole piece, the tune is sliced into differently sized windows of analysis to get the key every quarter note, 
every half note, every measure, every two measures, etc.  Each key becomes a chord for the slice e.g. C or Am,
This works when there are severel different pitches in the tune slice.
When there is only one note in a slice, the result is ambiguous e.g. the key/chord may be Em or E. 
The the key analysis method of chord selection is selected with the -d DEMO option to demonstrate some different 
commonly used chords and harmonic rhythms.

VeeHarmGen version 2 introduced preset **chord styles** of a map of the pitch classes to chords. 
By default output is generated for all styles.
The -s STYLE option can be used to filter the generated output e.g. -s jazz only includes style names containing the string jazz.
See VeeHarmGen/input/style for the set of styles and "all" superset styles.

    all-_-ptc.json
    all_jazz-_-ptc.json
    all_non_jazz-_-ptc.json
    all_rock_pop_0-_-ptc.json
    all_rock_pop_1-_-ptc.json
    blues_1-_-ptc.json
    country_rock_1-_-ptc.json
    country_rock_2-_-ptc.json
    early_jazz_1-_-ptc.json
    early_jazz_2-_-ptc.json
    easy_listening_1-_-ptc.json
    folk_1-_-ptc.json
    folk_rock_1-_-ptc.json
    glam_rock_1-_-ptc.json
    indie_rock_1-_-ptc.json
    jazz_related_1-_-ptc.json
    jazz_rock_1-_-ptc.json
    jazz_standard_1-_-ptc.json
    modern_jazz_1-_-ptc.json
    new_wave_1-_-ptc.json
    pop_1-_-ptc.json
    pop_country_1-_-ptc.json
    rock_pop_0_4-_-ptc.json
    rock_pop_0_5-_-ptc.json
    rock_pop_0_7-_-ptc.json
    rock_pop_1_4-_-ptc.json
    rock_pop_1_5-_-ptc.json
    rock_pop_1_7-_-ptc.json
    rock_pop_1_9-_-ptc.json
    show_tune_1-_-ptc.json
    soul_1-_-ptc.json

Each slice of melody has a set of pitch classes which can be mapped to a chord in a particular style.

There are 12 pitch classes in standard Western music: C, C#, D, D#, E, F, F#, G, G#, A, A# and B. 
The pitch class C consists of the Cs in all octaves. In VeeHarmGen ptc.json files a 12-bit pattern, 
e.g. **"1000 1001 0000", represents a melody containing the pitch classes C, E and G.**  
The first bit is C, the second is C#, ..., the last bit is B.

For example, an excerpt from all-_-ptc.json:

       "1000 1001 0000": {
        "C": 30,
        "G": 3,
        "B-": 1,
        "D7": 1,
        "G9": 3,
        "Em7": 1,
        "Fmaj7": 1,
        "F#maj7": 1,
        "C6": 1,
        "A7": 6,
        "Am7": 1,
        "Am": 1,
        "Cm": 1,
        "C/E": 1
    },
	


In the above example, there is a "tune" slice with only C, E and G notes, 
where the (unsorted) chord frequencies for the "tune" included:

       30 "C" chords
       6 "A7" chords 
       3 "G" chords
       3 "G9" chords
      etc.  
   
If VeeHarmGen was given an input tune slice with only C, E and G notes, it would select the "C" chord by default,  
unless the rank command line option was supplied, where 1 is least frequent and 100 (the default) is the most frequent
in the nearest-rank ordered list of possible chords.

### Example VeeHarmGen workflow 1

* Generate harmonic rhythms
  * Choose desired harmonic rhythm e.g. BAR1 (optionally manually edit to vary the rhythm. 
  In MuseScore, to create a Chord Symbol: select start note and then use the menu option Add > Text > Chord Symbol 
  (shortcut Ctrl+K))  
* Run desired harmonic rhythm for all styles
  * Choose favourite style e.g. glam_rock_1 
* Run chosen style with a variety of chord ranks e.g. 60, 30, 1 on various instruments (for a list of instruments: python VeeHarmGen.py -h)
  * Choose favourite chord rank

Assuming Perambulate.mxl is in VeeHarmGen\input\music:

Windows commands

    python VeeHarmGen.py -m input/music/Perambulate.mxl
    python VeeHarmGen.py -m output/Perambulate-BAR1.mxl
    python VeeHarmGen.py -m output/Perambulate-BAR1.mxl -s glam_rock_1 -r 60 -i Saxophone
    python VeeHarmGen.py -m output/Perambulate-BAR1.mxl -s glam_rock_1 -r 30 -i "Reed Organ" 
    python VeeHarmGen.py -m output/Perambulate-BAR1.mxl -s glam_rock_1 -r 1 -i Celesta
 
macOS / Ubuntu commands 

    python3 VeeHarmGen.py -m input/music/Perambulate.mxl
    python3 VeeHarmGen.py -m output/Perambulate-BAR1.mxl
    python3 VeeHarmGen.py -m output/Perambulate-BAR1.mxl -s glam_rock_1 -r 60 -i Saxophone
    python3 VeeHarmGen.py -m output/Perambulate-BAR1.mxl -s glam_rock_1 -r 30 -i "Reed Organ"
    python3 VeeHarmGen.py -m output/Perambulate-BAR1.mxl -s glam_rock_1 -r 1 -i Celesta



## Prerequisites

Pre-requisites for VeeHarmGen include MuseScore, Python, and Music21.
For more information on pre-requisite installation see:
 
* https://github.com/RedFerret61/MarkMelGen#WindowsInstall
* https://github.com/RedFerret61/MarkMelGen#macosinstall
* https://github.com/RedFerret61/MarkMelGen#ubuntuinstall



## WindowsInstall


### VeeHarmGen Windows installation

#### Install VeeHarmGen on Windows
 Download release zip to desired directory for VeeHarmGen and unzip with right click Extract All ...
#### Run VeeHarmGen on Windows 

 In a Command Prompt window change to install directory and show VeeHarmGen help e.g.:

    cd C:\Users\paul\Documents\VeeHarmGen

    VeeHarmGen.py -h
    :: or
    python VeeHarmGen.py -h

There are scripts to show VeeHarmGen features.
In a Command Prompt window change to install directory and run a script e.g.:

##### One measure harmonic rhythm

    cd C:\Users\paul\Music\VeeHarmGen
    run.cmd

        USAGE: run mxlfile
           where mxfile.mxl is in input/music e.g. run music
           Output is in output
        Produces harmonic rhythm placeholders and styles for the one measure harmonic rhythm.

To see the output, Start File Explorer and go to the output folder in your VeeHarmGen install directory.
Double-click on a musicxml file to open it in MuseScore. When finished, Close MuseScore.

##### One measure harmonic rhythm for a "rock" style subset

    run_BAR1_rock.cmd
        USAGE: run_BAR1_rock mxlfile
               where mxfile.mxl is in input/music e.g. run_BAR1_rock music
               Output is in output
        Produces harmonic rhythm placeholders and then
        uses "BAR1" as input for a "rock" style subset

##### Two measure harmonic rhythm for a "folk" style subset

    run_BAR2_folk.cmd

        USAGE: run_BAR2_folk mxlfile
               where mxfile.mxl is in input/music e.g. run_BAR2_folk music
               Output is in output
        Produces harmonic rhythm placeholders and then
        uses "BAR2" as input for a "folk" style subset

##### Two beat harmonic rhythm for a "jazz" style subset

    run_BEAT2_jazz.cmd

        USAGE: run_BEAT2_jazz mxlfile
               where mxfile.mxl is in input/music e.g. run_BEAT2_jazz music
               Output is in output
        Produces harmonic rhythm placeholders and then
        uses "BEAT2" as input for a "jazz" style subset

##### Using placeholder chords to output files for "all" styles

    run_placeholder.cmd

        USAGE: run_placeholder mxlfile
               where mxfile.mxl is in input/music/placeholder_chords e.g. run_placeholder music
               Output is in output
        Uses the input file placeholder chords to output files for "all" styles.

##### A range of chord popularity ranks

    run_rank.cmd

        USAGE: run_rank mxlfile
               where mxfile.mxl is in input/music e.g. run_rank music
               Output is in output
        Produces harmonic rhythm placeholders and then
        uses "BAR1" as input for the "all" style superset for a range of chord popularity ranks (-r)

##### A range of chord popularity ranks

    run_demo.cmd

        USAGE: run_demo mxlfile
               where mxfile.mxl is in input/music e.g. run_demo music
               Output is in output
        Produces demonstration chord type files for each harmonic rhythm.

## macOSInstall

Pre-requisites for VeeHarmGen include MuseScore, Python, and Music21.
For more information on pre-requisite installation see https://github.com/RedFerret61/MarkMelGen#macOSInstall

#### Install VeeHarmGen on macOS
 Download release zip to desired directory for VeeHarmGen and unzip by double-clicking on the zipped file .
#### Run VeeHarmGen on macOS

 In command prompt change to install directory, make run files executable and run VeeHarmGen e.g.:


     cd ~/VeeHarmGen
     
     # display help    
     python3 VeeHarmGen.py -h
     
     # run with default input music 
     python3 VeeHarmGen.py


There are scripts to show VeeHarmGen features.
In a Command Prompt window change to install directory and run a script e.g.:

##### One measure harmonic rhythm

    cd ~/VeeHarmGen
    chmod a+x run*
    
    ./run.sh

        USAGE: ./run.sh mxlfile
           where mxfile.mxl is in input/music e.g. ./run.sh music
           Output is in output
        Produces harmonic rhythm placeholders and styles for the one measure harmonic rhythm.

To see the output, Start File Explorer and go to the output folder in your VeeHarmGen install directory.
Double-click on a musicxml file to open it in MuseScore. When finished, Close MuseScore.

##### One measure harmonic rhythm for a "rock" style subset

    ./run_BAR1_rock.sh
    
        USAGE: ./run_BAR1_rock.sh mxlfile
            where mxfile.mxl is in input/music e.g. ./run_BAR1_rock.sh music
            Output is in output
        Produces harmonic rhythm placeholders and then
        uses "BAR1" as input for a "rock" style subset

##### Two measure harmonic rhythm for a "folk" style subset

    ./run_BAR2_folk.sh

        USAGE: ./run_BAR2_folk.sh mxlfile
            where mxfile.mxl is in input/music e.g. ./run_BAR2_folk.sh music
            Output is in output
        Produces harmonic rhythm placeholders and then
        uses "BAR2" as input for a "folk" style subset

##### Two beat harmonic rhythm for a "jazz" style subset

    ./run_BEAT2_jazz.sh

        USAGE: ./run_BEAT2_jazz.sh mxlfile
            where mxfile.mxl is in input/music e.g. ./run_BEAT2_jazz.sh music
            Output is in output
        Produces harmonic rhythm placeholders and then
        uses "BEAT2" as input for a "jazz" style subset

##### Using placeholder chords to output files for "all" styles

    ./run_placeholder.sh

        USAGE: ./run_placeholder.sh mxlfile
            where mxfile.mxl is in input/music/placeholder_chords e.g. ./run_placeholder.sh music
            Output is in output
        Uses the input file placeholder chords to output files for "all" styles.

##### A range of chord popularity ranks

    ./run_rank.sh

        USAGE: ./run_rank.sh mxlfile
            where mxfile.mxl is in input/music e.g. ./run_rank.sh music
            Output is in output
        Produces harmonic rhythm placeholders and then
        uses "BAR1" as input for the "all" style superset for a range of chord popularity ranks (-r)

##### A range of chord popularity ranks

    ./run_demo.sh

        USAGE: ./run_demo.sh mxlfile
            where mxfile.mxl is in input/music e.g. ./run_demo.sh music
            Output is in output
        Produces demonstration chord type files for each harmonic rhythm.

 
See "Run VeeHarmGen on Windows" for an output description.


---

## VeeHarmGen Installation instructions for Ubuntu
Pre-requisites for VeeHarmGen include MuseScore, Python, and Music21.
For more information on Ubuntu pre-requisite installation see
https://github.com/RedFerret61/MarkMelGen#UbuntuInstall

#### Install VeeHarmGen on Ubuntu
 Download release zip to desired directory for VeeHarmGen and unzip.
#### Run VeeHarmGen on Ubuntu

See "Run VeeHarmGen on macOS" as it is similar on Ubuntu.

---

## Input_Music
### *** Edit INPUT_MUSIC_FILENAME to have only the melody in one key ***

Starting from a midi file, open the .mid in MuseScore.
To find the melody channel / stave in MuseScore, View>Mixer (F10),
Play, click S to toggle Solo. MIDI channel shown in top right of Mixer.

Starting from a Music XML file, 
e.g. on windows C:\Users\<username>\AppData\Local\Programs\Python\Python39\Lib\site-packages\music21\corpus , 
open the .mxl in MuseScore.

#### Delete unwanted staves:

Edit>Instruments, select unwanted stave, Remove from Score.

#### Delete unwanted clefs:
If the melody is on a piano stave, and you want to delete the bass clef or a harmony clef.
Press i for the instruments' dialog.
Click Stave 2 on the piano then the "Remove from score" button in the middle of the box.
Click OK and the staff will be gone.
Any unwanted extra notes/rests may be selected and Deleted.

#### Delete unwanted bars:
For example bars in a different key signature . In MuseScore 3: In top ribbon, select "Page View". Page Down to 2nd key signature.
To select a range of measures:
1. Click on a blank space in the first desired measure;
2. Hold down Shift, then click on a space in the last measure of the desired range.

Then select Tools → Remove Selected Range or press Ctrl + Del (Mac: ⌘ + Backspace )

#### Save as MusicXML:
Finally, save your edits with File>Export, Export To: MusicXML, Export... (or File > Save as and change file extension to .mxl). 

---

## Output


### Demonstration tune slice key analysis output  

Output from:

    python VeeHarmGen.py -m input/music/music.mxl -d DEMO
or 

    run_demo music


Chord summary:

* 100 ... ON_KEY, PEDAL, NEXT_INTERVAL, BASS
* 200 ... SUSPENDED2
* 300 ... MINOR, MAJOR
* 400 ... SUSPENDED4
* 500 ... FIFTH
* 600 ... SIXTH
* 700 ... SEVENTH
* 900 ... NINTH, ELEVENTH, THIRTEENTH

 Harmonic rhythms:
 
* BEAT1 = chord changes every beat
* BEAT2 = chord changes every couple of beats
* BAR1 = chord changes every measure
* BAR2 = chord changes every 2 measures
* BAR4 = chord changes every 4 measures

This may be manually edited to add or substitute other chords from other output files.

In your favourite file:
To edit a chord symbol double click on it.
To enter a chord symbol:
     Select a start note or rest; Press Ctrl + K (Mac: Cmd + K );
     Enter chord symbol e.g. Am7. Exit chord symbol mode by pressing Esc.

    
### Chord evaluation advice

The chord tones are the root 1, 3, 5, and 7th chords. 

The 2, 4, and 6 notes are called tensions. Tensions are non chord tones that can be used for embellishment. 
They sound best in the mid to high ranges. They should be used with caution and tested to avoid conflict in a chord structure. 
Sometimes a 6th tone is used instead of the 7th tone for a smoother sound.

The 7th tone of the scale works with the 3rd tone to bring out more of the chords character. 
The combination of the 3rd and 7th tones are called guide tones. 

### Cadence evaluation advice
There are three cadences, the Tonic, Subdominant and the Dominant.

Tonic cadences are used for stability and rest.

Subdominant cadences are used for motion but should resolve into a stronger chord (a dominant or a tonic).

Dominant chords can stand on their own and they sound great when resolving into tonic chords.

One of the very useful and powerful aspects of cadences is that chords of like cadences in the same key can be substituted for each other.
The I, III, and VI chords are tonic chords the can be substitutes for each other, The II,IV, and *VII chords can be substituted for each other.

The V and VII chords can be substututes for each other. The *VII (b-7b5 chord) has a dual function.
It can act as a subdominant chord when moving into a dominant chord. It can act as a dominant chord when moving a tonic chord.
Experiment with cadences in your chord progressions.



### MuseScore Track/Chord Volume
* View > Mixer (F10)
* At top of desired channel (with chords) click right arrow to show channels
* Expect display of 2 channels: normal and Chord syms.
* You can now adjust volume of the main track and chord symbols separately.


### Play output with Metronome
 If using MuseScore, you can add a metronome by
 View > Play Panel (F11 toggle) and  by Metronome, click the right icon for play metronome.

If output is corrupted in MuseScore 3.6.2, alternatively check the output in other score writing software e.g.
* https://my.avid.com/get/sibelius-first 

## ToolsForStyleCreation

To create your own input style files you need several musicxml (.mxl) files. 
Each file must contain a leadsheet melody with chord symbols above the staff. 


* "create_chord_map.py" analyses one song to create chord data files 
* Manually create a new style name directory and populate with chord data files from several songs
* "create_styles.py" merges the chord data from several songs to create one style

### Preparing input musicxml (.mxl) files with melody with chord symbols for create_chord_map.py

The instructions assume you have MuseScore 3.6.2.

If you have a midi file of the desired song:
* Open the .mid file with MuseScore
* View > Mixer F10 
* Start Playback
* In Mixer toggle "S" to solo each track to determine the name of the melody instrument e.g. Harpsichord

* Now see if the chords are available in chordify e.g.
* https://chordify.net/ log in, search for the song, click on the one with the most "jam sessions" that is CHORDIFIED. Click  Overview.
  (F11 full screen, screenshot, save)
* In MuseScore transpose to match chordify (e.g. Ctrl+A, Tools Transpose Chromatically, By Interval, Up, Perfect Fifth deselect transpose key signatures )

Assuming the harmony is correct in original MIDI file, add the chords to the melody track.
* To enter a chord symbol:
     Select a start note or rest; Press Ctrl + K (Mac: Cmd + K );
     Enter chord symbol e.g. Am7. Exit chord symbol mode by pressing Esc.
* To edit a chord symbol double click on it.

* Edit > Instruments (I)
* Select each stave, if not the melody stave, click "Remove from score", then click OK
* Rewind to start, Start Playback. Check only melody remains.
* File > Export, Musicxml, Export ...
* Choose directory e.g. VeeHarmGen\input\music\placeholder_chords or VeeHarmGen\private\input\music\placeholder_chords
* Rename e.g. Composer-Year-Song_Title

* Open the .mxl file with MuseScore


 
* Play chordify with MusScore to check match (open Volume Mixer to balance)
* Edit the musicxml (.mxl) files and remove unnecessary measures.
In MuseScore 3:

  * Remove a range of measures: Select a range of measures;
  Press Ctrl+Del (Mac: Cmd+Del).

* Save the changes (File > Export, Musicxml, Compressed, Export ...)

### Creating style chord data from song lead sheets in musicxml format

There is an example scripts to show how to create style chord data for VeeHarmGen on windows.

    create_example_style_1.cmd

This uses create_chord_map.py and create_styles.py.

The "create_chord_map.py" tool can analyse an mxl file to create chord data files (.json) representing the chords for that file.
By default the output is placed in the input/style directory.

Normal run inputs specified song file and outputs to input/style:

Note: ensure input filename does not contain spaces.

    create_chord_map.py -m input\music\placeholder_chords\berlinAlexandersRagtime.mxl
    create_chord_map.py -m input\music\placeholder_chords\fosterBrownHair.mxl

Now check the chord data file, e.g. XXX-_-ptc.json, contains the expected chords from 
input\music\placeholder_chords\XXX_normalised.mxl

If not, the input file may be corrupted and need recreating.

Note: although the song may appear to be incorrectly normalised, later VeeHarmGen.py will transpose the input tune similarly so the chords should match.

### Creating styles

Create a new style name directory e.g. traditional-1 in input/style.  

Move the desired individual (.json) chord data files to this directory e.g. traditional-1. 

Run create_styles.py which for each sub-directory in input/styles  
merges the .json files in the sub-directory and writes 
the style data in parent including the name of sub-directory in the output file name.
e.g. traditional-1-_-ptc.json

Normal run (which looks for populated style directories under input/styles) :

    create_styles.py

Run specifying a different directory (note: afterwards, you will need to 
manually copy .json files to input/styles ) :

    create_styles.py -i private/input/style
