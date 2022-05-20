import numpy as np
# import PRO_FS_noT as PRO_ini
import PRO_FS2 as PRO
from tabulate import tabulate
import xlwt
import xlrd
import time

# Five Units: ATM 0; VDU 1; FCCU 2; HTU1 3; HTU2 4;
unit_num = 5
unitlist = range(unit_num)
TTlist = [3,3,2,1,1]
mode_unit = [2,2,4,2,2]
mode_num = 4
modelist = range(mode_num)

numO = 8
numO_g = 5
numO_d = 3
numOC = 8
numOC_g = 5
numOC_d = 3
OClist = range(numOC)
Olist = range(numO)

w = 0.9
c1 = 0.4
c2 = 0.4

def mutation(u, slot_num, MNMS_mu):
    max_T_mu = max(MNMS_mu)
    ind_mode_mu = np.ones(max_T_mu+1)*(-1)
    ind_mode_tran_pos_mu = np.ones(max_T_mu+2)*(-1)
    ind_tran_num_mu = np.random.randint(0, MNMS_mu[u]+1, 1)
    if ind_tran_num_mu == 0:
        ind_mode_mu[0] = np.random.randint(0, mode_unit[u], 1)
    else:
        ind_mode_mu[0] = np.random.randint(0, mode_unit[u], 1)
        AA = ind_mode_mu[0]
        for j in range(int(ind_tran_num_mu)):
            V = 0
            while V == 0:
                AA_ = np.random.randint(0, mode_unit[u], 1)
                if AA_ != AA:
                    ind_mode_mu[j+1] = AA_
                    AA = AA_
                    V = 1
    if ind_tran_num_mu != 0:
        for posi in range(int(ind_tran_num_mu)):
            if posi == 0:
                ind_mode_tran_pos_mu[1] = np.random.randint(1, slot_num - ind_tran_num_mu*(TTlist[u]+1)+1,1)
            else:
                ind_mode_tran_pos_mu[posi+1] = \
                    np.random.randint(ind_mode_tran_pos_mu[posi]+TTlist[u]+1, slot_num-(ind_tran_num_mu-posi)*(TTlist[u]+1)+1,1)
        ind_mode_tran_pos_mu[0] = 0
        ind_mode_tran_pos_mu[posi+2] = slot_num
    else:
        ind_mode_tran_pos_mu[0] = 0
        ind_mode_tran_pos_mu[1] = slot_num
    # Constructing solutions.
    ind_solution_mu = np.zeros((slot_num, mode_num))
    for i in indlist:
        for u in unitlist:
            for posi in range(int(ind_tran_num_mu)+1):
                modetype = np.zeros(mode_num)
                modetype[ind_mode_mu[posi].astype(int)] = 1
                ind_solution_mu[ind_mode_tran_pos_mu[posi].astype(int):ind_mode_tran_pos_mu[posi+1].astype(int),:] = \
                    np.tile(modetype.reshape((1,mode_num)), (ind_mode_tran_pos_mu[posi+1].astype(int)-ind_mode_tran_pos_mu[posi].astype(int),1))
    return ind_solution_mu

def PSO(numT,Tlist,numL1,Llist1,DS1,DV1,Pri,NCmax,run_time,DS_num,OCtank_ini, Otank_ini,runtime,case_times):
    # book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    timestart = time.time()
    slot_num = numT
    slotlist = range(slot_num)
    MNMS = [0] * unit_num
    for i in unitlist:
        MNMS[i] = int((slot_num - 1)/(TTlist[i] + 1))
    print "MNMS:",MNMS
    max_T = max(MNMS)
    mode_RF_MTBE_ini = np.tile([0]*slot_num,(2,mode_num,1))
    mode_RF_MTBE = np.tile([1,0,0,0],(2,ind_num,slot_num,1))
    # Initialization
    ind_tran_num = np.zeros((ind_num, unit_num))
    ind_mode = np.ones((ind_num, unit_num, max_T+1))*(-1)
    ind_mode_tran_pos = np.ones((ind_num, unit_num, max_T+2))*(-1)
    ind_solution = np.zeros((ind_num, unit_num, slot_num, mode_num))
    for u in unitlist:
        ind_tran_num[:,u] = np.random.randint(0, MNMS[u]+1, ind_num)
    # print "ind_tran_num:",ind_tran_num
    for i in indlist:
        for u in unitlist:
            if ind_tran_num[i,u] == 0:
                ind_mode[i, u, 0] = np.random.randint(0, mode_unit[u], 1)
            else:
                ind_mode[i, u, 0] = np.random.randint(0, mode_unit[u], 1)
                AA = ind_mode[i, u, 0]
                for j in range(int(ind_tran_num[i, u])):
                    V = 0
                    while V == 0:
                        AA_ = np.random.randint(0, mode_unit[u], 1)
                        if AA_ != AA:
                            ind_mode[i, u, j+1] = AA_
                            AA = AA_
                            V = 1
    # print "ind_mode:",ind_mode
    for i in indlist:
        for u in unitlist:
            if ind_tran_num[i,u] != 0:
                for posi in range(int(ind_tran_num[i, u])):
                    if posi == 0:
                        ind_mode_tran_pos[i,u,1] = np.random.randint(1, slot_num - ind_tran_num[i,u]*(TTlist[u]+1)+1,1)
                    else:
                        ind_mode_tran_pos[i,u,posi+1] = \
                            np.random.randint(ind_mode_tran_pos[i,u,posi]+TTlist[u]+1, slot_num-(ind_tran_num[i,u]-posi)*(TTlist[u]+1)+1,1)
                ind_mode_tran_pos[i, u, 0] = 0
                ind_mode_tran_pos[i, u, posi+2] = slot_num
            else:
                ind_mode_tran_pos[i, u, 0] = 0
                ind_mode_tran_pos[i, u, 1] = slot_num
    # print "ind_mode_tran_pos:",ind_mode_tran_pos
    # Constructing solutions.
    for i in indlist:
        for u in unitlist:
            for posi in range(int(ind_tran_num[i, u])+1):
                modetype = np.zeros(mode_num)
                modetype[int(ind_mode[i,u,posi])] = 1
                ind_solution[i,u,ind_mode_tran_pos[i,u,posi].astype(int):ind_mode_tran_pos[i,u,posi+1].astype(int),:] = \
                    np.tile(modetype.reshape((1,mode_num)), (ind_mode_tran_pos[i,u,posi+1].astype(int)-ind_mode_tran_pos[i,u,posi].astype(int),1))
    # Solving the individuals
    solution_cplex = np.insert(ind_solution.swapaxes(0,1), 3, np.tile(ind_solution.swapaxes(0,1)[2, :, :, :],(2,1,1,1)),axis=0)  # add mode of ETH and HDS units
    solution_cplex = np.concatenate((solution_cplex, mode_RF_MTBE), axis=0)  # add mode of RF and MTBE units
    solution_cplex = np.swapaxes(solution_cplex, 2, 3)
    ind_objective = [0]*ind_num
    for i in indlist:
        # M_header = range(slot_num)
        # M_header.insert(0, "M")
        # M_table_ = [0] * (slot_num + 1)
        # M_table = []
        # for U in range(9):
        #     M_table.append(M_table_[:])
        # M_table[0][0] = "ATM"
        # M_table[1][0] = "VDU"
        # M_table[2][0] = "FCCU"
        # M_table[3][0] = "ETH"
        # M_table[4][0] = "HDS"
        # M_table[5][0] = "HTU1"
        # M_table[6][0] = "HTU2"
        # M_table[7][0] = "RF"
        # M_table[8][0] = "MTBE"
        # for U in range(9):
        #     for T in slotlist:
        #         for Mode in modelist:
        #             if solution_cplex[:, i, :, :].reshape((unit_num + 4) * slot_num * mode_num).tolist()[
        #                                                 U * mode_num * slot_num + Mode * slot_num + T] >= 0.1:
        #                 M_table[U][T + 1] = Mode
        #                 break
        #             elif Mode == 3:
        #                 M_table[U][T + 1] = "N/A"
        # print tabulate(M_table, M_header, tablefmt="simple", numalign="center", floatfmt=".1f")
        ind_objective[i] = PRO.PRO_opt(numT, Tlist, numL1, Llist1, DS1, DV1, DS_num,OCtank_ini, Otank_ini, Pri,
                                       solution_cplex[:,i,:,:].reshape((unit_num + 4) * slot_num * mode_num).tolist())
    ind_sort = np.argsort(ind_objective)
    ind_gb_objective = ind_objective[ind_sort[0]]
    ind_gbest = np.copy(ind_solution[ind_sort[0]])
    ind_pb_objective = np.copy(ind_objective)
    ind_pbest = np.copy(ind_solution)
    # PSO processing
    NC = 0
    bestNC = -1
    bb = 0
    while NC < NCmax:
        # Record the iteration process.
        # sheet = book.add_sheet('NC'+str(NC), cell_overwrite_ok=True)
        # ind_solution_max = np.argmax(ind_solution,axis=3)
        # sheet.write(0, 0, "NC"+str(NC))
        # for u in unitlist:
        #     for s in slotlist:
        #         sheet.write(0, u*slot_num+s+1, "U"+str(u)+"s"+str(s))
        # for i in indlist:
        #     sheet.write(i+1, 0, "Ind_"+str(i))
        #     for u in unitlist:
        #         for s in slotlist:
        #             sheet.write(i+1, u*slot_num+s+1, int(ind_solution_max[i,u,s]))
        for i in indlist:
            w_prob = np.random.rand()
            if w_prob < w:
                choose_unit = np.random.randint(0,unit_num,1)
                ind_solution[i,choose_unit,:,:] = mutation(choose_unit.astype(int)[0],slot_num,MNMS)
            c1_prob = np.random.rand()
            if c1_prob < c1:
                choose_unit = np.random.randint(0,unit_num,1)
                ind_solution[i, choose_unit, :, :] = np.copy(ind_gbest[choose_unit])
            c2_prob = np.random.rand()
            if c2_prob < c2:
                choose_unit = np.random.randint(0,unit_num,1)
                ind_solution[i, choose_unit, :, :] = np.copy(ind_pbest[i,choose_unit,:,:])
        # Solving the individuals
        solution_cplex = np.insert(ind_solution.swapaxes(0,1), 3, np.tile(ind_solution.swapaxes(0,1)[2, :, :, :],(2,1,1,1)),axis=0)  # add mode of ETH and HDS units
        solution_cplex = np.concatenate((solution_cplex, mode_RF_MTBE), axis=0)  # add mode of RF and MTBE units
        solution_cplex = np.swapaxes(solution_cplex, 2, 3)
        for i in indlist:
            print "NC now =", NC, "    case num:",case_times
            print "Best Solution:  NC=", bestNC
            print "Best Solution: ", ind_gb_objective
            timeend = time.time() - timestart
            print "time cost:", timeend
            ind_objective[i] = PRO.PRO_opt(numT, Tlist, numL1, Llist1, DS1, DV1, DS_num,OCtank_ini, Otank_ini, Pri,
                                           solution_cplex[:,i,:,:].reshape((unit_num + 4) * slot_num * mode_num).tolist())
            if ind_objective[i] < ind_pb_objective[i]:
                ind_pb_objective[i] = ind_objective[i]
                ind_pbest[i] = np.copy(ind_solution[i])
                # M_header = range(slot_num)
                # M_header.insert(0, "M")
                # M_table_ = [0] * (slot_num + 1)
                # M_table = []
                # for U in range(9):
                #     M_table.append(M_table_[:])
                # M_table[0][0] = "ATM"
                # M_table[1][0] = "VDU"
                # M_table[2][0] = "FCCU"
                # M_table[3][0] = "ETH"
                # M_table[4][0] = "HDS"
                # M_table[5][0] = "HTU1"
                # M_table[6][0] = "HTU2"
                # M_table[7][0] = "RF"
                # M_table[8][0] = "MTBE"
                # for U in range(9):
                #     for T in slotlist:
                #         for Mode in modelist:
                #             if solution_cplex[:,i,:,:].reshape((unit_num + 4) * slot_num * mode_num).tolist()[U * mode_num * slot_num + Mode * slot_num + T] >= 0.1:
                #                 M_table[U][T + 1] = Mode
                #                 break
                #             elif Mode == 3:
                #                 M_table[U][T + 1] = "N/A"
                # print tabulate(M_table, M_header, tablefmt="simple", numalign="center", floatfmt=".1f")
            if time.time() - timestart > runtime:
                bb = 1
                break
        if bb == 1:
            break
        ind_sort = np.argsort(ind_objective)
        if ind_objective[ind_sort[0]] < ind_gb_objective:
            ind_gb_objective = ind_objective[ind_sort[0]]
            ind_gbest = np.copy(ind_solution[ind_sort[0]])
            bestNC = NC
        NC += 1

        ind_gbest_max = np.argmax(ind_gbest, axis=2)
    #     sheet.write(ind_num+2+1, 0, "NCbest")
    #     sheet.write(ind_num+2+2, 0, "NC" + str(bestNC))
    #     for u in unitlist:
    #         for s in slotlist:
    #             sheet.write(ind_num+2+1, u * slot_num + s + 1, "U" + str(u) + "s" + str(s))
    #             sheet.write(ind_num+2 + 2, u * slot_num + s + 1, int(ind_gbest_max[u, s]))
    #     sheet.write(ind_num+2+3, 0, "bestObj")
    #     sheet.write(ind_num+2+3, 1, float(ind_gb_objective))
    # book.save('PRO_PSO_ZhangL_30s999'+str(run_time)+'.xls')
    print "best objective:",ind_gb_objective
    timeend = time.time() - timestart
    print "time cost:", timeend
    # M = np.insert(ind_gbest, 3, np.tile(ind_gbest[2, :, :], (2, 1, 1)), axis=0)  # add mode of ETH and HDS units
    # M = np.swapaxes(M, 1, 2)
    # M = np.concatenate((M, mode_RF_MTBE_ini), axis=0)  # add mode of RF and MTBE units
    # M = M.reshape((unit_num + 4) * mode_num * slot_num).tolist()
    # M_header = range(slot_num)
    # M_header.insert(0, "M")
    # M_table_ = [0] * (slot_num + 1)
    # M_table = []
    # for U in range(9):
    #     M_table.append(M_table_[:])
    # print "Best Solution:  NC=", bestNC
    # M_table[0][0] = "ATM"
    # M_table[1][0] = "VDU"
    # M_table[2][0] = "FCCU"
    # M_table[3][0] = "ETH"
    # M_table[4][0] = "HDS"
    # M_table[5][0] = "HTU1"
    # M_table[6][0] = "HTU2"
    # M_table[7][0] = "RF"
    # M_table[8][0] = "MTBE"
    # for U in range(9):
    #     for T in slotlist:
    #         for Mode in modelist:
    #             if M[U * mode_num * slot_num + Mode * slot_num + T] >= 0.1:
    #                 M_table[U][T + 1] = Mode
    #                 break
    #             elif Mode == 3:
    #                 M_table[U][T + 1] = "N/A"
    # print tabulate(M_table, M_header, tablefmt="simple", numalign="center", floatfmt=".1f")
    return [ind_gb_objective, timeend, bestNC]

test_case_num = 24

def read_test_order():
    book = xlrd.open_workbook("test_18case_DPSO_2.xls")#Order_test_case
    sheet = book.sheet_by_name('test_case')
    all_numT, all_numL1, all_DV1, all_DS_num, all_OCtank_ini, all_Otank_ini, all_DS1, all_FOout = \
        [], [], [], [], [], [], [], []
    # numT
    n0 = 1
    all_numT = sheet.row_values(0, 0+1, test_case_num+1)
    # numL1
    n1 = 1
    all_numL1 = sheet.row_values(n0+1, 0+1, test_case_num+1)
    # all_numL1_1 = sheet.row_values(0, 0+1, 8+1)
    # numDV1
    n2 = np.sum(all_numL1)
    for L in range(test_case_num):
        all_DV1_ = []
        for l in range(int(all_numL1[L])):
            all_DV1_.append(sheet.row_values(int(n0+1 + n1+1 + np.sum(all_numL1[:L])+l), 1, numO+1))
        all_DV1.append(np.array(all_DV1_))
    # DS_num
    n3 = np.sum(all_numL1)
    for L in range(test_case_num):
        all_DS_num_ = []
        for l in range(int(all_numL1[L])):
            all_DS_num_.append(sheet.row_values(int(n0+1 + n1+1 + n2+1 + np.sum(all_numL1[:L])+l), 1, 2+1))
        all_DS_num.append(np.array(all_DS_num_))
    # OCtank_ini
    n4 = len(all_numL1)
    all_OCtank_ini = []
    for L in range(n4):
        all_OCtank_ini.append(np.array(sheet.row_values(int(n0+1 + n1+1 + n2+1 + n3+1 + L), 1, numO+1)))
    # Otank_ini
    n5 = len(all_numL1)
    all_Otank_ini = []
    for L in range(test_case_num):
        all_Otank_ini.append(np.array(sheet.row_values(int(n0+1 + n1+1 + n2+1 + n3+1 + n4+1 + L), 1, numO+1)))
    # all_DS1
    all_DS1 = []
    for L in range(test_case_num):
        DS1 = np.zeros((int(all_numL1[L]), int(all_numT[L])))
        for L1 in range(int(all_numL1[L])):
            DS1[L1, all_DS_num[L][L1, 0].astype(int):all_DS_num[L][L1, 1].astype(int) + 1] = 1
        all_DS1.append(DS1)
    # all_FOout
    all_FOout = []
    for L in range(test_case_num):
        all_FOout.append(np.zeros((int(all_numL1[L]), numO_g+numO_d)))
    print all_numL1#, all_DS_num , all_OCtank_ini, all_Otank_ini, all_DS1, all_FOout, all_DV1
    return np.array(all_numT,dtype="int"), np.array(all_numL1,dtype="int"), \
           all_DV1, all_DS_num, all_OCtank_ini, all_Otank_ini, all_DS1, all_FOout

def run(CASE):
    # printYield()
    book_result = xlwt.Workbook(encoding='utf-8', style_compression=0)
    run_time_num = 10
    NCmax = 9e10
    for i in range(len(CASE)):
        sheet = book_result.add_sheet(CASE[i], cell_overwrite_ok=True)
        sheet.write(0, 0, "Obj")
        sheet.write(0, 1, "Timecost")
        sheet.write(0, 2, "BestNC")
        # read cases with various numT
        AnumT, AnumL1, ADV1, ADS_num, AOCtank_ini, AOtank_ini, ADS1, _ = read_test_order()
        if CASE[i] == '100-0':
                name = "-read-100-0"
                ol = 0
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 1200
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '120-1':
                name = "-read-120-1"
                ol = 1
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 1400
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '140-2':
                name = "-read-140-2"
                ol = 2
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 1700
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '160-3':
                name = "-read-160-3"
                ol = 3
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 2000
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '180-4':
                name = "-read-180-4"
                ol = 4
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 2400
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '200-5':
                name = "-read-200-5"
                ol = 5
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 3000
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '100-6':
                name = "-read-100-6"
                ol = 6
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 1200
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '120-7':
                name = "-read-120-7"
                ol = 7
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 1400
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '140-8':
                name = "-read-140-8"
                ol = 8
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 1700
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '160-9':
                name = "-read-160-9"
                ol = 9
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 3600
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '180-10':
                name = "-read-180-10"
                ol = 10
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 2400
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '200-11':
                name = "-read-200-11"
                ol = 11
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 3600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 3000
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '100-12':
                name = "-read-100-12"
                ol = 12
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 1200
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '120-13':
                name = "-read-120-13"
                ol = 13
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 1400
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '140-14':
                name = "-read-140-14"
                ol = 2
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 1700
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '160-15':
                name = "-read-160-15"
                ol = 15
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 2000
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '180-16':
                name = "-read-180-16"
                ol = 16
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 2400
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '200-17':
                name = "-read-200-17"
                ol = 17
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 3000
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '100-18':
                name = "-read-100-18"
                ol = 18
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 1200
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '120-19':
                name = "-read-120-19"
                ol = 19
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 1400
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '140-20':
                name = "-read-140-20"
                ol = 20
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 1700
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '160-21':
                name = "-read-160-21"
                ol = 21
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 2000
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '180-22':
                name = "-read-180-22"
                ol = 22
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 2400
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])
        elif CASE[i] == '200-23':
                name = "-read-200-23"
                ol = 23
                VF = 1                                   # with or without Valid Functions
                numT = AnumT[ol]
                Tlist = range(numT)
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                case_times = 0
                obj = [0] * run_time_num
                timecost = [0] * run_time_num
                BNC = [0] * run_time_num
                runtime = 3000
                while case_times < run_time_num:
                    [obj[case_times], timecost[case_times], BNC[case_times]] = PSO(numT, Tlist, numL1, Llist1, DS1, DV1,
                                                                                   Pri, NCmax, case_times, DS_num,
                                                                                   OCtank_ini, Otank_ini, runtime,
                                                                                   case_times)
                    case_times += 1
                    for T in range(run_time_num):
                        sheet.write(T + 1, 0, round(obj[T], 3))
                        sheet.write(T + 1, 1, round(timecost[T], 3))
                        sheet.write(T + 1, 2, BNC[T])


        book_result.save('PRO_PSO_ZL_TL_RL1011-2.xls')
CASE = [
        # '100-0', #14162096.6519
        # '100-6', #14643888.7749
        '100-12', # 37279738.6646
        '100-18', #
        '120-1', #26976160.5763
        '120-7', #16513749.619
        # '120-13', #17880351.3534
        # '120-19', #
        # '140-2',
        # '140-8',
        # '140-14',
        # '140-20',
        # '160-3',
        # '160-9',
        # '160-15',
        # '160-21',
        # '180-4',
        # '180-10',
        # '180-16',
        # '180-22',
        # '200-5', # 37086017.2741
        # '200-11', # 28330718.5027
        # '200-17', # 24110178.8964
        # '200-23', # 24110178.8964
        ]

ind_num = 20
indlist = range(ind_num)
run(CASE)