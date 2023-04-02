mkdir input\style\example_style_1
echo --- delete current individual song style data for this style example_style_1 --- 
del input\style\example_style_1\*.json

echo --- "create_chord_map.py" analyses a song to create chord data files --- 
create_chord_map.py -m input\music\placeholder_chords\example_style_1\Cairo.mxl -o input/style/example_style_1/
create_chord_map.py -m input\music\placeholder_chords\example_style_1\Love_Stand_Strong.mxl -o input/style/example_style_1/
create_chord_map.py -m input\music\placeholder_chords\example_style_1\Perambulate.mxl -o input/style/example_style_1/

echo --- Now check the chord data files in input\style\example_style_1 e.g. SONG1-_-ptc.json, 
echo --- contains the expected chords from SONG1_normalised.mxl
echo --- If not, try re-assembling the lead sheet or running fix_musicxml_chord_symbols.py on song

echo --- "create_styles.py" merges the chord data from several songs to create one style --- 
create_styles.py -i input/style


