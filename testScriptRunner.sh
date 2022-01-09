# !/bin/bash

echo "Running Test 1/19: TT_0175PW_cutem"
python 2_code/main.py -i TT_0175PW_cutem -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c

echo "Running Test 2/19: TT_0175PW_cutem_5Radars"
python 2_code/main.py -i TT_0175PW_cutem_5Radars -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c 

echo "Running  Test 3/19: TT_0175PW_cutem_10Radars"
python 2_code/main.py -i TT_0175PW_cutem_10Radars -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c 

echo "Running Test 4/19: TT_0175PW_cutem_15Radars"
python 2_code/main.py -i TT_0175PW_cutem_15Radars -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c 

echo "Running Test 5/19: TT_0175PW_cutem_cpiOver"
python 2_code/main.py -i TT_0175PW_cutem_cpiOver -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c 

echo "Running Test 6/19: TT_0175PW_cutem_cpiUnder"
python 2_code/main.py -i TT_0175PW_cutem_cpiUnder -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c 

echo "Running Test 7/19: TT_0175PW_cutem_PdOver"
python 2_code/main.py -i TT_0175PW_cutem_PdOver -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c 

echo "Running Test 8/19: TT_0175PW_cutem_PdUnder"
python 2_code/main.py -i TT_0175PW_cutem_PdUnder -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c 

echo "Running Test 9/19: TT_0175PW_cutem_PfaOver"
python 2_code/main.py -i TT_0175PW_cutem_PfaOver -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c 

echo "Running Test 10/19: TT_0175PW_cutem_Estimators"
python 2_code/main.py -i TT_0175PW_cutem_Estimators -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c

echo "Running Test 11/19: TT_0175PW"
python 2_code/main.py -i TT_0175PW -m 0.15 -z 0.05 -l 0.1 -j 0.7 

echo "Running Test 12/19: TT_10PRI"
python 2_code/main.py -i TT_10PRI -m 0.15 -z 0.05 -l 0.1 -j 0.7 -p 

echo "Running Test 13/19: TT_05PRI"
python 2_code/main.py -i TT_05PRI -m 0.15 -z 0.05 -l 0.1 -j 0.7 -p 

echo "Running Test 14/19: TT_0PRI_IJonly"
python 2_code/main.py -i TT_0PRI_IJonly -m 0.0 -z 0.0 -l 0.0 -j 1.0 

echo "Running Test 15/19: TT_0PRI_ModeZaLr"
python 2_code/main.py -i TT_0PRI_ModeZaLr -m 0.33 -z 0.33 -l 0.34 -j 0.0 

echo "Running Test 16/19: TT_0PRI"
python 2_code/main.py -i TT_0PRI -m 0.25 -z 0.25 -l 0.25 -j 0.25 

echo "Running Test 17/19: TT_0175PW_cutem"
python 2_code/main.py -i TT_0175PW_cutem -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c 

echo "Running Test 18/19: TT_0PRI_IJhighest_noBurnthrough"
python 2_code/main.py -i TT_0PRI_IJhighest_noBurnthrough -m 0.15 -z 0.05 -l 0.1 -j 0.7 -b 

echo "Running Test 19/19: TT_0175PW_cutem_noBurnthrough"
python 2_code/main.py -i TT_0175PW_cutem_noBurnthrough -m 0.15 -z 0.05 -l 0.1 -j 0.7 -b -c