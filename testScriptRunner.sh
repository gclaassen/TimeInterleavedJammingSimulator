# !/bin/bash

echo "Running Test 17/21: 0PRI_TT_modeRangeOnly"
python 2_code/main.py -i 0PRI_TT_modeRangeOnly -m 0.5 -z 0.5 -l 0.0 -j 0.0 -t

echo "Running Test 18/21: 0PRI_TT_MaZaLr"
python 2_code/main.py -i 0PRI_TT_MaZaLr -m 0.33 -z 0.33 -l 0.34 -j 0.0 -t

echo "Running Test 20/21: 0PRI_TT_levelModes"
python 2_code/main.py -i TT_0PRI -m 0.25 -z 0.25 -l 0.25 -j 0.25 -t

echo "Running Test 19/21: 0PRI_TT_onlyIJ"
python 2_code/main.py -i 0PRI_TT_onlyIJ -m 0.0 -z 0.0 -l 0.0 -j 1.0 -t

echo "Running Test 21/21: 0PRI_TT_highIJ"
python 2_code/main.py -i 0PRI_TT_highIJ -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 13/21: 10PRI_TT_highIJ"
python 2_code/main.py -i 10PRI_TT_highIJ -m 0.15 -z 0.05 -l 0.1 -j 0.7 -p -t

echo "Running Test 14/21: 05PRI_TT_highIJ"
python 2_code/main.py -i 05PRI_TT_highIJ -m 0.15 -z 0.05 -l 0.1 -j 0.7 -p -t

echo "Running Test 12/21: 0175PW_TT_highIJ"
python 2_code/main.py -i 0175PW_TT_highIJ -m 0.15 -z 0.05 -l 0.1 -j 0.7 -t

echo "Running Test 1/21: 0175PW_cutem_TT_highIJ"
python 2_code/main.py -i 0175PW_cutem_TT_highIJ -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c

echo "Running Test 15/21: 0PRI_TT_highIJ_ignoreBurnthrough"
python 2_code/main.py -i 0PRI_TT_highIJ_ignoreBurnthrough -m 0.15 -z 0.05 -l 0.1 -j 0.7 -b -t

echo "Running Test 16/21: 0175PW_cutem_TT_highIJ_ignoreBurnthrough"
python 2_code/main.py -i 0175PW_cutem_TT_highIJ_ignoreBurnthrough -m 0.15 -z 0.05 -l 0.1 -j 0.7 -b -c -t

echo "Running Test 2/21: 0175PW_cutem_5Radars"
python 2_code/main.py -i TT_0175PW_cutem_5Radars -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running  Test 3/21: 0175PW_cutem_10Radars"
python 2_code/main.py -i 0175PW_cutem_10Radars -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 4/21: 0175PW_cutem_15Radars"
python 2_code/main.py -i 0175PW_cutem_15Radars -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 5/21: 0175PW_cutem_TT_highIJ_CPI_over"
python 2_code/main.py -i 0175PW_cutem_TT_highIJ_CPI_over -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 6/21: 0175PW_cutem_TT_highIJ_CPI_under"
python 2_code/main.py -i 0175PW_cutem_TT_highIJ_CPI_under -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 7/21: 0175PW_cutem_TT_highIJ_Pd_over"
python 2_code/main.py -i 0175PW_cutem_TT_highIJ_Pd_over -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 8/21: 0175PW_cutem_TT_highIJ_Pd_under"
python 2_code/main.py -i 0175PW_cutem_TT_highIJ_Pd_under -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 9/21: 0175PW_cutem_TT_highIJ_Pfa_over"
python 2_code/main.py -i 0175PW_cutem_TT_highIJ_Pfa_over -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 10/21: 0175PW_cutem_TT_highIJ_Pfa_under"
python 2_code/main.py -i 0175PW_cutem_TT_highIJ_Pfa_under -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t

echo "Running Test 11/21: 0175PW_cutem_TT_highIJ_estimators"
python 2_code/main.py -i 0175PW_cutem_TT_highIJ_estimators -m 0.15 -z 0.05 -l 0.1 -j 0.7 -c -t