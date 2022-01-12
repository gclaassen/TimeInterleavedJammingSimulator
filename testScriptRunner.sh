# !/bin/bash

echo "Running Test 1/21: TT_0PRI"
python 2_code/main.py -i TT_0PRI -m 0.5 -z 0.5 -l 0.0 -j 0.0 -t

echo "Running Test 2/21: TT_0PRI_ModeZaLr"
python 2_code/main.py -i TT_0PRI_ModeZaLr -m 0.33 -z 0.33 -l 0.34 -j 0.0 -t

echo "Running Test 3/21: TT_0PRI_modeTest"
python 2_code/main.py -i TT_0PRI_modeTest -m 0.25 -z 0.25 -l 0.25 -j 0.25 -t

echo "Running Test 4/21: TT_0PRI_IJonly"
python 2_code/main.py -i TT_0PRI_IJonly -m 0.0 -z 0.0 -l 0.0 -j 1.0 -t

echo "Running Test 5/21: TT_0PRI_IJhighest"
python 2_code/main.py -i TT_0PRI_IJhighest -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 6/21: TT_10PRI"
python 2_code/main.py -i TT_10PRI -m 0.15 -z 0.05 -l 0.1 -j 0.7 -p -t

echo "Running Test 7/21: TT_05PRI"
python 2_code/main.py -i TT_05PRI -m 0.15 -z 0.05 -l 0.1 -j 0.7 -p -t

echo "Running Test 8/21: TT_0175PW"
python 2_code/main.py -i TT_0175PW -m 0.15 -z 0.05 -l 0.1 -j 0.7 -t

echo "Running Test 9/21: TT_0175PW_cutem"
python 2_code/main.py -i TT_0175PW_cutem -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c

echo "Running Test 10/21: TT_0PRI_IJhighest_noBurnthrough"
python 2_code/main.py -i TT_0PRI_IJhighest_noBurnthrough -m 0.15 -z 0.05 -l 0.1 -j 0.7 -b -t

echo "Running Test 11/21: TT_0175PW_cutem_noBurnthrough"
python 2_code/main.py -i TT_0175PW_cutem_noBurnthrough -m 0.15 -z 0.05 -l 0.1 -j 0.7 -b -c -t

echo "Running Test 12/21: TT_0175PW_cutem_5Radars"
python 2_code/main.py -i TT_0175PW_cutem_5Radars -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running  Test 13/21: TT_0175PW_cutem_10Radars"
python 2_code/main.py -i TT_0175PW_cutem_10Radars -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 14/21: TT_0175PW_cutem_15Radars"
python 2_code/main.py -i TT_0175PW_cutem_15Radars -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 15/21: TT_0175PW_cutem_cpiOver"
python 2_code/main.py -i TT_0175PW_cutem_cpiOver -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 16/21: TT_0175PW_cutem_cpiUnder"
python 2_code/main.py -i TT_0175PW_cutem_cpiUnder -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 17/21: TT_0175PW_cutem_PdOver"
python 2_code/main.py -i TT_0175PW_cutem_PdOver -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 18/21: TT_0175PW_cutem_PdUnder"
python 2_code/main.py -i TT_0175PW_cutem_PdUnder -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 19/21: TT_0175PW_cutem_PfaOver"
python 2_code/main.py -i TT_0175PW_cutem_PfaOver -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 20/21: TT_0175PW_cutem_PfaUnder"
python 2_code/main.py -i TT_0175PW_cutem_PfaUnder -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 21/21: TT_0175PW_cutem_Estimators"
python 2_code/main.py -i TT_0175PW_cutem_Estimators -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t