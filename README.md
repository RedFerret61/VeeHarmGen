# VeeHarmGen
VeeHarmGen is a Vertical Harmony Generation program that 
takes an input musicxml file containing a melody and 
creates output musicxml files with added Chord Symbols.
These can be played back and edited in scorewriter programs
such as MuseScore 3.6.2.

The latest release has been tested on: 
* Windows 10.0.19044
  - with MuseScore 3.6.2, Python 3.9.6, music21 v 7.1.0 
* Ubuntu 20.04
  - with MuseScore 3.2.3, Python 3.8.10, music21 v 7.1.0

**Table of Contents**

1. [VeeHarmGen Installation instructions for Windows](#VeeHarmGen Installation instructions for Windows)
2. [VeeHarmGen Installation instructions for macOS](#VeeHarmGen Installation instructions for macOS)
3. [VeeHarmGen Installation instructions for Ubuntu](#VeeHarmGen Installation instructions for Ubuntu)
4. [Input Music](#Input Music)
5. [Output](#Output)


*Note: GitHub has a full table of contents with links in the header icon (top left of the readme.md).*

---

## VeeHarmGen Installation instructions for Windows
Pre-requisites for VeeHarmGen include MuseScore, Python, and Music21.

### MuseScore Windows installation
Browse to https://musescore.org/en/download
 
Download for Windows and run installer.
### Python Windows installation
 1. Firstly check python version required by Music21.
 see https://web.mit.edu/music21/doc/installing/installWindows.html

      in October 2021 this stated  "Windows users should download and install Python version 3.8 or higher."
* For example
  * Python 3.9.6 worked for me with music21 versions 6.7.1 and 7.1.0 
  * Python 3.10.0 did not work for me with music21 version 7.1.0 (numpy not compatible)

2. Browse to https://www.python.org/downloads/windows
    
    Download desired version (may not be the latest) and run.
    
    Select "Add Python to PATH". Install.


3. Check it works: Start, search, cmd, click on Command Prompt, type:
   
    python --version

    Expect the version to be displayed e.g. Python 3.9.6

### Music21 Windows installation
 
1. Music21 Installation details at https://web.mit.edu/music21/doc/installing/installWindows.html

    At command prompt:

    pip install music21

3. Check music21 version installed with:

   pip list

4. Configure with (press return to accept defaults):

   python -m music21.configure

if you have problems and want to try different versions. Uninstall music21 with:

   pip uninstall music21

Uninstall Python by opening Control Panel, Click "Uninstall a Program", Scroll down to Python and click uninstall for each version you don't want anymore.

To upgrade music21 at a later date to the latest version, 'pip uninstall music21' then 'pip install music21' again.

### VeeHarmGen Windows installation

#### Install VeeHarmGen on Windows
 Download release zip to desired directory for VeeHarmGen and unzip with right click Extract All ...
#### Run VeeHarmGen on Windows 

 In a Command Prompt window change to install directory and show VeeHarmGen help e.g.:

    cd C:\Users\paul\Documents\VeeHarmGen

    VeeHarmGen.py -h
    :: or
    python VeeHarmGen.py -h

Then run using default input music music.xml:

    VeeHarmGen.py
    :: or
    python VeeHarmGen.py
    :: or to run with different input music e.g. JingleBells-2_2.mxl
    python VeeHarmGen.py -m input/music/JingleBells-2_2.mxl

 This runs several key analysers on input music melody slices and 
 produces various output files with different chords and 
 harmonic rhythms.  

#### Output description
 
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

Example workflow after running VeeHarmGen:

* Choose a favourite output e.g. ON_KEY chords with a BAR1 harmonic rhythm.
* Audition other chord outputs e.g. SEVENTH. 
* If a chord suits that part of the melody, 
add it individually to your favourite output, by manual editing. 
 

 
    output = output\music-100-ON_KEY_MOST-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-100-ON_KEY_MOST-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-100-ON_KEY_MOST-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-100-ON_KEY_MOST-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-100-ON_KEY_MOST-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-101-ON_KEY_LEAST-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-101-ON_KEY_LEAST-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-101-ON_KEY_LEAST-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-101-ON_KEY_LEAST-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-101-ON_KEY_LEAST-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-102-ON_KEY_FIRST-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-102-ON_KEY_FIRST-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-102-ON_KEY_FIRST-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-102-ON_KEY_FIRST-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-102-ON_KEY_FIRST-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-103-ON_KEY_LAST-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-103-ON_KEY_LAST-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-103-ON_KEY_LAST-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-103-ON_KEY_LAST-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-103-ON_KEY_LAST-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-111-PEDAL-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-111-PEDAL-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-111-PEDAL-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-111-PEDAL-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-111-PEDAL-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-123-NEXT_INTERVAL_SECOND_OR_THIRD-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-123-NEXT_INTERVAL_SECOND_OR_THIRD-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-123-NEXT_INTERVAL_SECOND_OR_THIRD-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-123-NEXT_INTERVAL_SECOND_OR_THIRD-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-123-NEXT_INTERVAL_SECOND_OR_THIRD-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-145-NEXT_INTERVAL_FOURTH_OR_FIFTH-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-145-NEXT_INTERVAL_FOURTH_OR_FIFTH-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-145-NEXT_INTERVAL_FOURTH_OR_FIFTH-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-145-NEXT_INTERVAL_FOURTH_OR_FIFTH-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-145-NEXT_INTERVAL_FOURTH_OR_FIFTH-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-167-NEXT_INTERVAL_SIXTH_OR_SEVENTH-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-167-NEXT_INTERVAL_SIXTH_OR_SEVENTH-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-167-NEXT_INTERVAL_SIXTH_OR_SEVENTH-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-167-NEXT_INTERVAL_SIXTH_OR_SEVENTH-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-167-NEXT_INTERVAL_SIXTH_OR_SEVENTH-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-174-DESCENDING_BASS_TETRA-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-174-DESCENDING_BASS_TETRA-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-174-DESCENDING_BASS_TETRA-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-174-DESCENDING_BASS_TETRA-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-174-DESCENDING_BASS_TETRA-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-175-DESCENDING_CHROMATIC_BASS_TETRA-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-175-DESCENDING_CHROMATIC_BASS_TETRA-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-175-DESCENDING_CHROMATIC_BASS_TETRA-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-175-DESCENDING_CHROMATIC_BASS_TETRA-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-175-DESCENDING_CHROMATIC_BASS_TETRA-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-176-DESCENDING_BASS-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-176-DESCENDING_BASS-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-176-DESCENDING_BASS-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-176-DESCENDING_BASS-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-176-DESCENDING_BASS-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-177-DESCENDING_CHROMATIC_BASS-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-177-DESCENDING_CHROMATIC_BASS-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-177-DESCENDING_CHROMATIC_BASS-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-177-DESCENDING_CHROMATIC_BASS-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-177-DESCENDING_CHROMATIC_BASS-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-181-ASCENDING_BASS_TETRA_1-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-181-ASCENDING_BASS_TETRA_1-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-181-ASCENDING_BASS_TETRA_1-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-181-ASCENDING_BASS_TETRA_1-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-181-ASCENDING_BASS_TETRA_1-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-182-ASCENDING_BASS_TETRA_2-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-182-ASCENDING_BASS_TETRA_2-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-182-ASCENDING_BASS_TETRA_2-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-182-ASCENDING_BASS_TETRA_2-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-182-ASCENDING_BASS_TETRA_2-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-183-ASCENDING_BASS_TETRA_3-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-183-ASCENDING_BASS_TETRA_3-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-183-ASCENDING_BASS_TETRA_3-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-183-ASCENDING_BASS_TETRA_3-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-183-ASCENDING_BASS_TETRA_3-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-200-SUSPENDED2-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-200-SUSPENDED2-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-200-SUSPENDED2-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-200-SUSPENDED2-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-200-SUSPENDED2-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-202-ADD2-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-202-ADD2-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-202-ADD2-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-202-ADD2-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-202-ADD2-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-300-MINOR-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-300-MINOR-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-300-MINOR-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-300-MINOR-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-300-MINOR-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-301-MAJOR-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-301-MAJOR-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-301-MAJOR-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-301-MAJOR-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-301-MAJOR-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-400-SUSPENDED4-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-400-SUSPENDED4-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-400-SUSPENDED4-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-400-SUSPENDED4-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-400-SUSPENDED4-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-404-ADD4-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-404-ADD4-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-404-ADD4-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-404-ADD4-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-404-ADD4-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-500-FIFTH-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-500-FIFTH-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-500-FIFTH-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-500-FIFTH-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-500-FIFTH-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-600-SIXTH-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-600-SIXTH-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-600-SIXTH-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-600-SIXTH-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-600-SIXTH-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-606-ADDSIXTH-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-606-ADDSIXTH-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-606-ADDSIXTH-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-606-ADDSIXTH-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-606-ADDSIXTH-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-700-SEVENTH-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-700-SEVENTH-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-700-SEVENTH-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-700-SEVENTH-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-700-SEVENTH-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-900-NINTH-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-900-NINTH-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-900-NINTH-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-900-NINTH-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-900-NINTH-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-911-ELEVENTH-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-911-ELEVENTH-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-911-ELEVENTH-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-911-ELEVENTH-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-911-ELEVENTH-BAR4-2022_03_23-16_32_28.mxl
    output = output\music-913-THIRTEENTH-BEAT1-2022_03_23-16_32_28.mxl
    output = output\music-913-THIRTEENTH-BEAT2-2022_03_23-16_32_28.mxl
    output = output\music-913-THIRTEENTH-BAR1-2022_03_23-16_32_28.mxl
    output = output\music-913-THIRTEENTH-BAR2-2022_03_23-16_32_28.mxl
    output = output\music-913-THIRTEENTH-BAR4-2022_03_23-16_32_28.mxl

Now in Musescore, open desired output file, e.g. ...100-ON_KEY_MOST-BAR1... , play and choose favourite file.
This may be manually edited to add or substitute other chords from other output files.

In your favourite file:
To edit a chord symbol double click on it.
To enter a chord symbol:
     Select a start note or rest; Press Ctrl + K (Mac: Cmd + K );
     Enter chord symbol e.g. Am7. Exit chord symbol mode by pressing Esc.

    
### Chord advice

The chord tones are the root 1, 3, 5, and 7th chords. 

The 2, 4, and 6 notes are called tensions. Tensions are non chord tones that can be used for embellishment. 
They sound best in the mid to high ranges. They should be used with caution and tested to avoid conflict in a chord structure. 
Sometimes a 6th tone is used instead of the 7th tone for a smoother sound.

The 7th tone of the scale works with the 3rd tone to bring out more of the chords character. 
The combination of the 3rd and 7th tones are called guide tones. 

### Cadence advice
There are three cadences, the Tonic, Subdominant and the Dominant.

Tonic cadences are used for stability and rest.

Subdominant cadences are used for motion but should resolve into a stronger chord (a dominant or a tonic).

Dominant chords can stand on their own and they sound great when resolving into tonic chords.

One of the very useful and powerful aspects of cadences is that chords of like cadences in the same key can be substituted for each other.
The I, III, and VI chords are tonic chords the can be substitutes for each other, The II,IV, and *VII chords can be substituted for each other.

The V and VII chords can be substututes for each other. The *VII (b-7b5 chord) has a dual function.
It can act as a subdominant chord when moving into a dominant chord. It can act as a dominant chord when moving a tonic chord.
Experiment with cadences in your chord progressions.


 

---

## VeeHarmGen Installation instructions for macOS
Pre-requisites for VeeHarmGen include MuseScore, Python, and Music21.

### MuseScore on macOS
See https://musescore.org/en/handbook/3/install-macos  

 1. Download for mac from https://musescore.org/en/download
 2. Double-click the DMG file to mount the disk image.
 3. Drag and drop the MuseScore icon to the Applications folder icon.
 4. Launch MuseScore from the Applications folder to complete setup.

### Python on macOS:
 1. Firstly check python version required by Music21.
see https://web.mit.edu/music21/doc/installing/installMac.html
in December 2021 this recommended Python 3.9 or later.

 2. Use https://docs.python.org/3/using/mac.html and https://www.python.org/downloads/macos/
 3. To check the installed version of python, click the Launchpad icon in the Dock, type Terminal in the search field, then click Terminal. Then type:
    

    python3 --version
    Python 3.10.0



### Music21 on macOS
 

1. Install Music21. In a Terminal type:


        pip3 install music21


2. Check music21 version installed with:

       pip3 list



#### Install VeeHarmGen on macOS
 Download release zip to desired directory for VeeHarmGen and unzip by double-clicking on the zipped file .
#### Run VeeHarmGen on macOS

 In command prompt change to install directory, make run files executable and run VeeHarmGen e.g.:

 ```  
 cd ~/VeeHarmGen
 
 # display help    
 python3 VeeHarmGen.py -h
 
 # run with default input music 
 python3 VeeHarmGen.py
 
 # run with different input music e.g. JingleBells-2_2.mxl
 python3 VeeHarmGen.py -m input/music/JingleBells-2_2.mxl
 
```

See "Run VeeHarmGen on Windows" for an output description.


---

## VeeHarmGen Installation instructions for Ubuntu
Pre-requisites for VeeHarmGen include MuseScore, Python, and Music21.

### MuseScore on Ubuntu
 1. Install MuseScore via the command line:
   

    sudo add-apt-repository ppa:mscore-ubuntu/mscore3-stable
    sudo apt-get update
    sudo apt install musescore3

Note: If you use Ubuntu Software to install MuseScore, music21 will not find the MuseScore snap location. 

2. Activities, search MuseScore, click on MuseScore to complete setup.

### Python on Ubuntu:
 1. Firstly check python version required by Music21.
see https://web.mit.edu/music21/doc/installing/installLinux.html
in October 2021 this stated Music21 requires Python 3.7+.

 2. Check default installed version of python Ctrl+Alt+T
    

    python3 --version
    Python 3.8.10

The default python on Ubuntu 20.04 is compatible.


### Music21 on Ubuntu
 
1. If the package installer for Python (pip3) is not yet installed, in terminal :

       sudo apt install python3-pip


2. Install Music21


        pip3 install music21

Ignore Fortran to Python warning:  WARNING: The scripts f2py, f2py3 and f2py3.8 are installed in 
    '/home/admin3/.local/bin' which is not on PATH.
  Consider adding this directory to PATH or, if you prefer to suppress this warning, 
  use --no-warn-script-location.



3. Check music21 version installed with:

       pip3 list



#### Install VeeHarmGen on Ubuntu
 Download release zip to desired directory for VeeHarmGen and unzip.
#### Run VeeHarmGen on Ubuntu

 In command prompt change to install directory and run VeeHarmGen e.g.:

 ```  
 cd ~/pycharm     

  # display help    
 python3 VeeHarmGen.py -h
 
 # run with default input music 
 python3 VeeHarmGen.py
 
 # run with different input music e.g. JingleBells-2_2.mxl
 python3 VeeHarmGen.py -m input/music/JingleBells-2_2.mxl
```

See "Run VeeHarmGen on Windows" for an output description.



---

## Input Music
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




