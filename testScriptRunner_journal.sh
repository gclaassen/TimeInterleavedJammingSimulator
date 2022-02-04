# !/bin/bash

# echo "Running Test 1/9: JournalRandomStart_TT_0PRI"
# python 2_code/main.py -i JournalRandomStart_TT_0PRI -m 0.5 -z 0.5 -l 0.0 -j 0.0 -t -r

# echo "Running Test 2/9: JournalRandomStart_TT_0PRI_ModeZaLr"
# python 2_code/main.py -i JournalRandomStart_TT_0PRI_ModeZaLr -m 0.33 -z 0.33 -l 0.34 -j 0.0 -t -r

# echo "Running Test 3/9: JournalRandomStart_TT_0PRI_modeTest"
# python 2_code/main.py -i JournalRandomStart_TT_0PRI_modeTest -m 0.25 -z 0.25 -l 0.25 -j 0.25 -t -r

# echo "Running Test 4/9: JournalRandomStart_TT_0PRI_IJonly"
# python 2_code/main.py -i JournalRandomStart_TT_0PRI_IJonly -m 0.0 -z 0.0 -l 0.0 -j 1.0 -t -r

# echo "Running Test 5/9: JournalRandomStart_TT_0PRI_IJhighest"
# python 2_code/main.py -i JournalRandomStart_TT_0PRI_IJhighest -m 0.15 -z 0.05 -l 0.1 -j 0.7 -t -r

echo "Running Test 6/9: JournalRandomStart_TT_10PRI"
python 2_code/main.py -i JournalRandomStart_TT_10PRI -m 0.15 -z 0.05 -l 0.1 -j 0.7 -p -t -r

echo "Running Test 7/9: JournalRandomStart_TT_05PRI"
python 2_code/main.py -i JournalRandomStart_TT_05PRI -m 0.15 -z 0.05 -l 0.1 -j 0.7 -p -t -r

echo "Running Test 8/9: JournalRandomStart_TT_0175PW"
python 2_code/main.py -i JournalRandomStart_TT_0175PW -m 0.15 -z 0.05 -l 0.1 -j 0.7 -t -r

echo "Running Test 9/9: JournalRandomStart_TT_0175PW_cutem"
python 2_code/main.py -i JournalRandomStart_TT_0175PW_cutem -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -r