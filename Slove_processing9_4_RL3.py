# from __future__ import print_function
import cplex
from tabulate import tabulate
import numpy as np
import paddle.fluid as fluid
# from PRO_noTrans_6_allslot_FS import PRO_opt as PRO2
from refinery_1MiniS_211_0FS3 import refinery as PRO2
# from refinery_1MiniS_211_0 import refinery as PRO1
# from PRO_ShiL_FS import PRO_opt as PRO2
from refinery_1MiniS_211_0 import refinery as PRO1
import xlwt
import xlrd
import time as TIME

numOC_g = 5
numOC_d = 3
numO_g = 5
numO_d = 3
OClist_g = range(numOC_g)
OClist_d = range(numOC_d)
Olist_g = range(numO_g)
Olist_d = range(numO_d)
MININPUT = [200.0, 0, 0, 5.0,   0, 5.0, 0, 0,   0]
MAXINPUT = [300.0]*9
FOCOmax = 100
PtVmax = 2000
C_order = 30000
numU = 9
numM = 4
numT = 50
# Pri = 1
# sample = 0
# Mode_Unit = 0
numS = 4
numO = 8
numO_g = 5
numO_d = 3
numOC = 8
numOC_g = 5
numOC_d = 3
numP = 4
hours = 1
numL = 3
# MAXINPUT = 300
Mlist = range(numM)
Ulist = range(numU)
Tlist = range(numT)
Slist = range(numS)
Plist = range(numP)
OClist = range(numOC)
OCglist = range(numOC_g)
OCdlist = range(numOC_d)
Olist = range(numO)
Oglist = range(numO_g)
Odlist = range(numO_d)
Llist = range(numL)
TLlist = range(2) # TL1 and TL2
OPC = 388.2   # crude oil cost per ton
apoc = 50.0    # inv cost
apo = 75.0    # inv cost
bp = 30000.  # penalty for stockout of order l per ton
PRO = [83.,100.,117.,93.,90.,0.,0.,0.,
       0.,0.,0.,0.,0.,47.,55.,48.,
       0.0001,0.0002,0.04,0.01,0.02,0.001,0.001,0.038,
       0.,0.,0.,0.,0.,1.68,1.1,1.6] #P /RON,S,CN,CPF/  # PRO(P,OC)

PROMAX = [0.]*numP*numO
PROMAX[16:24] = [0.0005,0.0006,0.015,0.015,0.015,0.035,0.035,0.01] # PROMAX(P,O) S content unit is %
PROMAX[24:32] = [0.,0.,0.,0.,0.,1.6184,1.1995,1.6184]  # CPF(P,O)
PROMIN = [93.,97.,90.,93.,97.,0.,0.,0.,
          0.,0.,0.,0.,0.,49.,49.,51.,
          0.,0.,0.,0.,0.,0.,0.,0.,
          0.,0.,0.,0.,0.,0.,0.,0.] # PROMIN(P,O)

rMIN = [0.]*numOC*numO  #  rMIN(OC,O)

rMAX = [1.]*numOC*numO
rMAX[16:21] = [0.1]*5  # rMAX(OC,O)
TTlist = [3,2,1]
QIinputL = [200.,300.,0.,300.,0.,300.,5.,300.,0.,300.,5.,300.,0.,300.,0.,300.,0.,300.]  # numU*2
OCtankLmin = [0]*numOC
OCtankLmax = [4000]*numOC
OtankLmin = [0]*numO
OtankLmax = [2000]*numO
H = 300
H_E = 4500
FOout_MAX = 100
Yield = [0]*numU*numM*numS
Yieldlist = [7.008,15.349,8.109,64.534,4.576,19.403,9.267,61.754,
             11.286,37.352, 12.580,35.652,
             22.216, 5.02, 45.664, 23.104, 5.01, 42.583, 23.418, 4.15, 42.261, 26.683, 4.13, 39.580,
             98.1, 94.1, 93.2, 90,
             97., 88., 86.2, 79.,
             99.4, 99.4,
             9., 89., 4., 93.,
             10., 90.,
             120]
for U in [Ulist[0]]: # ATM
    for M in Mlist[0:2]:
        for S in Slist[0:4]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)*0.01
for U in [Ulist[1]]: # VDU
    for M in Mlist[0:2]:
        for S in Slist[0:2]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)*0.01
for U in [Ulist[0+2]]: # FCCU
    for M in Mlist:
        for S in Slist[0:3]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)*0.01
for U in [Ulist[1+2]]: # ETH
    for M in Mlist:
        for S in [Slist[0]]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)*0.01
for U in [Ulist[2+2]]:  # HDS
    for M in Mlist:
        for S in [Slist[0]]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)*0.01
for U in [Ulist[3+2]]:  # HTU1
    for M in Mlist[0:2]:
        for S in [Slist[0]]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)*0.01
for U in [Ulist[4+2]]:  # HTU2
    for M in Mlist[0:2]:
        for S in Slist[0:2]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)*0.01
for U in [Ulist[5+2]]:  # RF
    for M in [Mlist[0]]:
        for S in Slist[0:2]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)*0.01
for U in [Ulist[6+2]]:  # MTBE
    for M in [Mlist[0]]:
        for S in [Slist[0]]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)*0.01

# For Parameter tYieldlist
tYield = [0]*numU*numM*numM*numS
for U in [Ulist[0],Ulist[1]]: # ATM,VDU
    for M in Mlist[0:2]:
        for M1 in Mlist[0:2]:
            if M1 != M:
                for S in Slist[0:4]:
                    tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S] = 0.5*(Yield[U*numM*numS+M*numS+S]+Yield[U*numM*numS+M1*numS+S])
for U in [Ulist[0+2]]: # FCCU
    for M in Mlist[0:4]:
        for M1 in Mlist[0:4]:
            if M1 != M:
                for S in Slist[0:3]:
                    tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S] = 0.5*(Yield[U*numM*numS+M*numS+S]+Yield[U*numM*numS+M1*numS+S])
for U in [Ulist[1+2]]: # ETH
    for M in Mlist[0:4]:
        for M1 in Mlist[0:4]:
            if M1 != M:
                for S in [Slist[0]]:
                    tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S] = 0.5*(Yield[U*numM*numS+M*numS+S]+Yield[U*numM*numS+M1*numS+S])
for U in [Ulist[2+2]]:  # HDS
    for M in Mlist[0:4]:
        for M1 in Mlist[0:4]:
            if M1 != M:
                for S in [Slist[0]]:
                    tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S] = 0.5*(Yield[U*numM*numS+M*numS+S]+Yield[U*numM*numS+M1*numS+S])
for U in [Ulist[3+2]]:  # HTU1
    for M in Mlist[0:2]:
        for M1 in Mlist[0:2]:
            if M1 != M:
                for S in [Slist[0]]:
                    tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S] = 0.5*(Yield[U*numM*numS+M*numS+S]+Yield[U*numM*numS+M1*numS+S])
for U in [Ulist[4+2]]:  # HTU2
    for M in Mlist[0:2]:
        for M1 in Mlist[0:2]:
            if M1 != M:
                for S in Slist[0:2]:
                    tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S] = 0.5*(Yield[U*numM*numS+M*numS+S]+Yield[U*numM*numS+M1*numS+S])
OpCost = [11.,11.5,0.,0.,
          11.,11.5,0.,0.,
          58.,57.,56.5,56.,
          49.56,47.11,46.7,44.66,
          28.98,27.18,26.73,24.48,
          9.,8., 0., 0.,
          11.,10., 0., 0.,
          83.,0.,0.,0.,
          13.84,0.,0.,0.] # numU*numM
tOpCost = [0]*numU*numM*numM
# For Parameter tOpCostlist
for U in Ulist[0:2]:
    for M in Mlist[0:4]:
        for M1 in Mlist[0:4]:
            tOpCost[U*numM*numM+M*numM+M1] = 0.5*(OpCost[U*numM+M]+OpCost[U*numM+M1])+0
for U in Ulist[0+2:3+2]:
    for M in Mlist[0:4]:
        for M1 in Mlist[0:4]:
            tOpCost[U*numM*numM+M*numM+M1] = 0.5*(OpCost[U*numM+M]+OpCost[U*numM+M1])+0
for U in Ulist[3+2:5+2]:
    for M in Mlist[0:2]:
        for M1 in Mlist[0:2]:
            tOpCost[U*numM*numM+M*numM+M1] = 0.5*(OpCost[U*numM+M]+OpCost[U*numM+M1])+0

def PRO_opt_TT(numT_total,now_T,numL1,Llist1,Pri,DV1_left,DS1,DS_num,OCtank_ini,Otank_ini,results,results_par,mode_T,T_state,T_Yield,T_OpCost):#
    prob = cplex.Cplex()
    out = prob.set_results_stream(None)  # don't display the solution process.
    out = prob.set_log_stream(None)  # don't display the solution process.
    prob.objective.set_sense(prob.objective.sense.minimize)
    prob.parameters.mip.tolerances.mipgap.set(0.0)
    # prob.parameters.timelimit.set(200)
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Production Scheduling
    # ====================================== Operation Variable FinM : input Flowrate of Units
    obj = [0] * numU * numM
    ct = ['C'] * numU * numM
    FinMcount = numU * numM
    FinM_c = 0
    namey = []
    charlist = [str(i) for i in range(0, FinMcount)]
    for i in charlist:
        namey.append('FinM' + i)
    prob.variables.add(obj=obj, types=ct, names=namey)
    # ====================================== Operation Variable FOCin : input Flowrate of OC Units
    obj = [0] * numOC
    ct = ['C'] * numOC
    FOCincount = numOC
    FOCin_c = FinM_c + FinMcount
    namey = []
    charlist = [str(i) for i in range(0, FOCincount)]
    for i in charlist:
        namey.append('FOCin' + i)
    prob.variables.add(obj=obj, types=ct, names=namey)
    # ====================================== Operation Variable M : Mode of unit
    obj = [0] * numU * numM
    ct = ['B'] * numU * numM
    Mcount = numU * numM
    M_c = FOCin_c + FOCincount
    namey = []
    charlist = [str(i) for i in range(0, Mcount)]
    for i in charlist:
        namey.append('M' + i)
    prob.variables.add(obj=obj, types=ct, names=namey)
    # ====================================== Operation Variable FOCO : blend Flowrate of component oil
    obj = [0] * numOC * numO
    ct = ['C'] * numOC * numO
    FOCOcount = numOC * numO
    FOCO_c = M_c + Mcount
    namey = []
    charlist = [str(i) for i in range(0, FOCOcount)]
    for i in charlist:
        namey.append('FOCO' + i)
    prob.variables.add(obj=obj, types=ct, names=namey)
    # ====================================== Operation Variable FOout : output Flowrate of oil
    obj = [0] * numO * numL1
    ct = ['C'] * numO * numL1
    FOoutcount = numO * numL1
    FOout_c = FOCO_c + FOCOcount
    namey = []
    charlist = [str(i) for i in range(0, FOoutcount)]
    for i in charlist:
        namey.append('FOout' + i)
    prob.variables.add(obj=obj, types=ct, names=namey)
    # ====================================== State Variable VOC : Volume of component oil
    obj = [0] * numOC
    ct = ['C'] * numOC
    VOCcount = numOC
    VOC_c = FOout_c + FOoutcount
    namey = []
    charlist = [str(i) for i in range(0, VOCcount)]
    for i in charlist:
        namey.append('VOC' + i)
    prob.variables.add(obj=obj, types=ct, names=namey)
    # ====================================== State Variable VO : Volume of production oil
    obj = [0] * numO
    ct = ['C'] * numO
    VOcount = numO
    VO_c = VOC_c + VOCcount
    namey = []
    charlist = [str(i) for i in range(0, VOcount)]
    for i in charlist:
        namey.append('VO' + i)
    prob.variables.add(obj=obj, types=ct, names=namey)
    # ====================================== Operation Variable Pout : the input of crude oil and the yield of product
    obj = [0] * (numOC)#numO+1+
    ct = ['C'] * (numOC)#numO+1+
    Poutcount = (numOC)#numO+1+
    Pout_c = VO_c + VOcount
    namey = []
    charlist = [str(i) for i in range(0, Poutcount)]
    for i in charlist:
        namey.append('Pout' + i)
    prob.variables.add(obj=obj, types=ct, names=namey)
    # ====================================== Operation Variable PoutA : assistant variables
    obj = [0] * (numOC) # numO+1+   # +1 for crude oil flowrate variable.
    ct = ['C'] * (numOC) # numO+1+
    PoutAcount = (numOC) # numO+1+
    PoutA_c = Pout_c + Poutcount
    namey = []
    charlist = [str(i) for i in range(0, PoutAcount)]
    for i in charlist:
        namey.append('PoutA' + i)
    prob.variables.add(obj=obj, types=ct, names=namey)
    # ====================================== Operation Variable Qout : output flow of component oil
    obj = [0] * numOC
    ct = ['C'] * numOC
    Qoutcount = numOC
    Qout_c = PoutA_c + PoutAcount
    namey = []
    charlist = [str(i) for i in range(0, Qoutcount)]
    for i in charlist:
        namey.append('Qout' + i)
    prob.variables.add(obj=obj, types=ct, names=namey)
    # ====================================== Operation Variable Opro : property of product oil
    obj = [0] * numO * numP
    ct = ['C'] * numO * numP
    lb = [0] * numO * numP
    ub = [50000] * numO * numP
    Oprocount = numO * numP
    Opro_c = Qout_c + Qoutcount
    namey = []
    charlist = [str(i) for i in range(0, Oprocount)]
    for i in charlist:
        namey.append('Opro' + i)
    prob.variables.add(obj=obj, types=ct, lb = lb, ub = ub, names=namey)

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Refinery SCHEDUAL @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # ================================= Mode Operation Function =====================================================
    # @@@@@@ For ATM and VDU @@@@@@@@@@@@@@@@@@@@
    #                                  just one running Mode for AV/HTU1/HTU2  ========================================
    i = 0
    for U in [Ulist[0],Ulist[1],Ulist[5],Ulist[6]]:#
            i += 1
            names = "Just_one_M_AVH1H2 " + str(i)
            ind = []
            val = []
            for M in Mlist[0:2]:
                ind.append(U * numM + M + M_c)
                val.append(1.0)
            prob.linear_constraints.add(lin_expr=[[ind,val]],senses="E", rhs=[1.0], names=[names])
    #                                  just one Mode for FCCU/ETH/HDS  ==========================================
    i = 0
    for U in [Ulist[2],Ulist[3],Ulist[4]]:
            i += 1
            names = "Just_one_M_F_E_H " + str(i)
            ind = []
            val = []
            for M in Mlist[0:4]:
                ind.append(U * numM + M + M_c)
                val.append(1.0)
            prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[1.0], names=[names])
    #                                  just one Mode for RF/MTBE  ===============================================
    i = 0
    for U in [Ulist[7],Ulist[8]]:
            i += 1
            names = "Just_one_M_R_MT " + str(i)
            prob.linear_constraints.add(
                lin_expr=[[[U * numM + M + M_c for M in [Mlist[0]]],
                     [1.0 for M in [Mlist[0]]]]],
                senses="E", rhs=[1.0], names=[names])
    #                                  M_FUCC = M_ETH =================================================================
    i = 0
    for M in Mlist:
            i += 1
            names = "M_FUCC_E_M_ETH " + str(i)
            prob.linear_constraints.add(
                            lin_expr=[[[Ulist[2] * numM + M + M_c,
                                        Ulist[3] * numM + M + M_c],
                                        [1.0,-1.0]]],
                            senses="E", rhs=[0], names=[names])
    #                                  M_HDS = M_ETH =================================================================
    i = 0
    for M in Mlist:
            i += 1
            names = "M_FUCC_E_M_ETH " + str(i)
            prob.linear_constraints.add(
                            lin_expr=[[[Ulist[3] * numM + M + M_c,
                                        Ulist[4] * numM + M + M_c],
                                        [1.0,-1.0]]],
                            senses="E", rhs=[0], names=[names])
    # ================================= output flowrate Operation Function ============================================
    #                                  input flowrate constrained by Two Mode ======================================
    # @@@@@@ For ATM and VDU @@@@@@@@@@@@@@@@@@@@
    i = 0
    ii = 0
    for U1 in [Ulist[0],Ulist[1],Ulist[5],Ulist[6]]:#
            for M in Mlist[0:2]:
                i += 1
                names1 = "upperlimit_FinM_AVH1H2 " + str(i)
                names2 = "lowerlimit_FinM_AVH1H2 " + str(i)
                ind = []
                val1 = []
                val2 = []
                ind.append(Ulist[U1] * numM + M + FinM_c)
                val1.append(1.0)
                val2.append(1.0)
                ind.append(Ulist[U1] * numM + M + M_c)
                val1.append(-1.0*MAXINPUT[U1])
                val2.append(-1.0*MININPUT[U1])
                prob.linear_constraints.add(lin_expr=[[ind,val1]], senses="L", rhs=[0.0], names=[names1])
                prob.linear_constraints.add(lin_expr=[[ind,val2]], senses="G", rhs=[0.0], names=[names2])
    i = 0
    ii = 0
    for U in [Ulist[2],Ulist[3],Ulist[4]]:
            for M in Mlist[0:4]:
                i += 1
                names1 = "upperlimit_FinM_FEH " + str(i)
                names2 = "lowerlimit_FinM_FEH " + str(i)
                ind = []
                val1 = []
                val2 = []
                ind.append(Ulist[U] * numM + M + FinM_c)
                val1.append(1.0)
                val2.append(1.0)
                ind.append(Ulist[U] * numM + M + M_c)
                val1.append(-1.0*MAXINPUT[U])
                val2.append(-1.0*MININPUT[U])
                prob.linear_constraints.add(lin_expr=[[ind,val1]], senses="L", rhs=[0.0], names=[names1])
                prob.linear_constraints.add(lin_expr=[[ind,val2]], senses="G", rhs=[0.0], names=[names2])
    # ================================= intermediary oil balance ====================================================
    #                                  ATM input oil balance ==================================================
    #                                  VDU1 input oil balance ==================================================
    i = 0
    i += 1
    names = "VDU_input_balance " + str(i)
    ind = []
    val = []
    for M in Mlist[0:2]:
        ind.append(Ulist[1]* numM + M + FinM_c)
        val.append(1.0)
    for M in Mlist[0:2]:
        ind.append(Ulist[0]* numM + M + FinM_c)  # From ATM S4
        val.append(-1.0 * ((1-T_state[Ulist[0]])*Yield[Ulist[0] * numM * numS + M * numS + 3]+
                           (T_state[Ulist[0]])*T_Yield[Ulist[0]*numS+3]))
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    #                                  FCCU input oil balance ==================================================
    i = 0
    i += 1
    names = "FCCU_input_balance " + str(i)
    ind = []
    val = []
    for M in Mlist[0:4]:
        ind.append(Ulist[2]* numM + M + FinM_c)
        val.append(1.0)
    for M in Mlist[0:2]:
        ind.append(Ulist[1] * numM + M + FinM_c)  # From VDU1(1) S2
        val.append(-1.0 * ((1-T_state[Ulist[1]])*Yield[Ulist[1] * numM * numS + M * numS + 1]+
                           (T_state[Ulist[1]])*T_Yield[Ulist[1]*numS+1]))
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    #                                  ETH input oil balance ==================================================
    i = 0
    i += 1
    names = "ETH_input_balance " + str(i)
    ind = []
    val = []
    for M in Mlist[0:4]:
        ind.append(Ulist[3]* numM + M + FinM_c)
        val.append(1.0)
    ind.append(OClist[3] + FOCin_c)  # Fenliu To HDS gasoline
    val.append(1.0)
    for M in Mlist[0:4]:
        ind.append(Ulist[4]* numM + M + FinM_c)# From HDS(4) S1
        val.append(-1.0 * ((1-T_state[Ulist[4]])*Yield[Ulist[4] * numM * numS + M * numS + 0]+  # From HDS(4) S1
                           (T_state[Ulist[4]])*T_Yield[Ulist[4]*numS+0]))
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    #                                  HDS input oil balance ==================================================
    i = 0
    i += 1
    names = "HDS_input_balance " + str(i)
    ind = []
    val = []
    for M in Mlist[0:4]:
        ind.append(Ulist[4]* numM + M + FinM_c)
        val.append(1.0)
    for M in Mlist[0:4]:
        ind.append(Ulist[2]* numM + M + FinM_c)  # From FCCU(2) S3
        val.append(-1.0 * ((1-T_state[Ulist[2]])*Yield[Ulist[2] * numM * numS + M * numS + 2]+
                           (T_state[Ulist[2]])*T_Yield[Ulist[2]*numS+2]))
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    #                                  HTU1 input oil balance ==================================================
    i = 0
    i += 1
    names = "HTU1_input_balance " + str(i)
    ind = []
    val = []
    for M in Mlist[0:2]:
        ind.append(Ulist[5]* numM + M + FinM_c)
        val.append(1.0)
    ind.append(OClist[7] + FOCin_c)   # Fenliu To Light straightrun diesel
    val.append(1.0)
    for M in Mlist[0:2]:
        ind.append(Ulist[0] * numM + M + FinM_c)  # From ATM1(0) S2
        val.append(-1.0 * ((1-T_state[Ulist[0]])*Yield[Ulist[0] * numM * numS + M * numS + 1]+
                           (T_state[Ulist[0]])*T_Yield[Ulist[0]*numS+1]))
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    #                                  HTU2 input oil balance ==================================================
    i = 0
    i += 1
    names = "HTU2_input_balance " + str(i)
    ind = []
    val = []
    for M in Mlist[0:2]:
        ind.append(Ulist[6]* numM + M + FinM_c)
        val.append(1.0)
    for M in Mlist[0:2]:
        ind.append(Ulist[0] * numM + M + FinM_c)  # From ATM1(0) S3
        val.append(-1.0 * ((1-T_state[Ulist[0]])*Yield[Ulist[0] * numM * numS + M * numS + 2]+
                           (T_state[Ulist[0]])*T_Yield[Ulist[0]*numS+2]))
        ind.append(Ulist[1] * numM + M + FinM_c)  # From VDU1(2) S1
        val.append(-1.0 * ((1-T_state[Ulist[1]])*Yield[Ulist[1] * numM * numS + M * numS + 0]+
                           (T_state[Ulist[1]])*T_Yield[Ulist[1]*numS+0]))
    for M in Mlist[0:4]:
        ind.append(Ulist[2]* numM + M + FinM_c)# From FCCU(2) S1
        val.append(-1.0 * ((1-T_state[Ulist[2]])*Yield[Ulist[2] * numM * numS + M * numS + 0] +   # From FCCU(2) S1
                           (T_state[Ulist[2]])*T_Yield[Ulist[2]*numS+0]))
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    #                                  RF input oil balance ==================================================
    i = 0
    i += 1
    names = "RF_input_balance " + str(i)
    ind = []
    val = []
    ind.append(Ulist[7]* numM + FinM_c)
    val.append(1.0)
    for M in Mlist[0:2]:
        ind.append(Ulist[0] * numM + M + FinM_c)  # From ATM1(0) S1
        val.append(-1.0 * ((1-T_state[Ulist[0]])*Yield[Ulist[0] * numM * numS + M * numS + 0]+
                           (T_state[Ulist[0]])*T_Yield[Ulist[0]*numS+0]))
    for M in Mlist[0:2]:
        ind.append(Ulist[6]* numM + M + FinM_c)  # From HTU2(6) S1
        val.append(-1.0 * ((1-T_state[Ulist[6]])*Yield[Ulist[6] * numM * numS + M * numS + 0]+
                           (T_state[Ulist[6]])*T_Yield[Ulist[6]*numS+0]))
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    #                                  MTBE input oil balance ==================================================
    i = 0
    i += 1
    names = "MTBE_input_balance " + str(i)
    ind = []
    val = []
    ind.append(Ulist[8]* numM + FinM_c)
    val.append(1.0)
    for M in Mlist[0:4]:
        ind.append(Ulist[2]* numM + M + FinM_c)  # From FCCU(2) S2
        val.append(-1.0 * ((1-T_state[Ulist[2]])*Yield[Ulist[2] * numM * numS + M * numS + 1]+
                           (T_state[Ulist[2]])*T_Yield[Ulist[2]*numS+1]))
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    # ================================= Volume State Function of component oil tank =================================
    #                                  State Function of Volume C5  ==================================================
    i = 0
    i += 1
    names = "Volume_C5 " + str(i)
    ind = []
    val = []
    ind.append(0 + VOC_c)  # OUT: inventory of T
    val.append(1.0)
    ind.append(Ulist[7]* numM + FinM_c)  # IN: from RF(7) M0T0 output
    val.append(-1.0 * hours * Yield[Ulist[7] * numM * numS + 0 * numS + 0])   # IN: from RF(7) M0S1 output
    for O in Olist[0:5]:
        ind.append(0 * numO + O + FOCO_c)  # OUT: to blend
        val.append(hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[0]], names=[names])
    #                                  State Function of Volume Ref  ==================================================
    i = 0
    i += 1
    names = "Volume_Ref " + str(i)
    ind = []
    val = []
    ind.append(1 + VOC_c)  # OUT: inventory of T
    val.append(1.0)
    ind.append(Ulist[7]* numM + FinM_c)  # IN: from RF(7) M0T0 output
    val.append(-1.0 * hours * Yield[Ulist[7] * numM * numS + 0 * numS + 1]) # IN: from RF(7) M0S2 output
    for O in Olist[0:5]:
        ind.append(1 * numO + O + FOCO_c)  # OUT: to blend
        val.append(hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[1]], names=[names])
    #                                  State Function of Volume MTBE  ==================================================
    i = 0
    i += 1
    names = "Volume_MTBE " + str(i)
    ind = []
    val = []
    ind.append(2 + VOC_c)  # OUT: inventory of T
    val.append(1.0)
    ind.append(Ulist[8]* numM + FinM_c)  # IN: from MTBE(8) M0T0 output
    val.append(-1.0 * hours * Yield[Ulist[8] * numM * numS + 0 * numS + 0])  # IN: from MTBE(8) M0S1 output
    for O in Olist[0:5]:
        ind.append(2 * numO + O + FOCO_c)  # OUT: to blend
        val.append(hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[2]], names=[names])
    #                                  State Function of Volume HDS_g  ================================================
    i = 0
    i += 1
    names = "Volume_HDS " + str(i)
    ind = []
    val = []
    ind.append(3 + VOC_c)  # OUT: inventory of T
    val.append(1.0)
    ind.append(OClist[3] + FOCin_c)  # IN: from OClist[3] T0 output
    val.append(-1.0)
    for O in Olist[0:5]:
        ind.append(3 * numO + O + FOCO_c)  # OUT: to blend
        val.append(hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[3]], names=[names])
    #                                  State Function of Volume Eth_g  ================================================
    i = 0
    i += 1
    names = "Volume_Eth_g " + str(i)
    ind = []
    val = []
    ind.append(4 + VOC_c)  # OUT: inventory of T
    val.append(1.0)
    for M in Mlist[0:4]:
        ind.append(Ulist[3]* numM + M + FinM_c)  # IN: from ETH(3)  T0 output   # IN: from ETH(3) S1 output
        val.append(-1.0 * hours * ((1-T_state[Ulist[3]])*Yield[Ulist[3] * numM * numS + M * numS + 0] +   # IN: from ETH(3) S1 output
                                   (T_state[Ulist[3]])*T_Yield[Ulist[3]*numS+0]))
    for O in Olist[0:5]:
        ind.append(4 * numO + O + FOCO_c)  # OUT: to blend
        val.append(hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[4]], names=[names])
    #                                  State Function of Volume Rd2  ================================================
    i = 0
    i += 1
    names = "Volume_Rd2 " + str(i)
    ind = []
    val = []
    ind.append(5 + VOC_c)  # OUT: inventory of T
    val.append(1.0)
    for M in Mlist[0:2]:
        ind.append(Ulist[6]* numM + M + FinM_c) # IN: from HTU2(6)   T0 output# IN: from HTU2(6) S2 output
        val.append(-1.0 * hours * ((1-T_state[Ulist[6]])*Yield[Ulist[6] * numM * numS + M * numS + 1]+  # IN: from HTU2(6) S2 output
                                   (T_state[Ulist[6]])*T_Yield[Ulist[6]*numS+1]))
    for O in Olist[5:8]:
        ind.append(5 * numO + O + FOCO_c)  # OUT: to blend
        val.append(hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[5]], names=[names])
    #                                  State Function of Volume Rd1  ================================================
    i = 0
    i += 1
    names = "Volume_Rd1 " + str(i)
    ind = []
    val = []
    ind.append(6 + VOC_c)  # OUT: inventory of T
    val.append(1.0)
    for M in Mlist[0:2]:
        ind.append(Ulist[5]* numM + M + FinM_c) # IN: from HTU1(5)   T0 output# IN: from HTU1(5) S1 output
        val.append(-1.0 * hours * ((1-T_state[Ulist[5]])*Yield[Ulist[5] * numM * numS + M * numS + 0]+  # IN: from HTU1(5) S1 output
                                   (T_state[Ulist[5]])*T_Yield[Ulist[5]*numS+0]))

    for O in Olist[5:8]:
        ind.append(6 * numO + O + FOCO_c)  # OUT: to blend
        val.append(hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[6]], names=[names])
    #                                  State Function of Volume Lsd  ================================================
    i = 0
    i += 1
    names = "Volume_Lsd " + str(i)
    ind = []
    val = []
    ind.append(7 + VOC_c)  # OUT: inventory of T
    val.append(1.0)
    ind.append(OClist[7] + FOCin_c)  # IN: from Fen1(9) S1 output
    val.append(-1.0*hours)
    for O in Olist[5:8]:
        ind.append(7 * numO + O + FOCO_c)  # OUT: to blend
        val.append(hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[7]], names=[names])
    # ================================= online control ================================================================
    # #                                  Volume HDS=0 Eth=0 RD1=0 Lsd=0   =====================================
    # i = 0
    # for OC in OClist[3:5]+OClist[6:8]:
    #         i += 1
    #         names = "Volume_online " + str(i)
    #         ind = []
    #         val = []
    #         ind.append(OC + VOC_c)  # OUT: inventory of T
    #         val.append(1.0)
    #         prob.linear_constraints.add(lin_expr=[[ind, val]],senses="E", rhs=[0.0], names=[names])
    # ================================= component oil output flow: Qout =============================================
    #                                  output flow of  C5  ==================================================
    i = 0
    i += 1
    names = "Output_Flow_C5 " + str(i)
    ind = []
    val = []
    ind.append(OClist[0] + Qout_c)  # OUT: inventory of T
    val.append(1.0)
    ind.append(Ulist[7] * numM + 0 + FinM_c)  # IN: from RF(7) M0T output
    val.append(-1.0 * Yield[Ulist[7] * numM * numS + 0 * numS + 0])  # IN: from RF(7) M0S1 output
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    #                                  output flow of Ref  ==================================================
    i = 0
    i += 1
    names = "Output_Flow_Ref " + str(i)
    ind = []
    val = []
    ind.append(OClist[1] + Qout_c)  # OUT: inventory of T
    val.append(1.0)
    ind.append(Ulist[7] * numM + 0 + FinM_c)  # IN: from RF(7) M0T output
    val.append(-1.0 * Yield[Ulist[7] * numM * numS + 0 * numS + 1])  # IN: from RF(7) M0S2 output
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    #                                  output flow of MTBE  ==================================================
    i = 0
    i += 1
    names = "Output_Flow_MTBE " + str(i)
    ind = []
    val = []
    ind.append(OClist[2] + Qout_c)  # OUT: inventory of T
    val.append(1.0)
    ind.append(Ulist[8] * numM + 0 + FinM_c)  # IN: from MTBE(8) M0T output
    val.append(-1.0 * Yield[Ulist[8] * numM * numS + 0 * numS + 0])  # IN: from MTBE(8) M0S1 output
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    #                                  output flow of HDS  ==================================================
    i = 0
    i += 1
    names = "Output_Flow_HDS_g " + str(i)
    ind = []
    val = []
    ind.append(OClist[3] + FOCin_c)  # Fenliu To HDS gasoline
    val.append(1.0)
    ind.append(OClist[3] + Qout_c)  # OUT: inventory of T
    val.append(-1.0)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    #                                  output flow of Eth_g  ==================================================
    i = 0
    i += 1
    names = "Output_Flow_Eth_g " + str(i)
    ind = []
    val = []
    ind.append(OClist[4]+ Qout_c)  # OUT: inventory of T
    val.append(1.0)
    for M in Mlist[0:4]:
        ind.append(Ulist[3] * numM + M + FinM_c)  # IN: from ETH(3)  T output
        val.append(-1.0 * ((1-T_state[Ulist[3]])*Yield[Ulist[3] * numM * numS + M * numS + 0] +   # IN: from ETH(3) S1 output
                                   (T_state[Ulist[3]])*T_Yield[Ulist[3]*numS+0]))
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    #                                  output flow of Rd2  ==================================================
    i = 0
    i += 1
    names = "Output_Flow_Rd2 " + str(i)
    ind = []
    val = []
    ind.append(OClist[5] + Qout_c)  # OUT: inventory of T
    val.append(1.0)
    for M in Mlist[0:2]:
        ind.append(Ulist[6] * numM + M + FinM_c)  # IN: from HTU2(6)  T output
        val.append(-1.0 * ((1-T_state[Ulist[6]])*Yield[Ulist[6] * numM * numS + M * numS + 1]+  # IN: from HTU2(6) S2 output
                                   (T_state[Ulist[6]])*T_Yield[Ulist[6]*numS+1]))
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    #                                  output flow of Rd1  ==================================================
    i = 0
    i += 1
    names = "Output_Flow_Rd1 " + str(i)
    ind = []
    val = []
    ind.append(OClist[6] + Qout_c)  # OUT: inventory of T
    val.append(1.0)
    for M in Mlist[0:2]:
        ind.append(Ulist[5] * numM + M + FinM_c)  # From HTU1(5) S1
        val.append(-1.0 * ((1-T_state[Ulist[5]])*Yield[Ulist[5] * numM * numS + M * numS + 0]+  # IN: from HTU1(5) S1 output
                                   (T_state[Ulist[5]])*T_Yield[Ulist[5]*numS+0]))
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    #                                  output flow of Lsd  ==================================================
    i = 0
    i += 1
    names = "Output_Flow_Lsd_g " + str(i)
    ind = []
    val = []
    ind.append(OClist[7] + FOCin_c)  # Fenliu To Lsd gasoline
    val.append(1.0)
    ind.append(OClist[7] + Qout_c)  # OUT: inventory of T
    val.append(-1.0)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    # ================================= FOCO Operation Function ==================================================
    #                                  Property Limitation - RON  ================================================
    i = 0
    for O in Olist[0:5]:
        i += 1
        names = "RON_Limit " + str(i)
        ind = []
        val = []
        for OC in OClist[0:5]:
            ind.append(OC * numO + O + FOCO_c)
            val.append(PRO[0 * numOC + OC] - PROMIN[0 * numO + O])  # RON of 0
        prob.linear_constraints.add(lin_expr=[[ind, val]],senses="G", rhs=[0.0], names=[names])
    i = 0
    for O in Olist[0:5]:
        i += 1
        names = "RON_Limit_Cpro " + str(i)
        ind = []
        val = []
        for OC in OClist[0:5]:
            ind.append(OC * numO + O + FOCO_c)
            val.append(PRO[0 * numOC + OC] - PROMIN[0 * numO + O])  # RON of 0
        ind.append(O * numP + 0 + Opro_c)
        val.append(-1.0)
        prob.linear_constraints.add(lin_expr=[[ind, val]],senses="L", rhs=[0.0], names=[names])
    #                                  Property Limitation - S  ==================================================
    i = 0
    for O in Olist[0:5]:
        i += 1
        names = "S_Limit " + str(i)
        ind = []
        val = []
        for OC in OClist[0:5]:
            ind.append(OC * numO + O + FOCO_c)
            val.append(PRO[2 * numOC + OC] - PROMAX[2 * numO + O])  # S of 0
        prob.linear_constraints.add(lin_expr=[[ind, val]],senses="L", rhs=[0.0], names=[names])
    i = 0
    for O in Olist[0:5]:
        i += 1
        names = "S_Limit_Cpro " + str(i)
        ind = []
        val = []
        for OC in OClist[0:5]:
            ind.append(OC * numO + O + FOCO_c)
            val.append(PRO[2 * numOC + OC] - PROMAX[2 * numO + O])  # S of 0
        ind.append(O * numP + 2 + Opro_c)
        val.append(1.0)
        prob.linear_constraints.add(lin_expr=[[ind, val]],senses="G", rhs=[0.0], names=[names])
    #                                  Property Limitation - CN  =================================================
    i = 0
    for O in Olist[5:8]:
        i += 1
        names = "CN_Limit " + str(i)
        ind = []
        val = []
        for OC in OClist[5:8]:
            ind.append(OC * numO + O + FOCO_c)
            val.append(PRO[1 * numOC + OC] - PROMIN[1 * numO + O])  # CN of 0
        prob.linear_constraints.add(lin_expr=[[ind, val]],senses="G", rhs=[0.0], names=[names])
    i = 0
    for O in Olist[5:8]:
        i += 1
        names = "CN_Limit_Cpro " + str(i)
        ind = []
        val = []
        for OC in OClist[5:8]:
            ind.append(OC * numO + O + FOCO_c)
            val.append(PRO[1 * numOC + OC] - PROMIN[1 * numO + O])  # CN of 0
        ind.append(O * numP + 1 + Opro_c)
        val.append(-1.0)
        prob.linear_constraints.add(lin_expr=[[ind, val]],senses="L", rhs=[0.0], names=[names])
    #                                  Property Limitation - S  =================================================
    i = 0
    for O in Olist[5:8]:
        i += 1
        names = "S_Limit " + str(i)
        ind = []
        val = []
        for OC in OClist[5:8]:
            ind.append(OC * numO + O + FOCO_c)
            val.append(PRO[2 * numOC + OC] - PROMAX[2 * numO + O])  # S of 0
        prob.linear_constraints.add(lin_expr=[[ind, val]],senses="L", rhs=[0.0], names=[names])
    i = 0
    for O in Olist[5:8]:
        i += 1
        names = "S_Limit_Cpro " + str(i)
        ind = []
        val = []
        for OC in OClist[5:8]:
            ind.append(OC * numO + O + FOCO_c)
            val.append(PRO[2 * numOC + OC] - PROMAX[2 * numO + O])  # S of 0
        ind.append(O * numP + 2 + Opro_c)
        val.append(1.0)
        prob.linear_constraints.add(lin_expr=[[ind, val]],senses="G", rhs=[0.0], names=[names])
    #                                  Property Limitation - CPF  ===============================================
    i = 0
    for O in Olist[5:8]:
        i += 1
        names = "CPF_Limit " + str(i)
        ind = []
        val = []
        for OC in OClist[5:8]:
            ind.append(OC * numO + O + FOCO_c)
            val.append(PRO[3 * numOC + OC] - PROMAX[3 * numO + O])  # CPF of 0
        prob.linear_constraints.add(lin_expr=[[ind, val]],senses="L", rhs=[0.0], names=[names])
    i = 0
    for O in Olist[5:8]:
        i += 1
        names = "CPF_Limit_Cpro " + str(i)
        ind = []
        val = []
        for OC in OClist[5:8]:
            ind.append(OC * numO + O + FOCO_c)
            val.append(PRO[3 * numOC + OC] - PROMAX[3 * numO + O])  # CPF of 0
        ind.append(O * numP + 3 + Opro_c)
        val.append(1.0)
        prob.linear_constraints.add(lin_expr=[[ind, val]],senses="G", rhs=[0.0], names=[names])
    #                                  MTBE NOT exceed 10%  ================================================
    i = 0
    for O in Olist[0:5]:
        i += 1
        names = "MTBE_NOT_Exc_0.1 " + str(i)
        prob.linear_constraints.add(
            lin_expr=[[[OClist[0] * numO + O + FOCO_c,
                        OClist[1] * numO + O + FOCO_c,
                        OClist[2] * numO + O + FOCO_c,
                        OClist[3] * numO + O + FOCO_c,
                        OClist[4] * numO + O + FOCO_c],
                        [-0.1, -0.1, 0.9, -0.1, -0.1]]],
            senses="L", rhs=[0.0], names=[names])
    # ================================= Volume State Function of production oil tank =============================
    #                                  Volume State Function of gasoline oil tank  ===============================
    for O in Olist[0:5]:
        i = 0
        i += 1
        names = "Volume_Otank" + str(O) + " " + str(i)
        ind = []
        val = []
        ind.append(O + VO_c)
        val.append(1.0)
        for OC in OClist[0:5]:
            ind.append(OC * numO + O + FOCO_c)
            val.append(-1.0 * hours)
        for L in Llist1:
            ind.append(O * numL1 + L + FOout_c)
            val.append(hours)
        prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[Otank_ini[O]], names=[names])
    #                                  Volume State Function of diesel oil tank  ===============================
    for O in Olist[5:8]:
        i = 0
        i += 1
        names = "Volume_Otank" + str(O) + " " + str(i)
        ind = []
        val = []
        ind.append(O + VO_c)
        val.append(1.0)
        for OC in OClist[5:8]:
            ind.append(OC * numO + O + FOCO_c)
            val.append(-1.0 * hours)
        for L in Llist1:
            ind.append(O * numL1 + L + FOout_c)
            val.append(hours)
        prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[Otank_ini[O]], names=[names])
    #                                  Order amount limit  ==========================================
    i = 0
    for O in Olist:
        for L in Llist1:
            i += 1
            names1 = "Order_amount " + str(i)
            ind = []
            val = []
            ind.append(O * numL1 + L + FOout_c)
            val.append(1.0)
            prob.linear_constraints.add(lin_expr=[[ind, val]],senses="L", rhs=[DV1_left[L][O]], names=[names1])
    i = 0
    for O in Olist:
        for L in Llist1:
            i += 1
            names1 = "Order_amount " + str(i)
            ind = []
            val = []
            ind.append(O * numL1 + L + FOout_c)
            val.append(1.0)
            prob.linear_constraints.add(lin_expr=[[ind, val]],senses="L", rhs=[DS1[L][now_T]*FOout_MAX], names=[names1])
    # #                                        Mode of transition limitation  ==========================================
    # i = 0
    # for U in [Ulist[0],Ulist[1],Ulist[5],Ulist[6]]:
    #     for M in Mlist[:2]:
    #         i += 1
    #         names1 = "ModeT_limit_AVHH " + str(i)
    #         ind = []
    #         val = []
    #         ind.append(U * numM + M + M_c)
    #         val.append(1.0)
    #         prob.linear_constraints.add(lin_expr=[[ind, val]],senses="G", rhs=[mode_T[U * numM + M]], names=[names1])
    # i = 0
    # for U in [Ulist[2],Ulist[3],Ulist[4]]:
    #     for M in Mlist:
    #         i += 1
    #         names1 = "ModeT_limit_FEH " + str(i)
    #         ind = []
    #         val = []
    #         ind.append(U * numM + M + M_c)
    #         val.append(1.0)
    #         prob.linear_constraints.add(lin_expr=[[ind, val]],senses="G", rhs=[mode_T[U * numM + M]], names=[names1])
    # #                                  Production amount limit  ==========================================
    # i = 0
    # i += 1
    # names1 = "Crudeoil_amount " + str(i)
    # ind = []
    # val = []
    # for M in Mlist[:2]:
    #     ind.append(0 * numM + M + FinM_c)
    #     val.append(1.0)
    # prob.linear_constraints.add(lin_expr=[[ind, val]],senses="E", rhs=[results], names=[names1])
    # i = 0
    # for O in Olist_g:
    #     i += 1
    #     names1 = "gas_Product_amount " + str(i)
    #     ind = []
    #     val = []
    #     for OC in OClist_g:
    #             ind.append(OC * numO + O + FOCO_c)
    #             val.append(1.0)
    #     ind.append((O+1) + Pout_c)
    #     val.append(-1.0)
    #     prob.linear_constraints.add(lin_expr=[[ind, val]],senses="E", rhs=[0], names=[names1])
    # i = 0
    # for O in Olist_d:
    #     i += 1
    #     names1 = "die_Product_amount " + str(i)
    #     ind = []
    #     val = []
    #     for OC in OClist_d:
    #         ind.append((OC+numOC_g) * numO + (O+numO_g) + FOCO_c)
    #         val.append(1.0)
    #     ind.append((O+numO_g+1) + Pout_c)
    #     val.append(-1.0)
    #     prob.linear_constraints.add(lin_expr=[[ind, val]],senses="E", rhs=[0], names=[names1])
    i = 0
    for OC in OClist:
        i += 1
        names = "Qout_abs_L " + str(i)
        prob.linear_constraints.add(lin_expr=[[[OC + Qout_c,OC + Pout_c],
                                               [1.0,-1.0]]], senses="L", rhs=[results[OC]], names=[names])
        names = "Qout_abs_G " + str(i)
        prob.linear_constraints.add(lin_expr=[[[OC + Qout_c,OC + Pout_c],
                                               [1.0,1.0]]], senses="G", rhs=[results[OC]], names=[names])
    # #                                  Absolute  value limitation  ==========================================
    # i = 0
    # for O in range(numOC):#numO+1+
    #     i += 1
    #     names1 = "Order_amount " + str(i)
    #     prob.linear_constraints.add(lin_expr=[[[O + Pout_c, O + PoutA_c],
    #                                            [1.0 ,1.0]]],senses="G", rhs=[results[O]], names=[names1])
    # ============================================ inputting variables setting ================================
    # prob.variables.set_lower_bounds(zip(range(M_c, Mcount+M_c),Mode))
    # prob.variables.set_upper_bounds(zip(range(M_c, Mcount+M_c),Mode))
    # ============================================ SET Variable BOUND ================================

    # prob.variables.set_lower_bounds(zip(range(OL_c, OLcount + OL_c), [0] * OLcount))
    # prob.variables.set_upper_bounds(zip(range(OL_c, OLcount + OL_c), [2000] * OLcount))

    prob.variables.set_lower_bounds(zip(range(Pout_c, Poutcount + Pout_c), [0] * Poutcount))
    # prob.variables.set_lower_bounds(zip(range(PoutA_c+1, 8 + PoutA_c+1), [0] * PoutAcount))
    # prob.variables.set_upper_bounds(zip(range(PoutA_c+1, 8 + PoutA_c+1), [FOCOmax*numOC_g] * PoutAcount))
    prob.variables.set_lower_bounds(zip(range(PoutA_c+1, 8 + PoutA_c+1), [0] * PoutAcount))
    prob.variables.set_upper_bounds(zip(range(PoutA_c+1, 8 + PoutA_c+1), [OCtankLmax[0]] * PoutAcount))

    prob.variables.set_lower_bounds(zip(range(FOCO_c, FOCOcount + FOCO_c), [0] * FOCOcount))
    prob.variables.set_upper_bounds(zip(range(FOCO_c, FOCOcount + FOCO_c), [FOCOmax] * FOCOcount))
    prob.variables.set_lower_bounds(zip(range(VO_c, VOcount + VO_c), [0] * VOcount))
    prob.variables.set_upper_bounds(zip(range(VO_c, VOcount + VO_c), [PtVmax] * VOcount))
    prob.variables.set_lower_bounds(zip(range(VOC_c, VOCcount + VOC_c), [0] * VOCcount))
    prob.variables.set_upper_bounds(zip(range(VOC_c, VOCcount + VOC_c), [OCtankLmax[0]] * VOCcount))

    prob.variables.set_lower_bounds(zip(range(FOout_c, FOoutcount + FOout_c), [0] * FOoutcount))
    # prob.variables.set_upper_bounds(zip(range(FOout_c, FOoutcount + FOout_c), [80] * FOoutcount))

    # ================================= SET QI/OC/xQI/xQItri/xQI1/xQItri1 BOUND ===========================
    # ========================================= objection coefficients ===========================
    for U in [Ulist[0],Ulist[1],Ulist[5],Ulist[6]]:
        for M in Mlist[0:2]:
            prob.objective.set_linear(Ulist[U] * numM + M + FinM_c, hours * ((1-T_state[U]) * OpCost[Ulist[U] * numM + M] +
                                                                             T_state[U] * T_OpCost[U]))
    for U in [Ulist[2]]:
        for M in Mlist[0:4]:
            prob.objective.set_linear(Ulist[U] * numM + M + FinM_c, hours * ((1-T_state[U]) * OpCost[Ulist[U] * numM + M] +
                                                                             T_state[U] * T_OpCost[U]))
    for U in [Ulist[3],Ulist[4]]:#
        for M in Mlist[0:4]:
            prob.objective.set_linear(Ulist[U] * numM + M + FinM_c, hours * ((1-T_state[U]) * OpCost[Ulist[U] * numM + M] +
                                                                             T_state[U] * T_OpCost[U]))
    for U in [Ulist[7],Ulist[8]]:
        for M in Mlist[0:1]:
            prob.objective.set_linear(Ulist[U] * numM + M + FinM_c, hours * ((1-T_state[U]) * OpCost[Ulist[U] * numM + M] +
                                                                             T_state[U] * T_OpCost[U]))
    # for O in Olist:
    #     prob.objective.set_linear(O + VO_c, -apoc)
    C_OC = [1, 1.6, 1.5, 1, 1, 1, 1.5, 1]
    for OC in OClist:
        prob.objective.set_linear(OC + VOC_c, -apo* C_OC[OC])#
    for L in Llist1:
        for O in Olist:
            prob.objective.set_linear(O * numL1 + L + FOout_c, -20 * (numT_total - DS_num[L][1]) - apo * 1.8)
    for OC in range(numOC):
        prob.objective.set_linear(OC + Pout_c, C_order*results_par[OC]*1.1)
    for O in Olist:
        for P in Plist:
            prob.objective.set_linear(O * numP + P + Opro_c, 1)
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Solving @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # prob.write('PRO_NN_sort.lp')
    prob.solve()
    sol = prob.solution
    # print
    # solution.get_status() returns an integer code
    # print "Solution status = ", sol.get_status(), ":",sol.status[sol.get_status()]
    # the following line prints the corresponding string
    # print "Solution value  = ", sol.get_objective_value(), "\n"
    FOout = sol.get_values(FOout_c, FOout_c + FOoutcount - 1)
    OC_inventory = sol.get_values(VOC_c, VOC_c + VOCcount - 1)
    O_inventory = sol.get_values(VO_c, VO_c + VOcount - 1)
    Mode_act = np.rint(np.array(sol.get_values(M_c, M_c + Mcount - 1))).tolist()
    if Pri == 1:
        numT = 1
        Tlist = range(numT)
        print "Banery number = ", prob.variables.get_num_binary()
        print "Variable number = ", prob.variables.get_num()
        print "Contraint number = ", prob.linear_constraints.get_num(), "\n"
        header = Tlist
        # FUin: numU*numT
        M = sol.get_values(M_c, M_c + Mcount - 1)
        FinM = sol.get_values(FinM_c, FinM_c + FinMcount - 1)
        FUin_header = header[:]
        FUin_header.insert(0, "FUin")
        FUin_table_ = [0] * (numT + 1)
        FUin_table = []
        for U in Ulist[0:9]:
            FUin_table.append(FUin_table_[:])
        print "Unit Input Flowrate:  "
        FUin_table[0][0] = "ATM"
        FUin_table[1][0] = "VDU"
        FUin_table[2][0] = "FCCU"
        FUin_table[3][0] = "ETH"
        FUin_table[4][0] = "HDS"
        FUin_table[5][0] = "HTU1"
        FUin_table[6][0] = "HTU2"
        FUin_table[7][0] = "RF"
        FUin_table[8][0] = "MTBE"
        for U in Ulist[0:9]:
            for Mode in Mlist:
                FUin_table[U][1] += FinM[U * numM + Mode]
        print tabulate(FUin_table, FUin_header, tablefmt="simple", numalign="center", floatfmt=".3f")

        # FUinM: numU*numM*numT
        FUinM3_header = header[:]
        FUinM3_header.insert(0, "FUin[3M]")
        FUinM3_table_ = [0] * (numT + 1)
        FUinM3_table = []
        for U in Ulist[0:9]:
            FUinM3_table.append(FUinM3_table_[:])
        print "Unit Input Flowrate of Three Modes:  "
        FUinM3_table[0][0] = "ATM"
        FUinM3_table[1][0] = "VDU"
        FUinM3_table[2][0] = "FCCU"
        FUinM3_table[3][0] = "ETH"
        FUinM3_table[4][0] = "HDS"
        FUinM3_table[5][0] = "HTU1"
        FUinM3_table[6][0] = "HTU2"
        FUinM3_table[7][0] = "RF"
        FUinM3_table[8][0] = "MTBE"
        for U in Ulist[0:9]:
            X = [0.0] * 3
            for Mode in Mlist:
                X[0] += round(FinM[U * numM + Mode], 3)
            FUinM3_table[U][1] = X
        print tabulate(FUinM3_table, FUinM3_header, tablefmt="simple", numalign="center", floatfmt=".3f")

        # Print Fout
        FOCin = sol.get_values(FOCin_c, FOCin_c + FOCincount - 1)
        Fout_header = header[:]
        Fout_header.insert(0, "Fout")
        Fout_table_ = [0] * (numT + 1)
        Fout_table = []
        for U in range(11):
            Fout_table.append(Fout_table_[:])
        print "Output flowrate of Units:  "
        Fout_table[0][0] = "ATM"
        Fout_table[1][0] = "VDU"
        Fout_table[2][0] = "FCCU"
        Fout_table[3][0] = "ETH"
        Fout_table[4][0] = "HDS"
        Fout_table[5][0] = "HTU1"
        Fout_table[6][0] = "HTU2"
        Fout_table[7][0] = "RF"
        Fout_table[8][0] = "MTBE"
        Fout_table[9][0] = "Fen1"
        Fout_table[10][0] = "Fen2"
        for U in [Ulist[2], Ulist[3], Ulist[4]]:
                S_all = []
                for S in Slist:
                    Y = 0
                    for Mode in Mlist:
                        if M[U * numM + Mode] >= 0.1 and Y == 0:
                            Y = Yield[U * numM * numS + Mode * numS + S]
                            break
                    S_all.append(round(FUin_table[U][1] * Y, 3))
                Fout_table[U][1] = S_all
        for U in [Ulist[0], Ulist[1], Ulist[5], Ulist[6]]:
                S_all = []
                for S in Slist:
                    Y = 0
                    for Mode in Mlist:
                        if M[U * numM + Mode] >= 0.1 and Y == 0:
                            Y = Yield[U * numM * numS + Mode * numS + S]
                            break
                    S_all.append(round(FUin_table[U][1] * Y, 3))
                Fout_table[U][1] = S_all
        for U in [Ulist[7], Ulist[8]]:
                S_all = []
                for S in Slist:
                    S_all.append(round(FUin_table[U][1] * Yield[U * numM * numS + 0 * numS + S], 3))
                Fout_table[U][1] = S_all
        for U in [9]:
                Fout_table[U][1] = [round(FOCin[OClist[7]], 3), round(FUin_table[5][1], 3)]
        for U in [10]:
                Fout_table[U][1] = [round(FOCin[OClist[3]], 3), round(FUin_table[3][1], 3)]
        print tabulate(Fout_table, Fout_header, tablefmt="simple", numalign="center", floatfmt=".1f")

        # FOCO: numOC*numO*numT
        FOCO = sol.get_values(FOCO_c, FOCO_c + FOCOcount - 1)
        FOCO_header = header[:]
        FOCO_header.insert(0, "FOCO")
        FOCO_table_ = [0] * (numT + 1)
        FOCO_table = []
        for OC in OClist:
            for O in Olist:
                FOCO_table.append(FOCO_table_[:])
        print "blending Flowrate of OC to O: "
        for OC in OClist:
            for O in Olist:
                FOCO_table[OC * numO + O][0] = "OC" + str(OC) + " O" + str(O)
                FOCO_table[OC * numO + O][1] = FOCO[OC * numO + O]
        print tabulate(FOCO_table, FOCO_header, tablefmt="simple", numalign="center", floatfmt=".3f")
        # Opro: numO*numP
        Opro = sol.get_values(Opro_c, Opro_c + Oprocount - 1)
        Opro_header = range(numO)
        Opro_header.insert(0, "Opro")
        Opro_table_ = [0] * (numO + 1)
        Opro_table = []
        for P in Plist:
            Opro_table.append(Opro_table_[:])
        print "blending Flowrate of OC to O: "
        for P in Plist:
            Opro_table[P][0] = " P" + str(P)
            for O in Olist:
                Opro_table[P][O+1] = Opro[O * numP + P]
        print tabulate(Opro_table, Opro_header, tablefmt="simple", numalign="center", floatfmt=".3f")

        # FOout: numO*numL*numT
        FOout = sol.get_values(FOout_c, FOout_c + FOoutcount - 1)
        FOout_header = range(numO)
        FOout_header.insert(0, "FOout")
        FOout_table_ = [0] * (numO + 1)
        FOout_table = []
        for L in range(numL1):
            FOout_table.append(FOout_table_[:])
        print "Flowrate of O to Order: "
        for L in range(numL1):
            FOout_table[L][0] = " L" + str(L)
            for O in Olist:
                FOout_table[L][O+1] = FOout[O * numL1 + L]
        print tabulate(FOout_table, FOout_header, tablefmt="simple", numalign="center", floatfmt=".3f")
        order_header = range(numO)
        order_header.insert(0, "order_left")
        order_table_ = [0] * (numO + 1)
        order_table = []
        for L in range(numL1):
            order_table.append(order_table_[:])
        print "Amount of O in Order: "
        for L in range(numL1):
            order_table[L][0] = " L" + str(L)
            for O in Olist:
                order_table[L][O+1] = DV1_left[L][O]
        print tabulate(order_table, order_header, tablefmt="simple", numalign="center", floatfmt=".3f")
        orderT_header = range(numT_total)
        orderT_header.insert(0, "orderT")
        orderT_table_ = [0] * (numT_total + 1)
        orderT_table = []
        for L in range(numL1):
            orderT_table.append(orderT_table_[:])
        print "Time range of Order: "
        for L in range(numL1):
            orderT_table[L][0] = " L" + str(L)
            for T in range(numT_total):
                orderT_table[L][T+1] = DS1[L][T]
        print tabulate(orderT_table, orderT_header, tablefmt="simple", numalign="center", floatfmt=".3f")

        # PRO:numO*numT
        PRO_header = header[:]
        PRO_header.insert(0, "PRO")
        PRO_table_ = [0] * (numT + 1)
        PRO_table = []
        for O in Olist:
            for i in range(3):
                PRO_table.append(PRO_table_[:])
        for O in Olist[0:5]:
            PRO_table[O * 3 + 0][0] = "max"
            PRO_table[O * 3 + 1][0] = "O" + str(O)
            PRO_table[O * 3 + 2][0] = "min"
            for T in Tlist:
                F_sum = sum([FOCO[OC * numO + O] for OC in OClist[0:5]])
                if F_sum >= 0.001:
                    PRO_table[O * 3 + 0][T + 1] = "[" + str(PROMAX[0 * numO + O]) + " " + str(
                        PROMAX[2 * numO + O]) + "]"
                    PRO_table[O * 3 + 1][T + 1] = "[" + str(round(sum(
                        [FOCO[OC * numO + O] * PRO[0 * numOC + OC] for OC in OClist[0:5]]) / F_sum,
                                                                  2)) + " " + \
                                                  str(round(sum(
                                                      [FOCO[OC * numO + O] * PRO[2 * numOC + OC] for
                                                       OC in OClist[0:5]]) / F_sum, 4)) + "]"
                    PRO_table[O * 3 + 2][T + 1] = "[" + str(PROMIN[0 * numO + O]) + " " + str(
                        PROMIN[2 * numO + O]) + "]"
                elif T != 0:
                    PRO_table[O * 3 + 0][T + 1] = "[" + str(PROMAX[0 * numO + O]) + " " + str(
                        PROMAX[2 * numO + O]) + "]"
                    PRO_table[O * 3 + 1][T + 1] = PRO_table[O * 3 + 1][T]
                    PRO_table[O * 3 + 2][T + 1] = "[" + str(PROMIN[0 * numO + O]) + " " + str(
                        PROMIN[2 * numO + O]) + "]"
                else:
                    PRO_table[O * 3 + 0][T + 1] = "[" + str(PROMAX[0 * numO + O]) + " " + str(
                        PROMAX[2 * numO + O]) + "]"
                    PRO_table[O * 3 + 1][T + 1] = "INI"
                    PRO_table[O * 3 + 2][T + 1] = "[" + str(PROMIN[0 * numO + O]) + " " + str(
                        PROMIN[2 * numO + O]) + "]"
        for O in Olist[5:8]:
            PRO_table[O * 3 + 0][0] = "max"
            PRO_table[O * 3 + 1][0] = "O" + str(O)
            PRO_table[O * 3 + 2][0] = "min"
            for T in Tlist:
                F_sum = sum([FOCO[OC * numO + O] for OC in OClist[5:8]])
                if F_sum >= 0.001:
                    PRO_table[O * 3 + 0][T + 1] = "[" + str(PROMAX[1 * numO + O]) + " " + str(
                        PROMAX[2 * numO + O]) + " " + str(PROMAX[3 * numO + O]) + "]"
                    PRO_table[O * 3 + 1][T + 1] = "[" + str(round(sum(
                        [FOCO[OC * numO + O] * PRO[1 * numOC + OC] for OC in OClist[5:8]]) / F_sum,
                                                                  2)) + " " + \
                                                  str(round(sum(
                                                      [FOCO[OC * numO + O] * PRO[2 * numOC + OC] for
                                                       OC in OClist[5:8]]) / F_sum, 4)) + " " + \
                                                  str(round(sum(
                                                      [FOCO[OC * numO + O] * PRO[3 * numOC + OC] for
                                                       OC in OClist[5:8]]) / F_sum, 4)) + "]"
                    PRO_table[O * 3 + 2][T + 1] = "[" + str(PROMIN[1 * numO + O]) + " " + str(
                        PROMIN[2 * numO + O]) + " " + str(PROMIN[3 * numO + O]) + "]"
                elif T != 0:
                    PRO_table[O * 3 + 0][T + 1] = "[" + str(PROMAX[1 * numO + O]) + " " + str(
                        PROMAX[2 * numO + O]) + " " + str(PROMAX[3 * numO + O]) + "]"
                    PRO_table[O * 3 + 1][T + 1] = PRO_table[O * 3 + 1][T]
                    PRO_table[O * 3 + 2][T + 1] = "[" + str(PROMIN[1 * numO + O]) + " " + str(
                        PROMIN[2 * numO + O]) + " " + str(PROMIN[3 * numO + O]) + "]"
                else:
                    PRO_table[O * 3 + 0][T + 1] = "[" + str(PROMAX[1 * numO + O]) + " " + str(
                        PROMAX[2 * numO + O]) + " " + str(PROMAX[3 * numO + O]) + "]"
                    PRO_table[O * 3 + 1][T + 1] = "INI"
                    PRO_table[O * 3 + 2][T + 1] = "[" + str(PROMIN[1 * numO + O]) + " " + str(
                        PROMIN[2 * numO + O]) + " " + str(PROMIN[3 * numO + O]) + "]"
        print tabulate(PRO_table, PRO_header, tablefmt="simple", numalign="center", floatfmt=".3f")

        # EU: numU*numT
        EU_header = header[:]
        EU_header.insert(0, "EU")
        EU_table_ = [0] * (numT + 1)
        EU_table = []
        for U in range(0, 9):
            EU_table.append(EU_table_[:])
        print "Unit Energy Cost:  "
        EU_table[0][0] = "ATM"
        EU_table[1][0] = "VDU"
        EU_table[2][0] = "FCCU"
        EU_table[3][0] = "ETH"
        EU_table[4][0] = "HDS"
        EU_table[5][0] = "HTU1"
        EU_table[6][0] = "HTU2"
        EU_table[7][0] = "RF"
        EU_table[8][0] = "MTBE"
        for U in [Ulist[2]]:
                Y = 0
                for Mode in Mlist:
                    if M[U * numM + Mode] >= 0.1 and Y == 0:
                        Y = OpCost[U * numM + Mode]
                        break
                EU_table[U][1] = round(FUin_table[U][1] * Y * hours, 3)
        for U in [Ulist[0], Ulist[1], Ulist[5], Ulist[6], Ulist[3], Ulist[4]]:
                Y = 0
                for Mode in Mlist:
                    if M[U * numM + Mode] >= 0.1 and Y == 0:
                        Y = OpCost[U * numM + Mode]
                        break
                EU_table[U][1] = round(FUin_table[U][1] * Y * hours, 3)
        for U in [Ulist[7], Ulist[8]]:
                EU_table[U][1] = round(FUin_table[U][1] * OpCost[U * numM + 0] * hours, 3)
        print tabulate(EU_table, EU_header, tablefmt="simple", numalign="center", floatfmt=".3f")
        # VOC: numOC*numT
        VOC = sol.get_values(VOC_c, VOC_c + VOCcount - 1)
        VOC_header = [now_T - 1, now_T]
        VOC_header.insert(0, "VOC")
        VOC_table_ = [0] * (numT + 2)
        VOC_table = []
        for OC in OClist:
            VOC_table.append(VOC_table_[:])
        print "Volume of OC: "
        for OC in OClist:
            VOC_table[OC][0] = "OC" + str(OC)
            VOC_table[OC][1] = OCtank_ini[OC]
            VOC_table[OC][2] = VOC[OC]
        print tabulate(VOC_table, VOC_header, tablefmt="simple", numalign="center", floatfmt=".3f")
        print "VOC:", np.round(VOC, 2).tolist()

        # VO: numO*numT
        VO = sol.get_values(VO_c, VO_c + VOcount - 1)
        VO_header = [now_T - 1, now_T]
        VO_header.insert(0, "VO")
        VO_table_ = [0] * (numT + 2)
        VO_table = []
        for O in Olist:
            VO_table.append(VO_table_[:])
        print "Volume of O: "
        for O in Olist:
            VO_table[O][0] = "O" + str(O)
            VO_table[O][1] = Otank_ini[O]
            VO_table[O][2] = VO[O]
        print tabulate(VO_table, VO_header, tablefmt="simple", numalign="center", floatfmt=".3f")
        print "VO:", np.round(VO, 2).tolist()
        # M: numU*numM
        M = sol.get_values(M_c, M_c + Mcount - 1)
        M_header = [now_T - 1, now_T]
        M_header.insert(0, "M")
        M_table_ = [0] * (numT + 2)
        M_table = []
        for U in Ulist[0:9]:
            M_table.append(M_table_[:])
        print "Unit Mode:  "
        M_table[0][0] = "ATM"
        M_table[1][0] = "VDU"
        M_table[2][0] = "FCCU"
        M_table[3][0] = "ETH"
        M_table[4][0] = "HDS"
        M_table[5][0] = "HTU1"
        M_table[6][0] = "HTU2"
        M_table[7][0] = "RF"
        M_table[8][0] = "MTBE"
        for U in Ulist[0:9]:
            for Mode in Mlist:
                if M[U * numM + Mode] >= 0.1:
                    M_table[U][1] = Mode
                    break
                elif Mode == 3:
                    M_table[U][1] = "N/A"
            for Mode in Mlist:
                if mode_T[U * numM + Mode] >= 0.1:
                    M_table[U][2] = Mode
                    break
                elif Mode == 3:
                    M_table[U][2] = "N/A"
        print tabulate(M_table, M_header, tablefmt="simple", numalign="center", floatfmt=".1f")
        print "NowT:",now_T,"results: ",results
        Qout = sol.get_values(Qout_c, Qout_c + Qoutcount - 1)
        PoutA_header = header[:]
        PoutA_header.insert(0, "Qout")
        PoutA_table_ = [0] * (numT + 1)
        PoutA_table = []
        for O in range(numOC+1):#numO+
            PoutA_table.append(PoutA_table_[:])
        print "Asistant variables of Raw materials and Products: "
        for O in range(numOC):#numO+1+
            # if O == 0:
            #     PoutA_table[O][0] = "Cru-Oil"
            #     PoutA_table[O][1] = PoutA[O]
            # else:
                PoutA_table[O][0] = "Pro"+str(O)
                PoutA_table[O][1] = Qout[O]
        print tabulate(PoutA_table, PoutA_header, tablefmt="simple", numalign="center", floatfmt=".3f")
        Pout = sol.get_values(Pout_c, Pout_c + Poutcount - 1)
        PoutA = sol.get_values(PoutA_c, PoutA_c + PoutAcount - 1)
        Pout_header = header[:]
        Pout_header.insert(0, "Pout")
        Pout_table_ = [0] * (numT + 1)
        Pout_table = []
        for O in range(numOC+1):#numO+
            Pout_table.append(Pout_table_[:])
        print "Amount of Raw materials and Products: "
        for O in range(numOC):#numO+1+
            # if O == 0:
            #     Pout_table[O][0] = "Cru-Oil"
            #     Pout_table[O][1] = Pout[O]
            # else:
                Pout_table[O][0] = "Pro"+str(O)
                Pout_table[O][1] = Pout[O]
        print tabulate(Pout_table, Pout_header, tablefmt="simple", numalign="center", floatfmt=".3f")
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ Objective Value @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        partcost = 0
        for Modec in Mlist:
            partcost += FinM[0 * numM + Modec]
        partcost_cru = partcost
        ObjVal = 0

        partcost = 0
        for U in range(0, 9):
            partcost += EU_table[U][1]
        partcost_o = partcost
        ObjVal += partcost

        partcost = 0
        for OC in OClist:
            partcost += (VOC[OC]) * apoc
        partcost_VOC = partcost
        ObjVal += partcost

        partcost = 0
        for O in Olist:
            partcost += (VO[O]) * apo
        partcost_VO = partcost
        ObjVal += partcost

        partcost = 0
        for L in Llist1:
            for O in Olist:
                partcost += FOout[O * numL1 + L] *(-20*(numT_total-DS_num[L][1]))
        partcost_FOout = partcost
        ObjVal += partcost

        # partcost = 0
        # for O in range(numO + 1):
        #     partcost += Pout[O] * C_order*results_par[O]
        # partcost_Pout = partcost
        # ObjVal += partcost
        #
        # partcost = 0
        # for O in range(numO + 1):
        #     partcost += PoutA[O] * C_order*results_par[O] * (1+0.01)
        # partcost_PoutA = partcost
        # ObjVal += partcost

        print "crude oil output: ",partcost_cru,"operation cost: ", partcost_o, \
            "component oil inventory cost: ", partcost_VOC,\
            "Product inventory cost: ",partcost_VO,"FOout cost: ", partcost_FOout
            # "Pout cost: ", partcost_Pout,"PoutA cost: ", partcost_PoutA
        print "Pruduction Scheduling Objective: ", ObjVal

    return OC_inventory, O_inventory, FOout, Mode_act

def infer_data(MeanMinMax,t,numL1,DS_num, order_left, FOout,OC_inventory,O_inventory):
    # t is the number of present slot.
    # order_left represents the left amount of order at the last slot beginning.
    # FOout represents the product output flowrate in the last slot.
    # (order_left[L][O] - FOout[L,O] * hours) represents the left amount of order at the present slot beginning.
    Llist1 = range(numL1)
    Prod_flow = np.zeros((numO, numL1, n_num))
    # print "infer data order left:",order_left
    # print "infer data FOout:",FOout
    # print "DS_num:",DS_num
    for O in Olist:
        for L in Llist1:
            for n in range(0, n_num):
                if t + n <= DS_num[L][0]:
                    Prod_flow[O, L, n] = (order_left[L][O] - FOout[L, O] * hours) / (DS_num[L][1] - t + 1 - n)
                elif DS_num[L][0] < t + n <= DS_num[L][1]:
                    if n == 0:
                        Prod_flow[O, L, n] = (order_left[L][O] - FOout[L, O] * hours) / (DS_num[L][1] - t + 1)
                    else:
                        Prod_flow[O, L, n] = Prod_flow[O, L, n - 1]
                elif DS_num[L][1] < t + n:
                    Prod_flow[O, L, n] = 0
    inputdata = []
    raw_data = []
    for O in Olist:
        for n in range(n_num):
            Prod_sum = 0
            for L in Llist1:
                Prod_sum += Prod_flow[O,L,n]
            #     if O in [0,1]:
            #         print "t:",t," O:",O,"  n:",n,"  L:",L," Prod_flow:",Prod_flow[O,L,n]
            # if O in [0, 1]:
            #     print "t:", t, " O:", O, "  n:", n, " Prod_sum:", Prod_sum
            raw_data.append(Prod_sum)
            if Prod_sum > MeanMinMax[2,O*(n_num)+n]:
                Prod_sum = (MeanMinMax[2,O*(n_num)+n] - MeanMinMax[0,O*(n_num)+n])/(MeanMinMax[2,O*(n_num)+n] -
                                                                                    MeanMinMax[1,O*(n_num)+n])
            elif MeanMinMax[2,O*(n_num)] - MeanMinMax[1,O*(n_num)] != 0:
                Prod_sum = (Prod_sum - MeanMinMax[0,O*(n_num)+n])/(MeanMinMax[2,O*(n_num)+n] - MeanMinMax[1,O*(n_num)+n])
            inputdata.append(Prod_sum)
    # print "\n"
    for OC in OClist:
        if OC_inventory[OC] > MeanMinMax[2,numO*(n_num)+OC]:
            inputdata.append((MeanMinMax[2,numO*(n_num)+OC] - MeanMinMax[0,numO*(n_num)+OC])/(MeanMinMax[2,numO*(n_num)+OC] -
                                                                                   MeanMinMax[1,numO*(n_num)+OC]))
        elif MeanMinMax[2,numO*(n_num)+OC] - MeanMinMax[1,numO*(n_num)+OC] != 0:
            inputdata.append((OC_inventory[OC] - MeanMinMax[0,numO*(n_num)+OC])/(MeanMinMax[2,numO*(n_num)+OC] -
                                                                                   MeanMinMax[1,numO*(n_num)+OC]))
        else:
            inputdata.append(OC_inventory[OC])
        raw_data.append(OC_inventory[OC])
    for O in Olist:
        if O_inventory[O] > MeanMinMax[2,numO*(n_num)+numOC+O]:
            inputdata.append((MeanMinMax[2,numO*(n_num)+numOC+O] - MeanMinMax[0,numO*(n_num)+numOC+O])/(MeanMinMax[2,numO*(n_num)+numOC+O] -
                                                                                      MeanMinMax[1,numO*(n_num)+numOC+O]))
        elif MeanMinMax[2,numO*(n_num)+numOC+O] - MeanMinMax[1,numO*(n_num)+numOC+O] != 0:
            inputdata.append((O_inventory[O] - MeanMinMax[0,numO*(n_num)+numOC+O])/(MeanMinMax[2,numO*(n_num)+numOC+O] -
                                                                                      MeanMinMax[1,numO*(n_num)+numOC+O]))
        else:
            inputdata.append(O_inventory[O])
        raw_data.append(O_inventory[O])
    return inputdata, raw_data

def infer_data_P(MeanMinMax,t,numL1,DS_num, order_left, FOout,OC_inventory,O_inventory,sheet1,numT):
    # t is the number of present slot.
    # order_left represents the left amount of order at the last slot beginning.
    # FOout represents the product output flowrate in the last slot.
    # (order_left[L][O] - FOout[L,O] * hours) represents the left amount of order at the present slot beginning.
    Llist1 = range(numL1)
    Prod_flow = np.zeros((n_num, numO, numL1))
    Prod_fl_T = np.zeros((n_num, numO, numL1))
    Prod_fl_S = np.zeros((n_num, numO, numL1))
    INV_OC = np.zeros((numOC))
    INV_O = np.zeros((numO))
    # print "infer data order left:",order_left
    # print "infer data FOout:",FOout
    # print "DS_num:",DS_num
    for O in Olist:
        for L in Llist1:
            for n in range(0, n_num):
                if t + n <= DS_num[L][0]:
                    Prod_fl_T[n, O, L] = (order_left[L][O] - FOout[L, O] * hours) / (DS_num[L][1] - t-n + 1)
                elif DS_num[L][0] < t + n <= DS_num[L][1]:
                    if n == 0:
                        Prod_fl_T[n, O, L] = (order_left[L][O] - FOout[L, O] * hours) / (DS_num[L][1] - t-n + 1)
                    else:
                        Prod_fl_T[n, O, L] = Prod_fl_T[n-1, O, L]
                elif DS_num[L][1] < t + n:
                    Prod_fl_T[n, O, L] = 0
                if t + n < DS_num[L][0]:
                    Prod_fl_S[n, O, L] = 0
                elif DS_num[L][0] <= t + n <= DS_num[L][1]:
                    if n == 0:
                        Prod_fl_S[n, O, L] = (order_left[L][O] - FOout[L, O] * hours) / (DS_num[L][1] - t-n + 1)
                    elif t+n == DS_num[L][0]:
                        Prod_fl_S[n, O, L] = (order_left[L][O] - FOout[L, O] * hours) / (DS_num[L][1] - DS_num[L][0] + 1)
                    else:
                        Prod_fl_S[n, O, L] = Prod_fl_S[n-1, O, L]
                elif DS_num[L][1] < t + n:
                    Prod_fl_S[n, O, L] = 0

    #     if np.sum(order_left[:,O] - FOout[:, O] * hours) < 0.001:
    #         INV_O[O] = MeanMinMax[2,2*numO*(n_num)+numOC+O]
    #     else:
    #         INV_O[O] = O_inventory[O] / np.sum(order_left[:,O] - FOout[:, O] * hours)
    # for OC in OClist[:5]:
    #     if np.sum(order_left[:,:5] - FOout[:,:5] * hours) < 0.001:
    #         INV_OC[OC] = MeanMinMax[2,2*numO*(n_num)+OC]
    #     else:
    #         INV_OC[OC] = OC_inventory[OC] / np.sum(order_left[:,:5] - FOout[:,:5] * hours)
    # for OC in OClist[5:8]:
    #     if np.sum(order_left[:,5:8] - FOout[:,5:8] * hours) < 0.001:
    #         INV_OC[OC] = MeanMinMax[2,2*numO*(n_num)+OC]
    #     else:
    #         INV_OC[OC] = OC_inventory[OC] / np.sum(order_left[:,5:8] - FOout[:,5:8] * hours)

    for o in OClist:
        INV_OC[o] = OC_inventory[o]
    for o in Olist:
        INV_O[o] = O_inventory[o]
    inputdata = [0]*(8*2*n_num+16)
    raw_data = [0]*(8*2*n_num+16)
    for O in Olist:
        for n in range(n_num):
            Prod_sum_S = 0
            Prod_sum_T = 0
            for L in Llist1:
                Prod_sum_S += Prod_fl_S[n, O, L]
                Prod_sum_T += Prod_fl_T[n, O, L]
            #     if O in [0,1]:
            #         print "t:",t," O:",O,"  n:",n,"  L:",L," Prod_flow:",Prod_flow[O,L,n]
            # if O in [0, 1]:
            #     print "t:", t, " O:", O, "  n:", n, " Prod_sum:", Prod_sum  O*(n_num)+n
            raw_data[O * (n_num) + n] = Prod_sum_S
            sheet1.write(t + 1, 1 + (O * (n_num) + n), round(Prod_sum_S, 6))
            raw_data[numO*n_num + (O * (n_num) + n)] = Prod_sum_T
            sheet1.write(t + 1, 1 + numO*n_num + (O * (n_num) + n), round(Prod_sum_T, 6))
            if Prod_sum_S > MeanMinMax[2,O*(n_num)+n]:
                print "\n"
                print "%^^&&***((((((  Max Line Prod_sum_S  )))))#$%^^$##$%"
                print "\n"
                Prod_sum_S = (MeanMinMax[2,O*(n_num)+n] - MeanMinMax[0,O*(n_num)+n])/(MeanMinMax[2,O*(n_num)+n] -
                                                                                    MeanMinMax[1,O*(n_num)+n])
            elif Prod_sum_S < MeanMinMax[1,O*(n_num)+n]:
                print "\n"
                print "%^^&&***((((((  Min Line Prod_sum_S  )))))#$%^^$##$%"
                print "\n"
                Prod_sum_S = (MeanMinMax[1,O*(n_num)+n] - MeanMinMax[0,O*(n_num)+n])/(MeanMinMax[2,O*(n_num)+n] -
                                                                                    MeanMinMax[1,O*(n_num)+n])
            elif MeanMinMax[2,O*(n_num)+n] - MeanMinMax[1,O*(n_num)+n] != 0:
                Prod_sum_S = (Prod_sum_S - MeanMinMax[0,O*(n_num)+n])/(MeanMinMax[2,O*(n_num)+n] -
                                                                       MeanMinMax[1,O*(n_num)+n])
            inputdata[O * (n_num) + n] = Prod_sum_S
            sheet1.write(t + 2 + numT, 1 + (O * (n_num) + n), round(Prod_sum_S, 6))
            if Prod_sum_T > MeanMinMax[2,numO*n_num+O*(n_num)+n]:
                Prod_sum_T = (MeanMinMax[2,numO*n_num+O*(n_num)+n] - MeanMinMax[0,numO*n_num+O*(n_num)+n])/\
                             (MeanMinMax[2,numO*n_num+O*(n_num)+n] - MeanMinMax[1,numO*n_num+O*(n_num)+n])
            elif Prod_sum_T < MeanMinMax[1,numO*n_num+O*(n_num)+n]:
                print "\n"
                print "%^^&&***((((((  Min Line Prod_sum_T  )))))#$%^^$##$%"
                print "\n"
                Prod_sum_T = (MeanMinMax[1,numO*n_num+O*(n_num)+n] - MeanMinMax[0,numO*n_num+O*(n_num)+n])/\
                             (MeanMinMax[2,numO*n_num+O*(n_num)+n] - MeanMinMax[1,numO*n_num+O*(n_num)+n])
            elif MeanMinMax[2,numO*n_num+O*(n_num)+n] - MeanMinMax[1,numO*n_num+O*(n_num)+n] != 0:
                Prod_sum_T = (Prod_sum_T - MeanMinMax[0,numO*n_num+O*(n_num)+n])/\
                             (MeanMinMax[2,numO*n_num+O*(n_num)+n] - MeanMinMax[1,numO*n_num+O*(n_num)+n])
            inputdata[numO*n_num+(O * (n_num) + n)] = Prod_sum_T
            sheet1.write(t + 2 + numT, 1 + numO*n_num+(O * (n_num) + n), round(Prod_sum_T, 6))
    # print "\n"
    for OC in OClist:
        raw_data[OC + 2*numO * (n_num)] = round(INV_OC[OC], 6)
        sheet1.write(t + 1, OC + 2*numO * (n_num) + 1, round(INV_OC[OC], 6))
        if INV_OC[OC] > MeanMinMax[2,2*numO*(n_num)+OC]:
            v = (MeanMinMax[2,2*numO*(n_num)+OC] - MeanMinMax[0,2*numO*(n_num)+OC])/(MeanMinMax[2,2*numO*(n_num)+OC] -
                                                                                   MeanMinMax[1,2*numO*(n_num)+OC])
            inputdata[OC + 2*numO * (n_num)] = round(v, 6)
            sheet1.write(t + 2 + numT, OC + 2*numO * (n_num) + 1, round(v, 6))
        elif MeanMinMax[2,2*numO*(n_num)+OC] - MeanMinMax[1,2*numO*(n_num)+OC] != 0:
            v = (INV_OC[OC] - MeanMinMax[0,2*numO*(n_num)+OC])/(MeanMinMax[2,2*numO*(n_num)+OC] -
                                                                                   MeanMinMax[1,2*numO*(n_num)+OC])
            inputdata[OC + 2*numO * (n_num)] = round(v, 6)
            sheet1.write(t + 2 + numT, OC + 2*numO * (n_num) + 1, round(v, 6))
        else:
            inputdata[OC + 2*numO * (n_num)] = round(INV_OC[OC], 6)
            sheet1.write(t + 2 + numT, OC + 2*numO * (n_num) + 1, round(INV_OC[OC], 6))
    for O in Olist:
        raw_data[O + numOC + 2*numO * (n_num)] = round(INV_O[O], 6)
        sheet1.write(t + 1, O + numOC + 2*numO * (n_num) + 1, round(INV_O[O], 6))
        if INV_O[O] > MeanMinMax[2,2*numO*(n_num) + numOC+O] and \
            MeanMinMax[2,2*numO*(n_num) + numOC+O] - MeanMinMax[1,2*numO*(n_num) + numOC+O] == 0:
            v = 0
            inputdata[O + numOC + 2*numO * (n_num)] = round(v, 6)
            sheet1.write(t + 2 + numT, O + numOC + 2*numO * (n_num) + 1, round(v, 6))
        elif INV_O[O] > MeanMinMax[2,2*numO*(n_num) + numOC+O]:
            v = (MeanMinMax[2,2*numO*(n_num) + numOC+O] - MeanMinMax[0,2*numO*(n_num) + numOC+O])/\
                (MeanMinMax[2,2*numO*(n_num) + numOC+O] - MeanMinMax[1,2*numO*(n_num) + numOC+O])
            inputdata[O + numOC + 2*numO * (n_num)] = round(v, 6)
            sheet1.write(t + 2 + numT, O + numOC + 2*numO * (n_num) + 1, round(v, 6))
        elif MeanMinMax[2,2*numO*(n_num) + numOC+O] - MeanMinMax[1,2*numO*(n_num) + numOC+O] != 0:
            v = (INV_O[O] - MeanMinMax[0,2*numO*(n_num) + numOC+O])/\
                (MeanMinMax[2,2*numO*(n_num) + numOC+O] - MeanMinMax[1,2*numO*(n_num) + numOC+O])
            inputdata[O + numOC + 2*numO * (n_num)] = round(v, 6)
            sheet1.write(t + 2 + numT, O + numOC + 2*numO * (n_num) + 1, round(v, 6))
        else:
            inputdata[O + numOC + 2*numO * (n_num)] = round(INV_O[O], 6)
            sheet1.write(t + 2 + numT, O + numOC + 2*numO * (n_num) + 1, round(INV_O[O], 6))
    return inputdata, raw_data

def pre_net(img):
    w_param_attrs_conv1 = fluid.ParamAttr(name="conv1_weight", trainable=True)
    B_param_attrs_conv1 = fluid.ParamAttr(name="conv1_bais", trainable=True)
    conv_pool_1 = fluid.nets.simple_img_conv_pool(
        input=img,
        filter_size=[8, 12],
        num_filters=100,
        pool_size=1,
        pool_stride=1,
        act="relu",
        param_attr=w_param_attrs_conv1, bias_attr=B_param_attrs_conv1)
    w_param_attrs_fc1 = fluid.ParamAttr(name="fc1_weight", trainable=True)
    B_param_attrs_fc1 = fluid.ParamAttr(name="fc1_bais", trainable=True)
    fc_1 = fluid.layers.fc(input=conv_pool_1, size=10, act='tanh',
                           param_attr=w_param_attrs_fc1, bias_attr=B_param_attrs_fc1)
    w_param_attrs_conv21 = fluid.ParamAttr(name="conv21_weight", trainable=True)
    B_param_attrs_conv21 = fluid.ParamAttr(name="conv21_bais", trainable=True)
    conv_pool_2_1 = fluid.nets.simple_img_conv_pool(
        input=img,
        filter_size=[8, 1],
        num_filters=50,
        pool_size=1,
        pool_stride=1,
        act="relu",
        param_attr=w_param_attrs_conv21, bias_attr=B_param_attrs_conv21)
    w_param_attrs_conv22 = fluid.ParamAttr(name="conv22_weight", trainable=True)
    B_param_attrs_conv22 = fluid.ParamAttr(name="conv22_bais", trainable=True)
    conv_pool_2_2 = fluid.nets.simple_img_conv_pool(
        input=img,
        filter_size=[8, 3],
        num_filters=50,
        pool_size=1,
        pool_stride=1,
        act="relu",
        param_attr=w_param_attrs_conv22, bias_attr=B_param_attrs_conv22)
    w_param_attrs_conv23 = fluid.ParamAttr(name="conv23_weight", trainable=True)
    B_param_attrs_conv23 = fluid.ParamAttr(name="conv23_bais", trainable=True)
    conv_pool_2_3 = fluid.nets.simple_img_conv_pool(
        input=img,
        filter_size=[8, 5],
        num_filters=50,
        pool_size=1,
        pool_stride=1,
        act="relu",
        param_attr=w_param_attrs_conv23, bias_attr=B_param_attrs_conv23)
    conv_pool_2 = fluid.layers.concat(input=[conv_pool_2_1, conv_pool_2_2, conv_pool_2_3], axis=3)
    w_param_attrs_fc2 = fluid.ParamAttr(name="fc2_weight", trainable=True)
    B_param_attrs_fc2 = fluid.ParamAttr(name="fc2_bais", trainable=True)
    fc_2 = fluid.layers.fc(input=conv_pool_2, size=20, act='tanh',
                           param_attr=w_param_attrs_fc2, bias_attr=B_param_attrs_fc2)
    w_param_attrs_conv31 = fluid.ParamAttr(name="conv31_weight", trainable=True)
    B_param_attrs_conv31 = fluid.ParamAttr(name="conv31_bais", trainable=True)
    conv_pool_3_1 = fluid.nets.simple_img_conv_pool(
        input=img,
        filter_size=[1, 3],
        num_filters=50,
        pool_size=1,
        pool_stride=1,
        act="relu",
        param_attr=w_param_attrs_conv31, bias_attr=B_param_attrs_conv31)
    w_param_attrs_conv32 = fluid.ParamAttr(name="conv32_weight", trainable=True)
    B_param_attrs_conv32 = fluid.ParamAttr(name="conv32_bais", trainable=True)
    conv_pool_3_2 = fluid.nets.simple_img_conv_pool(
        input=img,
        filter_size=[1, 4],
        num_filters=50,
        pool_size=1,
        pool_stride=1,
        act="relu",
        param_attr=w_param_attrs_conv32, bias_attr=B_param_attrs_conv32)
    w_param_attrs_conv33 = fluid.ParamAttr(name="conv33_weight", trainable=True)
    B_param_attrs_conv33 = fluid.ParamAttr(name="conv33_bais", trainable=True)
    conv_pool_3_3 = fluid.nets.simple_img_conv_pool(
        input=img,
        filter_size=[1, 5],
        num_filters=50,
        pool_size=1,
        pool_stride=1,
        act="relu",
        param_attr=w_param_attrs_conv33, bias_attr=B_param_attrs_conv33)
    conv_pool_3 = fluid.layers.concat(input=[conv_pool_3_1, conv_pool_3_2, conv_pool_3_3], axis=3)
    w_param_attrs_fc3 = fluid.ParamAttr(name="fc3_weight", trainable=True)
    B_param_attrs_fc3 = fluid.ParamAttr(name="fc3_bais", trainable=True)
    fc_3 = fluid.layers.fc(input=conv_pool_3, size=20, act='tanh',
                           param_attr=w_param_attrs_fc3, bias_attr=B_param_attrs_fc3)
    fc = fluid.layers.concat(input=[fc_1, fc_2, fc_3], axis=1)
    w_param_attrs_fc1 = fluid.ParamAttr(name="fcall1_weight", trainable=True)
    B_param_attrs_fc1 = fluid.ParamAttr(name="fcall1_bais", trainable=True)
    fc_all1 = fluid.layers.fc(input=fc, size=80, act='tanh',
                              param_attr=w_param_attrs_fc1, bias_attr=B_param_attrs_fc1)
    w_param_attrs_fc2 = fluid.ParamAttr(name="fcall2_weight", trainable=True)
    B_param_attrs_fc2 = fluid.ParamAttr(name="fcall2_bais", trainable=True)
    fc_all2 = fluid.layers.fc(input=fc_all1, size=30, act='tanh',
                              param_attr=w_param_attrs_fc2, bias_attr=B_param_attrs_fc2)
    w_param_attrs_fc = fluid.ParamAttr(name="fc_weight", trainable=True)
    B_param_attrs_fc = fluid.ParamAttr(name="fc_bais", trainable=True)
    pre = fluid.layers.fc(input=fc_all2, size=output_num, #act='tanh',
                             param_attr=w_param_attrs_fc, bias_attr=B_param_attrs_fc)
    return pre

def infer_OC(MeanMinMax,inputdata,numT,t,sheet1, save_dirname=None, model_filename=None, params_filename=None):
    if save_dirname is None:
        return
    place = fluid.CPUPlace()
    exe = fluid.Executor(place)
    inputdata = np.array(inputdata, dtype='float32')
    # l = inputdata.reshape((1,input_num))
    insert_data = np.hstack((inputdata[8 * 2 * n_num:8 * 2 * n_num + 8],
                             inputdata[8 * 2 * n_num:8 * 2 * n_num + 8],
                             inputdata[8 * 2 * n_num + 8:],
                             inputdata[8 * 2 * n_num + 8:]))
    n = 0
    for ii in range(0, 8 * 2 * n_num, 10):
        inputdata = np.insert(inputdata, ii + 2 * n, insert_data[n])
        inputdata = np.insert(inputdata, ii + 2 * n + 1, insert_data[16 + n])
        n += 1
    l = inputdata[:8 * 2 * n_num + 32].reshape((1, 2, 8, 12))
    # print "infer input data:",l
    inference_scope = fluid.core.Scope()
    with fluid.scope_guard(inference_scope):
        [inference_program, feed_target_names,
         fetch_targets] = fluid.io.load_inference_model(
             save_dirname, exe, model_filename, params_filename)
        results = exe.run(
            inference_program,
            feed={feed_target_names[0]: l},
            fetch_list=fetch_targets)
        # print("Inference result of operation is: ", results)
        sheet1.write(t + 2 + numT, numO + numOC + 2*numO * (n_num) + 4 + 2 * numO + 2 * numOC,
                    round(results[0][0][0] * hours, 6))
        for OC in OClist:
            sheet1.write(t + 2 + numT, numO + numOC + 2*numO * (n_num) + 5 + 2 * numO + numO + 2 * numOC + OC,
                                round(results[0][0][OC], 6))
        # results = results[0][0] * (MeanMinMax[2,input_num+bias_OC:input_num+bias_OC+output_num] -  # Here is different from the HDA algorithm.
        #                            MeanMinMax[1,input_num+bias_OC:input_num+bias_OC+output_num]) \
        #                         + MeanMinMax[0,input_num+bias_OC:input_num+bias_OC+output_num]
        results = results[0][0]         # For TRL algorithm
        for OC in OClist:
            sheet1.write(t + 1, numO + numOC + 2*numO * (n_num) + 5 + 2 * numO + numO + 2 * numOC + OC,
                                round(results[OC], 6))
    return results

def write_head(sheet,numT):
    sheet.write(0, 0, "Slot")
    for t in range(numT):
        sheet.write(t+1, 0, t)
    for t in range(numT):
        sheet.write(t+2+numT, 0, t)
    for O in Olist:
        for n in range(0, n_num):
            if n == 0:
                sheet.write(0,O * (n_num) + n + 1, "O" + str(O)+"S" + str(n))
            else:
                sheet.write(0,O * (n_num) + n + 1, "S" + str(n))
            sheet.write(0,numO*n_num + O * (n_num) + n + 1, "T" + str(n))
    for OC in OClist:
        sheet.write(0, OC + 2*numO * (n_num) + 1, "OC" + str(OC))
    for O in Olist:
        sheet.write(0, O + numOC + 2*numO * (n_num) + 1, "O" + str(O))
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 1, "CRO_in")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 4, "JIV93")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 6, "JIV97")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 8, "G3I90")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 10, "G3I93")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 12, "G3I97")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 14, "G3I0")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 16, "G3I10")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 18, "GIV0")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 20, "OC0")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 22, "OC1")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 24, "OC2")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 26, "OC3")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 28, "OC4")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 30, "OC5")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 32, "OC6")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 34, "OC7")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 36, "CRO_in")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 37, "JIV93")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 38, "JIV97")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 39, "G3I90")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 40, "G3I93")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 41, "G3I97")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 42, "G3I0")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 43, "G3I10")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 44, "GIV0")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 45, "OC0")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 46, "OC1")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 47, "OC2")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 48, "OC3")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 49, "OC4")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 50, "OC5")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 51, "OC6")
    sheet.write(0, numO + numOC + 2*numO * (n_num) + 52, "OC7")

def fea_pro(Mode,Tlist,numT):
    for u in [0,1]:
        TT = 0
        for t in Tlist[1:]:
            if t >= numT-TTlist[0]:
                Mode[u, :, t] = Mode[u, :, t - 1]
            elif TT > 0:
                Mode[u,:,t] = Mode[u,:,t-1]
                TT -= 1
            elif np.argmax(Mode[u,:,t]) != np.argmax(Mode[u,:,t-1]):
                TT = TTlist[0]
    for u in [2,3,4]:
        TT = 0
        for t in Tlist[1:]:
            if t >= numT-TTlist[1]:
                Mode[u, :, t] = Mode[u, :, t - 1]
            elif TT > 0:
                Mode[u,:,t] = Mode[u,:,t-1]
                TT -= 1
            elif np.argmax(Mode[u,:,t]) != np.argmax(Mode[u,:,t-1]):
                TT = TTlist[1]
    for u in [5,6]:
        TT = 0
        for t in Tlist[1:]:
            if t >= numT-TTlist[2]:
                Mode[u, :, t] = Mode[u, :, t - 1]
            elif TT > 0:
                Mode[u,:,t] = Mode[u,:,t-1]
                TT -= 1
            elif np.argmax(Mode[u,:,t]) != np.argmax(Mode[u,:,t-1]):
                TT = TTlist[2]
    return Mode

test_case_num = 24

def read_test_order():
    book = xlrd.open_workbook("test_18case_DPSO_2.xls")#_2Order_test_case-old
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
    num_sample = 1
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    # read cases with various numT
    AnumT, AnumL1, ADV1, ADS_num, AOCtank_ini, AOtank_ini, ADS1, _ = read_test_order()
    at = TIME.localtime()
    bt = "%Y-%m-%d %H:%M:%S"
    for sample in range(num_sample):
        for i in range(len(CASE)):
            if CASE[i] == 'read-case-all_100-0':
                name = "100-0"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_120-1':
                name = "120-1"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_140-2':
                name = "140-2"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_160-3':
                name = "160-3"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_180-4':
                name = "180-4"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_200-5':
                name = "200-5"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_100-6':
                name = "100-6"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_120-7':
                name = "120-7"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_140-8':
                name = "140-8"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_160-9':
                name = "160-9"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_180-10':
                name = "180-10"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_200-11':
                name = "200-11"
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
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# sample:", name, "################"
                Pri = 0
                n_num = 10
                numL1,DV1,DS_num,OCtank_ini,Otank_ini,DS1=AnumL1[ol], ADV1[ol], ADS_num[ol], AOCtank_ini[ol], AOtank_ini[ol], ADS1[ol]
                Llist1 = range(numL1)
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_100-12':
                name = "100-12"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_120-13':
                name = "120-13"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_140-14':
                name = "140-14"
                ol = 14
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_160-15':
                name = "160-15"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_180-16':
                name = "180-16"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_200-17':
                name = "200-17"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_100-18':
                name = "100-18"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_120-19':
                name = "120-19"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_140-20':
                name = "140-20"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_160-21':
                name = "160-21"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_180-22':
                name = "180-22"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')
            elif CASE[i] == 'read-case-all_200-23':
                name = "200-23"
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
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                # book.save('Solving_results_LargeCASE' + name + '.xls')

            elif CASE[i] == 'VS-case1-9-13slots2-1.6':
                name = "-13-9"
                numT = 13
                Tlist = range(numT)
                VF = 1                                   # with or without Valid Functions
                TC = "time"                             # Termination_condition: gap or time
                if TC == "gap":
                    gap = 0.01
                    time = 0
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
                elif TC == "time":
                    gap = 0.0
                    time = 600
                    case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
                print "############################# VS-case1-9-13slots2:", sample, "################"
                numL1 = 3
                Llist1 = range(numL1)
                n_num = 10
                # DV1 = [
                #     [21, 40, 45, 40, 45, 123, 72, 115],
                #     [22, 36, 42, 42, 44, 168, 75, 90],
                #     [23, 30, 46, 33, 34, 92, 64, 70],
                #     [32, 33, 31, 25, 23, 83, 34, 90],
                #     [20, 35, 37, 30, 32, 113, 45, 107],
                #     [22, 27, 23, 28, 27, 93, 52, 70]]
                DV1 = [
                       [21,40,45,40,45,123,72,115],
                       [22,36,42,42,44,68,75,90],
                       [23,30,46,33,34,92,64,80],
                       [32,23,11,15,23,83,34,90],
                       [20,15,17,20,22,113,45,107],
                       [12,27,13,18,27,93,52,70]]
                DV1 = np.array(DV1)
                OCtank_ini = [9,1,12,2,6,4,7,3]
                Otank_ini = [7,1,7,1,2,12,8,5]
                Pri = 0
                DS_num = [
                          [0,5],
                          [6,13],
                          [4,9],
                          [2,11],
                          [4,12],
                          [1,10]]
                DS_num = np.array(DS_num)
                DV1 = np.array(DV1[:numL1]) #-np.array(DV1_1[:numL1])-np.array(DV1_2[:numL1])
                DS1 = np.zeros((numL1, numT))
                for L1 in Llist1:
                    DS1[L1, DS_num[L1, 0].astype(int):DS_num[L1, 1].astype(int) + 1] = 1
                sheet = book.add_sheet('case' + name, cell_overwrite_ok=True)
                for L in Llist1:
                    sheet.write(L, 0, "L" + str(L))
                    for O in Olist:
                        sheet.write(L, O + 1, DV1[L, O])
                for L in Llist1:
                    sheet.write(L + numL1 + 1, 0, "L" + str(L))
                    sheet.write(L + numL1 + 1, 1, DS_num[L, 0])
                    sheet.write(L + numL1 + 1, 2, DS_num[L, 1])
                sheet.write(numL1 + numL1 + 1, 0, "Slot")
                for T in Tlist:
                    sheet.write(numL1 + numL1 + 1, T + 1, "slot" + str(T))
                for L in Llist1:
                    sheet.write(L + 1 + numL1 + numL1 + 1, 0, "L" + str(L))
                    for T in Tlist:
                        sheet.write(L + 1 + numL1 + numL1 + 1, T + 1, DS1[L, T])

                for OC in OClist:
                    sheet.write(L + 1 + numL1 + numL1 + 2, OC, "OC" + str(OC))
                    sheet.write(L + 1 + numL1 + numL1 + 3, OC, OCtank_ini[OC])
                for O in Olist:
                    sheet.write(L + 1 + numL1 + numL1 + 4, O, "O" + str(O))
                    sheet.write(L + 1 + numL1 + numL1 + 5, O, Otank_ini[O])
                # book.save('Solving_results_LargeCASE' + name + '.xls')

            Mode_Unit = np.zeros((numU, numM, numT))
            T_state = [0] * numU
            T_state_last = [0] * numU
            T_Yield = [0] * numU * numS
            T_OpCost = [0] * numU
            T_state_times = [0] * numU
            FOout = np.zeros((numL1, numO))
            order_left = np.array(DV1)
            OC_inventory = OCtank_ini
            O_inventory = Otank_ini
            book1 = xlwt.Workbook(encoding='utf-8', style_compression=0)
            sheet1 = book1.add_sheet('case' + name, cell_overwrite_ok=True)
            write_head(sheet1,numT)
            Timestart = TIME.time()
            for t in Tlist:#range(1):
                mode_T = [0] * (numU * numM)  # Including modes of FCCU/ETH/HDS units
                data_l,raw_l = infer_data_P(MeanMinMax_l,t,numL1,DS_num, order_left, FOout,OC_inventory,O_inventory,sheet1,numT)
                results = infer_OC(MeanMinMax_l,data_l,numT,t,sheet1,save_dirname_l,model_filename_l,params_filename_l)
                results = results.astype(float)
                Pri = 0
                results_par = [1]*(numO+numOC)
                order_left = order_left - FOout     # order_left[numL1,numO]
                O_inventory_ = np.copy(O_inventory)
                OC_inventory, O_inventory, FOout, Mode_act = PRO_opt_TT(numT,t,numL1,Llist1,Pri,order_left,DS1,DS_num,
                                                OC_inventory,O_inventory,results,results_par,mode_T,T_state,T_Yield,T_OpCost)
                # print "t:",t,"OC_inventory:",OC_inventory
                # print "t:",t,"O_inventory:",O_inventory
                # print "t:",t,"FOout:",FOout
                Mode_Unit[:,:,t] = np.array(Mode_act).reshape((numU,numM))    # Mcount = numU * numM in PRO_opt.
                FOout = np.array(FOout).reshape((numO, numL1)).T   # FOout[numL1, numO]
                if t == 0:
                    for O in Olist:
                        v = sum([FOout[L, O] for L in Llist1]) + O_inventory[O] - Otank_ini[O]
                        sheet1.write(t + 1, numO + numOC + 2 * numO * (n_num) + 5 + 2 * numO + 2 * numOC + O, round(v, 6))
                else:
                    for O in Olist:
                        v = sum([FOout[L, O] for L in Llist1]) + O_inventory[O] - O_inventory_[O]
                        sheet1.write(t + 1, numO + numOC + 2 * numO * (n_num) + 5 + 2 * numO + 2 * numOC + O, round(v, 6))

            # book1.save('data_LargeCASE07_hcase' + name + '.xls')
            # gap = 0
            Mode_Unit = fea_pro(Mode_Unit,Tlist,numT)
            Mode_Unit = Mode_Unit.reshape((numU*numM*numT,)).tolist()

            print("################## The Whole Solution ##################### ")
            Pri = 1
            # PRO2(numT, numL1, DV1, DS1, gap, Mode_Unit)
            # objective2 = PRO2(numT, Tlist, numL1, Llist1, DS1, DV1, Pri, Mode_Unit)
            # objective2 = PRO2(numT,numL1,DV1,DS1,gap,Mode_act)
            objective2 = PRO2(numT, Tlist, numL1, Llist1, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode_Unit)
            print "Time cost:", TIME.time()-Timestart
            print "### Time:", TIME.strftime(bt,at),"###"
            objective1, Crud_in, gap = PRO1(numT, Tlist, numL1, Llist1, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode_Unit)
            sheet.write(L + 1 + numL1 + numL1 + 6, 0, "objective1")
            sheet.write(L + 1 + numL1 + numL1 + 6, 1, objective2)
            sheet.write(L + 1 + numL1 + numL1 + 7, 0, "objective2")
            sheet.write(L + 1 + numL1 + numL1 + 7, 1, objective1)
            # sheet.write(L + 1 + numL1 + numL1 + 7, 2, "dual")
            # sheet.write(L + 1 + numL1 + numL1 + 7, 3, dual)
            sheet.write(L + 1 + numL1 + numL1 + 7, 4, "gap")
            sheet.write(L + 1 + numL1 + numL1 + 7, 5, gap)
            for t in Tlist[:200]:
                sheet.write(L + 1 + numL1 + numL1 + 8, t, Crud_in[t])
        book.save('Solving_results_LargeCASE-TRL211011'+ name + '.xls')
        #     random_num = 1
        #     sheet = book.add_sheet('case-s' + name, cell_overwrite_ok=True)
        #     Obj = [0] * random_num
        #     for r in range(random_num):
        #         print "=============== suiji",r," ==================="
        #         Mode_Unit = np.zeros((numU,numM,numT))
        #         T_state = [0] * numU
        #         T_state_last = [0] * numU
        #         T_state_times = [0] * numU
        #         for t in Tlist:
        #             for U in Ulist:
        #                 if t >= 2:
        #                     if T_state_times[U] != 0:
        #                         T_state_times[U] -= 1
        #                         T_state[U] = 1
        #                     elif (U in [0, 1] and t >= numT - 3 - 1) or (U in [2, 3, 4] and t >= numT - 2 - 1) or (
        #                                     U in [5, 6] and t >= numT - 1 - 1):
        #                         T_state_last[U] = 1
        #                         T_state[U] = 0
        #                     elif sum(np.abs(Mode_Unit[U, :, t - 1] - Mode_Unit[U, :, t - 2])) != 0:
        #                         if U in [0, 1]:
        #                             T_state_times[U] = 2
        #                         elif U in [2, 3, 4]:
        #                             T_state_times[U] = 1
        #                         elif U in [5, 6]:
        #                             T_state_times[U] = 0
        #                         T_state[U] = 1
        #                     else:
        #                         T_state[U] = 0
        #                 if T_state[U] == 1 or T_state_last[U] == 1:
        #                     Mode_Unit[U, np.argmax(Mode_Unit[U, :, t - 1]), t] = 1
        #                 else:
        #                     if U in [0, 1, 5, 6]:
        #                         Mode_Unit[U, np.random.randint(0,2), t] = 1
        #                     elif U in [2]:
        #                         Mode_Unit[U, np.random.randint(0,4), t] = 1
        #                     elif U in [7, 8]:
        #                         Mode_Unit[U, 0, t] = 1
        #         Mode_Unit[3, :, :] = Mode_Unit[2, :, :]
        #         Mode_Unit[4, :, :] = Mode_Unit[2, :, :]
        #         Mode_Unit = Mode_Unit.reshape((numU*numM*numT,)).tolist()
        #         objective2 = PRO2(numT, Tlist, numL1, Llist1, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode_Unit)
        #         sheet.write(r, 0, r)
        #         sheet.write(r, 1, objective2)
        #         Obj[r] = objective2
        #     meanV = np.mean(Obj)
        #     maxV = np.max(Obj)
        #     minV = np.min(Obj)
        #     sheet.write(r+1, 0, "mean")
        #     sheet.write(r+1, 1, meanV)
        #     sheet.write(r+2, 0, "max")
        #     sheet.write(r+2, 1, maxV)
        #     sheet.write(r+3, 0, "min")
        #     sheet.write(r+3, 1, minV)
        # book.save('Solving_results_LargeCASE'+name + '_details_S.xls')
mean_l= [23.367035, 16.994191, 14.711604, 13.433808, 12.446063, 11.526283, 10.563673, 9.513687, 8.370137, 7.121449, 22.153565, 16.769212, 14.687206, 13.462022, 12.501687, 11.590227, 10.62679, 9.573292, 8.418157, 7.15492, 14.809299, 13.058894, 12.486369, 12.089494, 11.616373, 11.020006, 10.258665, 9.341686, 8.277545, 7.074462, 15.055228, 13.085518, 12.476556, 12.082446, 11.613205, 11.009558, 10.249164, 9.329648, 8.264611, 7.062698, 15.09487, 13.069458, 12.425843, 12.018936, 11.550624, 10.950811, 10.196025, 9.280492, 8.219078, 7.022412, 12.903355, 16.912589, 19.435173, 20.898371, 21.312345, 20.976275, 20.037687, 18.590169, 16.723389, 14.492913, 36.344453, 29.612545, 27.208713, 25.772285, 24.477982, 23.058242, 21.387535, 19.455707, 17.263655, 14.81638, 22.18736, 22.025317, 22.549987, 22.857237, 22.592115, 21.811884, 20.577207, 18.93826, 16.945666, 14.628512, 32.859126, 25.316886, 21.898634, 19.526772, 17.490856, 15.568672, 13.666746, 11.752975, 9.831434, 7.919798, 31.647247, 25.092806, 21.874867, 19.556479, 17.546702, 15.632601, 13.72914, 11.810133, 9.878128, 7.952362, 24.318518, 21.395513, 19.685529, 18.195649, 16.67174, 15.069261, 13.365306, 11.580981, 9.738575, 7.872778, 24.567702, 21.423741, 19.675036, 18.184624, 16.664763, 15.058021, 13.356673, 11.572105, 9.729461, 7.863004, 24.585273, 21.387272, 19.605973, 18.10388, 16.585867, 14.983209, 13.289137, 11.511415, 9.676325, 7.82053, 32.218455, 33.849674, 34.065775, 33.318006, 31.615326, 29.255952, 26.418621, 23.21416, 19.756519, 16.154386, 55.658862, 46.55083, 41.841789, 38.194805, 34.782682, 31.334961, 27.762047, 24.07252, 20.292355, 16.478024, 41.503501, 38.966524, 37.190155, 35.284872, 32.901721, 30.094577, 26.961587, 23.562876, 19.979355, 16.292474, 2.199378, 11.408053, 6.666477, 10.120172, 6.553411, 95.001664, 26.323009, 18.001698, 0.680383, 0.685545, 0.679583, 0.652857, 0.684581, 1.695244, 1.573464, 1.438533]
min_l= [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
max_l= [319.266205, 179.846252, 147.133331, 140.509521, 137.176193, 134.729767, 133.816666, 133.816666, 133.816666, 133.816666, 290.325073, 175.715988, 153.812744, 146.204239, 144.480209, 141.878967, 140.180557, 138.844437, 138.844437, 138.844437, 284.878113, 143.913391, 135.54834, 140.494476, 137.78624, 137.321304, 138.271271, 140.191666, 139.809845, 139.809845, 253.557022, 146.149994, 133.665619, 141.683334, 141.683334, 141.683334, 141.683334, 141.683334, 141.683334, 141.683334, 247.830643, 141.497177, 121.414543, 114.618652, 117.334923, 119.78437, 119.194443, 120.245239, 120.245239, 121.89286, 259.0, 205.216797, 232.55098, 255.266663, 255.266663, 255.266663, 255.266663, 259.277771, 259.277771, 259.277771, 654.913025, 342.173187, 286.899994, 279.350006, 279.350006, 279.350006, 279.350006, 279.350006, 279.350006, 279.350006, 353.083405, 215.199997, 213.680954, 226.583328, 226.583328, 226.583328, 226.583328, 226.583328, 226.583328, 226.583328, 319.266205, 179.846252, 147.133331, 140.509521, 137.176193, 134.729767, 133.816666, 133.816666, 133.816666, 133.816666, 290.325073, 175.715988, 153.812744, 146.204239, 144.480209, 141.878967, 140.180557, 138.844437, 138.844437, 138.844437, 284.878113, 143.913391, 135.54834, 140.494476, 137.78624, 137.321304, 138.271271, 140.191666, 139.809845, 139.809845, 253.557022, 146.149994, 133.665619, 141.683334, 141.683334, 141.683334, 141.683334, 141.683334, 141.683334, 141.683334, 247.830643, 147.097168, 127.014549, 126.185715, 126.185715, 126.185715, 126.185715, 126.185715, 126.185715, 121.89286, 259.0, 217.05098, 235.583328, 255.266663, 255.266663, 255.266663, 255.266663, 259.277771, 259.277771, 259.277771, 654.913025, 342.173187, 286.899994, 279.350006, 279.350006, 279.350006, 279.350006, 279.350006, 279.350006, 279.350006, 353.083405, 242.611984, 232.300003, 244.300003, 244.300003, 244.300003, 244.300003, 244.300003, 244.300003, 232.709518, 31.00746, 200.70578, 47.380035, 262.501801, 126.400879, 769.281067, 414.393158, 378.988007, 9.0, 9.0, 9.0, 9.0, 9.0, 162.666672, 120.707596, 200.0]

# mean_l= [22.54967, 16.38824, 14.16709, 12.93163, 11.99912, 11.12741, 10.21206, 9.22702, 8.13346, 6.93673, 21.4515, 16.26019, 14.2302, 13.03189, 12.09656, 11.21227, 10.28293, 9.28197, 8.17417, 6.95902, 14.45138, 12.72583, 12.11762, 11.70276, 11.24513, 10.66291, 9.93023, 9.06452, 8.04517, 6.89325, 14.53358, 12.65508, 12.06409, 11.69622, 11.25681, 10.68765, 9.9564, 9.08465, 8.05481, 6.89066, 14.74942, 12.77243, 12.12968, 11.70978, 11.24983, 10.66897, 9.93346, 9.06297, 8.04119, 6.88392, 16.07617, 18.55925, 20.29097, 21.28595, 21.44253, 20.9543, 19.93024, 18.48834, 16.63875, 14.42967, 36.11417, 29.29761, 26.81074, 25.33585, 24.07625, 22.68488, 21.06486, 19.2063, 17.06674, 14.66597, 18.17174, 19.9635, 21.27661, 21.97809, 21.95349, 21.32986, 20.20778, 18.68692, 16.77784, 14.52598, 31.71021, 24.43099, 21.12036, 18.83597, 16.89452, 15.06194, 13.23528, 11.40856, 9.56425, 7.72491, 30.5998, 24.29068, 21.17454, 18.92808, 16.98699, 15.14264, 13.30109, 11.4569, 9.59707, 7.73998, 23.60243, 20.7619, 19.06687, 17.60485, 16.13986, 14.59729, 12.95372, 11.24695, 9.47608, 7.67991, 23.72351, 20.72515, 19.04332, 17.62043, 16.16552, 14.62714, 12.97807, 11.25935, 9.47701, 7.67082, 23.92934, 20.83351, 19.09987, 17.62842, 16.1572, 14.61095, 12.96151, 11.2455, 9.46946, 7.66981, 34.99077, 35.18459, 34.68456, 33.52739, 31.61259, 29.15335, 26.25852, 23.07361, 19.65523, 16.10121, 55.00807, 45.9021, 41.18412, 37.55869, 34.22516, 30.86294, 27.36773, 23.77035, 20.07036, 16.32922, 37.08124, 36.58642, 35.66642, 34.21714, 32.12069, 29.52423, 26.52985, 23.268, 19.78852, 16.18949, 2.1531, 11.22421, 6.73185, 9.68827, 6.62526, 95.45024, 25.4359, 18.31947, 0.66113, 0.66606, 0.65823, 0.65919, 0.65377, 1.57489, 1.51773, 1.39511, 5.77366, 7.53692, 11.42985, 11.06073, 11.08466, 28.65948, 20.4139, 28.01327, 1.99146, 17.92317, 3.52675, 20.05329, 5.05987, 51.29095, 37.81823, 8.55764]
# min_l= [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.08609, 9.77479, 2.18228, 0.0, 4.5, 36.9304, 4.97, 0.0]
# max_l= [301.14438, 168.73329, 135.47638, 120.38525, 114.21049, 111.94968, 111.50519, 112.68658, 112.25476, 111.88937, 277.77737, 166.10001, 139.7, 130.53334, 124.88333, 122.33334, 120.92857, 119.875, 119.05556, 119.05556, 230.00053, 128.53334, 106.05036, 107.71905, 108.23333, 108.23333, 108.94478, 114.73333, 114.73333, 114.73333, 260.24997, 139.03874, 110.61684, 107.33309, 107.93684, 109.81439, 109.48055, 108.68889, 108.68889, 108.68889, 203.75262, 125.83199, 112.4884, 110.20953, 111.99167, 111.31111, 111.31111, 112.48008, 114.53333, 114.53333, 267.0, 188.02141, 187.57562, 201.56667, 201.56667, 201.56667, 210.81667, 210.81667, 211.27121, 219.56667, 567.0, 335.17743, 280.43527, 257.44449, 242.94901, 236.23872, 232.55505, 229.74265, 227.5231, 226.98137, 364.59964, 216.37314, 203.75, 203.75, 218.03572, 216.75, 216.75, 216.75, 216.75, 216.75, 301.14438, 168.73329, 135.47638, 120.38525, 119.34949, 119.09064, 122.6, 122.79643, 122.6, 122.6, 277.77737, 166.10001, 139.7, 130.53334, 124.88333, 122.33334, 120.92857, 119.875, 119.05556, 119.05556, 230.00053, 139.76793, 115.53333, 118.16933, 117.94206, 117.74976, 117.74976, 114.73333, 114.73333, 114.73333, 260.24997, 139.99429, 117.96117, 116.65119, 116.27018, 118.14773, 117.81389, 117.6, 117.6, 117.6, 204.27185, 141.90985, 123.03187, 120.47659, 119.80992, 119.80992, 119.80992, 119.80992, 119.80992, 114.53333, 267.0, 204.57143, 231.98633, 231.65672, 232.50082, 235.74533, 235.74533, 224.89999, 224.89999, 224.89999, 567.0, 335.17743, 280.43527, 257.44449, 242.94901, 236.23872, 234.05, 234.05, 234.05, 234.05, 364.59964, 224.20648, 228.96388, 228.96388, 228.96388, 228.96388, 228.96388, 216.75, 216.75, 216.75, 31.51951, 222.66901, 44.3617, 256.8334, 126.40088, 741.0957, 422.93646, 393.98801, 9.0, 9.0, 9.0, 9.0, 9.0, 133.33333, 113.2924, 83.0, 129.09076, 124.61226, 144.51404, 137.0, 152.31178, 225.72247, 124.84395, 205.46649, 2.7063, 24.35666, 4.35621, 27.03092, 13.56681, 63.91981, 57.85975, 53.209]

mean_b= [23.023547, 17.371682, 14.822004, 13.22718, 12.04546, 11.016361, 10.02153, 9.007689, 7.944961, 6.811235, 21.191565, 16.510503, 14.352019, 12.953374, 11.868087, 10.894359, 9.932935, 8.93753, 7.886427, 6.766805, 16.688683, 14.55715, 13.403402, 12.495931, 11.64827, 10.794162, 9.89298, 8.929034, 7.892108, 6.775553, 16.803727, 14.594678, 13.413751, 12.495477, 11.644954, 10.788201, 9.88562, 8.918005, 7.878398, 6.760177, 17.176574, 14.748371, 13.482595, 12.523827, 11.653675, 10.79087, 9.88525, 8.91998, 7.88373, 6.770045, 17.263768, 16.667302, 15.985991, 15.186674, 14.252374, 13.240151, 12.146748, 10.964744, 9.689067, 8.317781, 17.366803, 16.694246, 15.990571, 15.183299, 14.24751, 13.238083, 12.145368, 10.968696, 9.696981, 8.326606, 17.251131, 16.63758, 15.953058, 15.152596, 14.219464, 13.211556, 12.120405, 10.94271, 9.6724, 8.306295, 11.475, 9.840719, 8.303404, 6.865822, 5.534139, 4.317981, 3.225953, 2.265508, 1.456051, 0.814465, 11.381676, 9.760019, 8.232883, 6.805985, 5.487758, 4.282346, 3.19922, 2.248784, 1.449395, 0.811936, 11.397703, 9.773496, 8.244631, 6.815681, 5.492803, 4.284246, 3.200058, 2.24773, 1.446257, 0.808966, 11.412179, 9.784886, 8.251347, 6.818142, 5.49121, 4.28272, 3.197329, 2.24557, 1.444321, 0.807788, 11.432511, 9.803769, 8.269975, 6.83688, 5.511602, 4.301427, 3.215387, 2.259965, 1.454623, 0.812774, 14.047796, 12.054024, 10.174969, 8.417261, 6.790879, 5.307753, 3.975337, 2.80581, 1.820684, 1.033895, 14.114704, 12.117756, 10.236366, 8.475919, 6.845289, 5.355099, 4.016827, 2.838603, 1.845734, 1.053643, 14.064002, 12.071219, 10.193144, 8.43767, 6.81179, 5.326895, 3.992537, 2.819291, 1.830236, 1.041373, 8.889514, 29.979871, 14.784882, 27.389704, 21.57139, 272.777613, 81.55021, 57.896566, 0.560493, 0.542471, 0.513212, 0.51177, 0.52178, 2.449411, 2.442554, 2.458308, 0.368417, 0.044382, 0.587201, 0.095882, 0.904118, 0.082521, 0.917479, 0.071944, 0.928056, 0.070917, 0.929083, 0.073646, 0.926354, 0.143278, 0.856722, 0.144965, 0.855035, 0.145625, 0.854375, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.084347, 0.915653, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.41059, 0.58941, 260.949734, 7.262992, 8.357119, 11.492758, 11.383469, 11.113866, 16.257991, 16.12234, 16.18259, 2.204592, 19.841327, 3.564577, 19.530248, 5.56372, 49.680463, 23.295316, 17.631509]
min_b= [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 200.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.086088, 9.77479, 2.182279, 0.0, 4.5, 36.930401, 4.97, 0.0]
max_b= [341.937653, 188.276382, 140.889297, 119.279083, 107.312958, 100.235542, 96.549706, 95.326187, 94.819016, 94.702156, 330.287537, 183.287552, 136.954208, 116.608604, 107.508606, 102.108604, 98.965752, 97.090752, 96.007416, 95.539879, 230.666672, 131.0, 103.553589, 97.553589, 95.053589, 94.822578, 94.822578, 94.822578, 94.822578, 94.822578, 234.827286, 136.816666, 103.650002, 96.949532, 94.658844, 93.831718, 93.812347, 93.812347, 93.812347, 93.812347, 246.412338, 133.427139, 108.552292, 104.052292, 102.952293, 102.952293, 102.952293, 102.952293, 102.952293, 102.952293, 139.090668, 139.090668, 139.090668, 139.090668, 139.090668, 139.090668, 139.090668, 139.090668, 139.090668, 139.090668, 163.148026, 138.144852, 138.144852, 138.144852, 138.144852, 138.144852, 138.144852, 138.144852, 138.144852, 138.144852, 139.663391, 139.663391, 139.663391, 139.663391, 139.663391, 139.663391, 139.663391, 139.663391, 139.663391, 139.663391, 98.093452, 93.431557, 87.962601, 81.745857, 79.989731, 79.989731, 79.989731, 76.856888, 75.198135, 68.247215, 105.329582, 105.329582, 97.766792, 91.006653, 91.006653, 85.941956, 74.696274, 72.025337, 70.066933, 66.693771, 104.773537, 104.773537, 104.773537, 102.299652, 89.769966, 89.769966, 82.316216, 76.558723, 70.679207, 64.911766, 94.970383, 88.79644, 88.79644, 88.79644, 88.79644, 82.224319, 82.224319, 82.224319, 70.552544, 70.552544, 90.615562, 89.10862, 87.55806, 86.132065, 84.406097, 82.02166, 79.928268, 77.463234, 74.520645, 70.447395, 122.31897, 121.087967, 121.087967, 117.095886, 115.656807, 112.376518, 109.578934, 105.837082, 101.184715, 94.231979, 122.387978, 120.101669, 117.921379, 115.455582, 112.921867, 111.765182, 106.760345, 103.681564, 97.875969, 93.035004, 122.150948, 121.696823, 121.051369, 118.200043, 117.039803, 113.474136, 109.255287, 104.838692, 99.892159, 94.905258, 42.625801, 194.718246, 57.654446, 223.512253, 135.454071, 836.979126, 375.130249, 424.436859, 9.0, 9.0, 9.0, 9.0, 9.0, 29.0, 29.0, 29.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 300.0, 47.705605, 56.223808, 64.17926, 63.481117, 64.166664, 139.090668, 124.843948, 139.663391, 2.706296, 24.356663, 4.356209, 27.030918, 19.424021, 61.175903, 57.859745, 41.047001]


MeanMinMax_l = np.array([mean_l,min_l,max_l],dtype='float32')
MeanMinMax_b = np.array([mean_b,min_b,max_b],dtype='float32')
# save_dirname_l = "PRO_RL_Policy_all-3" # ********* FOR TRL ***********
# model_filename_l = "all_policy.model"
# params_filename_l = "all_policy.param"
save_dirname_l = "PRO_RL_Policy_all-R-3" # ********* FOR RL ***********
model_filename_l = "all_policy.model"
params_filename_l = "all_policy.param"
save_dirname_b = "PRO_NN_n_num_allslot0930_B.model"
model_filename_b = "all_policy.model"
params_filename_b = "all_policy.param"
n_num = 10
slot_num = 15
input_num = 8*(2*n_num) # +16
bias_OC = 0 # 0
output_num = 8
input_b_num = 0 # 19+9+16
output_num_l = 0
output_num_b = 0
CASE = [
        # 'read-case-all_100-0', 
        # 'read-case-all_100-6',
        # 'read-case-all_100-12',  
        # 'read-case-all_100-18', 
        # 'read-case-all_120-1',
        # 'read-case-all_120-7',
        # 'read-case-all_120-13',
        # 'read-case-all_120-19',
        # 'read-case-all_140-2',
        # 'read-case-all_140-8',
        # 'read-case-all_140-14',
        # 'read-case-all_140-20',
        # 'read-case-all_160-3',
        # 'read-case-all_160-9', 
        # 'read-case-all_160-15', 
        # 'read-case-all_160-21', 
        # 'read-case-all_180-4',
        # 'read-case-all_180-10',
        # 'read-case-all_180-16',
        # 'read-case-all_180-22',
        # 'read-case-all_200-5', #
        # 'read-case-all_200-11', 
        # 'read-case-all_200-17', 
        # 'read-case-all_200-23',  
        # 'VS-case1-9-13slots2-1.6'   # ********* FOR THE DETAILS OF SCHEDULING ***********

        ]
run(CASE)

