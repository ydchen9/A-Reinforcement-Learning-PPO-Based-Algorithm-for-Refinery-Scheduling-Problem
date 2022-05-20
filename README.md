# A-Reinforcement-Learning-PPO-Based-Algorithm-for-Refinery-Scheduling-Problem
A Reinforcement Learning Based Algorithm for Refinery Scheduling Algorithm

The case study is running in the platform of on the Python2.7 platform on the Windows 7 system, which is set in a computer with Intel Core i7-3770 CPU@ 3.40GHz 3.40GHz, 32GB. Furthermore, the CPLEX 12.6.0 solver and the deep learning Library PaddlePaddle 1.8.4 are used.

1. The TRL algorithm training files are all included in "policy-train-files.zip". 
2. The file of test_18case_DPSO.xls is the cases in Table V of the manuscript.
3. The file of test_18case_DPSO_2.xls is the cases in Table VIII of the manuscript.
4. The file of Slove_processing9_4_RL3.py is the mian file for the TRL algorithm to solve the large-scale refinery scheduling problem. When runing the program, the case file must be specified first in the line 1969: book = xlrd.open_workbook("test_18case_DPSO_2.xls"). The files of "refinery_1MiniS_211_0FS3.py" and "refinery_1MiniS_211_0.py" are two imported files for this main file. The "refinery_1MiniS_211_0FS3.py" is used to solve the whole scheduling problem with a given schedule, which can evaluate the quality of the given scheduling plan. The "refinery_1MiniS_211_0.py" is used to solve the whole scheduling problem by the CPLEX slover. After each case solved by TRL in Slove_processing9_4_RL3.py, the CPLEX solver will be called to solve the same case. You can set the solving time for CPLEX solver in lines 2362-2374. The file of Slove_processing9_4_RL3_needed files.zip is the network data needed in the main program file.
5. The file of PRO_DPSO.py is the main program for DPSO to solve the large-scale refinery scheduling problem. The PRO_FS2.py is a imported file of this main program. The needed file for this program is too big and thus in another website, which can be obtained by the link: https://pan.baidu.com/s/1k6hHDxErqa71iPAc5u5tug Extraction code: 8m7m.
6. The file of Slove_processing9_3.py is the main program for KTA to solve the large-scale refinery scheduling problem. 

