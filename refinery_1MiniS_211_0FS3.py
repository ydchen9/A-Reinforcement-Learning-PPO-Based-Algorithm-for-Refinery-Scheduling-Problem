import cplex
from cplex.callbacks import MIPInfoCallback
import numpy as np
from tabulate import tabulate
#U /ATM 0,VCD 1,FCCU 2,ETH 3,HDS 4,HTU1 5,HTU2 6,RF 7,MTBE 8/
#M /A 0,G 1,D 2,GG 3,GD 4,DG 5,DD 6,M 7,H 8/
#T /t1*tnumT/
#S /s1*s4/
#O /JIV93 0,JIV97 1,GII90 2,GII93 3,GII97 4,GII0 5,GIIM10 6,GIV0 7/
#OC /C5 0,Reformate 1,MTBE 2,HDS 3,Etherified 4,diesel1 5,diesel2 6,Lightdi 7/
#P /RON,CN,S,CPF/
#L /L1,L2/
#TL /TL1,TL2/
#LimitV /MIN,MAX/
#ObjectFunction..Object       =e= sum(T,QI('ATM',T)*OPC+sum(U,sum(M,sum(M1,xQI(U,M,M1,T)*tOpCost(U,M,M1))))
#                                 +sum(U,sum(M1,xyQI(U,M1,T)*OpCost(U,M1))))
#                                 +sum(T,ap*(sum(O,OINV(O,T))+sum(OC,OCINV(OC,T))))
#                                 +sum(L,sum(O,bp*(R(L,O)-sum(T,Otankout(O,L,T)))));
numU = 9
numM = 4
numS = 4
numO = 8
numOC = 8
numP = 4
hours = 1
numL = 2
MAXINPUT = 300
Mlist = range(numM)
Ulist = range(numU)
Slist = range(numS)
Plist = range(numP)
TTlist = [3,2,1]
OClist = range(numOC)
Olist = range(numO)
Llist = range(numL)
TLlist = range(2) # TL1 and TL2
OPC = 388.2   # crude oil cost per ton
apoc = 50.0    # inv cost
apo = 75.0    # inv cost
bp = 30000.  # penalty for stockout of order l per ton
invC_multi_flow = 4  # invOC uplimit , its value is invC_multi_flow times of flow*hours
invO_multi_L = 6   # invO uplimit , its value is invO_multi_flow times of flow*hours
MTBE120or110 = 120
FOCOmax = 100
FOout_MAX = 100
# PRO = [94.,99.,94.,98.,89.,0.,0.,0.,
#        0.,0.,0.,0.,0.,48.,49.,59.,
#        0.0001,0.0002,0.0004,0.02,0.03,0.001,0.001,0.038,
#        0.,0.,0.,0.,0.,1.68,1.1,1.6] #P /RON,CN,S,CPF/  # PRO(P,OC)
PRO = [#96.,98.,99.,93.,89.,0.,0.,0.,
       83.,100.,117.,93.,90.,0.,0.,0.,
       #0.,0.,0.,0.,0.,48.,49.,59.,
       0.,0.,0.,0.,0.,47.,55.,48.,
       #0.0001,0.0002,0.0004,0.02,0.03,0.038,0.002,0.001,
       0.0001,0.0002,0.04,0.01,0.02,0.001,0.001,0.038,
       #0.0001,0.0001,0.05,0.01,0.01,0.038,0.002,0.001,
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

numT = 8
Tlist = range(numT)
R = [[10.,40.,20.,10.,55.,100.,60.,70.],
     [20.,30.,10.,10.,70.,80.,70.,90.]] # numL*numO
RT = [[1.,6.],[3.,8.]] # numL*2
# R= np.array(R)
# RT= np.array(RT)
QIinputL = [200.,300.,0.,300.,0.,300.,0.,300.,0.,300.,0.,300.,0.,300.,0.,300.,0.,300.]  # numU*2
#OCtankL = [0.,1000.,0.,1000.,0.,1000.,0.,1000.,0.,1000.,0.,1000.,0.,1000.,0.,1000.] #numOC*2
#OtankL = [0.,1000.,0.,1000.,0.,1000.,0.,1000.,0.,1000.,0.,1000.,0.,1000.,0.,1000.] #numO*2
# Parameter tYield
Yield = [0]*numU*numM*numS
# Yieldlist = [7.008,15.349,8.109,64.534,4.576,19.403,9.267,61.754,
#              11.286,37.532,12.580,35.652,
#              22.216, 5.02, 45.664,  23.104, 5.01, 42.583,  23.418, 4.15, 42.261,  26.683, 4.13, 39.580,
#              93.2,90,98.1,94.1,
#              86.2,79.,97.,88.,
#              99.4,99.4,
#              4.,93.,9.,89.,
#              10.,90.,
#              120]
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
        for S in Slist:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)
for U in [Ulist[1]]: # VCD
    for M in Mlist[0:2]:
        for S in Slist[0:2]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)
for U in [Ulist[2]]: # FCCU
    for M in Mlist[0:4]:
        for S in Slist[0:3]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)
for U in [Ulist[3]]: # ETH
    for M in Mlist[0:4]:
        for S in [Slist[0]]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)
for U in [Ulist[4]]:  # HDS
    for M in Mlist[0:4]:
        for S in [Slist[0]]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)
for U in [Ulist[5]]:  # HTU1
    for M in Mlist[0:2]:
        for S in [Slist[0]]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)
for U in [Ulist[6]]:  # HTU2
    for M in Mlist[0:2]:
        for S in Slist[0:2]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)
for U in [Ulist[7]]:  # RF
    for M in [Mlist[0]]:
        for S in Slist[0:2]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)
for U in [Ulist[8]]:  # MTBE
    for M in [Mlist[0]]:
        for S in [Slist[0]]:
            Yield[U*numM*numS+M*numS+S] = Yieldlist.pop(0)

tYield = [0]*numU*numM*numM*numS
for U in [Ulist[0]]: # ATM
    for M in Mlist[0:2]:
        for M1 in Mlist[0:2]:
            if M1 != M:
                for S in Slist:
                    tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S] = 0.5*(Yield[U*numM*numS+M*numS+S]+Yield[U*numM*numS+M1*numS+S])
for U in [Ulist[1]]: # VCD
    for M in Mlist[0:2]:
        for M1 in Mlist[0:2]:
            if M1 != M:
                for S in Slist[0:2]:
                    tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S] = 0.5*(Yield[U*numM*numS+M*numS+S]+Yield[U*numM*numS+M1*numS+S])
for U in [Ulist[2]]: # FCCU
    for M in Mlist[0:4]:
        for M1 in Mlist[0:4]:
            if M1 != M:
                for S in Slist[0:3]:
                    tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S] = 0.5*(Yield[U*numM*numS+M*numS+S]+Yield[U*numM*numS+M1*numS+S])
for U in [Ulist[3]]: # ETH
    for M in Mlist[0:4]:
        for M1 in Mlist[0:4]:
            if M1 != M:
                for S in [Slist[0]]:
                    tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S] = 0.5*(Yield[U*numM*numS+M*numS+S]+Yield[U*numM*numS+M1*numS+S])
for U in [Ulist[4]]:  # HDS
    for M in Mlist[0:4]:
        for M1 in Mlist[0:4]:
            if M1 != M:
                for S in [Slist[0]]:
                    tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S] = 0.5*(Yield[U*numM*numS+M*numS+S]+Yield[U*numM*numS+M1*numS+S])
for U in [Ulist[5]]:  # HTU1
    for M in Mlist[0:2]:
        for M1 in Mlist[0:2]:
            if M1 != M:
                for S in [Slist[0]]:
                    tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S] = 0.5*(Yield[U*numM*numS+M*numS+S]+Yield[U*numM*numS+M1*numS+S])
for U in [Ulist[6]]:  # HTU2
    for M in Mlist[0:2]:
        for M1 in Mlist[0:2]:
            if M1 != M:
                for S in Slist[0:2]:
                    tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S] = 0.5*(Yield[U*numM*numS+M*numS+S]+Yield[U*numM*numS+M1*numS+S])


# OpCost = [11.,11.5,0.,0.,
#           11.,11.5,0.,0.,
#           58.,57.,56.5,56.,
#           49.56,47.11,46.7,44.66,
#           28.98,27.18,26.73,24.48,
#           9.,8., 0., 0.,
#           11.,10., 0., 0.,
#           83.,0.,0.,0.,
#           13.84,0.,0.,0.]   # numU*numM
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

def buildmodel(prob,numT, Tlist, numL, Llist, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode ):
    prob.objective.set_sense(prob.objective.sense.minimize)
    # list number is address, inlet is value. Orgenize the list number to get the value.  #,QI_atm,QI_eth,QI_htu1
    # the yield value
    # ====================================== Variable x
    obj = [0]*numU*numM*numM*numT
    ct  = ['B']*numU*numM*numM*numT
    xcount = numU*numM*numM*numT
    x_c = 0
    namey = []
    charlist = [str(i) for i in range(0, xcount )]
    for i in charlist:
        namey.append('x' + i)
    prob.variables.add(obj=obj, types=ct, names = namey)
    # ====================================== Variable y
    obj = [0]*numU*numM*numT
    ct  = ['B']*numU*numM*numT
    ycount = numU*numM*numT
    y_c = x_c + xcount
    namey = []
    charlist = [str(i) for i in range(0,ycount)]
    for i in charlist:
        namey.append('y'+i)
    prob.variables.add(obj=obj, types=ct, names = namey)
    # ====================================== Variable xQI
    obj = [0]*numU*numM*numM*numT
    ct  = ['C']*numU*numM*numM*numT
    xQIcount = numU*numM*numM*numT
    xQI_c = y_c + ycount
    namey = []
    charlist = [str(i) for i in range(1, xQIcount + 1)]
    for i in charlist:
        namey.append('xQI' + i)
    prob.variables.add(obj=obj, types=ct, names = namey)
    # =======================================Variable xyQI
    obj = [0]*numU*numM*numT
    ct  = ['C']*numU*numM*numT
    xyQIcount = numU*numM*numT
    xyQI_c = xQI_c + xQIcount
    namey = []
    charlist = [str(i) for i in range(1, xyQIcount + 1)]
    for i in charlist:
        namey.append('xyQI' + i)
    prob.variables.add(obj=obj, types=ct, names = namey)
    # ======================================Variable QO
    obj = [0]*numU*numS*numT
    ct  = ['C']*numU*numS*numT
    QOcount = numU*numS*numT
    QO_c = xyQI_c + xyQIcount
    namey = []
    charlist = [str(i) for i in range(1, QOcount + 1)]
    for i in charlist:
        namey.append('QO' + i)
    prob.variables.add(obj=obj, types=ct, names = namey)
    # ===================================== Variable QI
    obj = [0] * numU * numT
    ct = ['C'] * numU * numT
    QIcount = numU * numT
    QI_c = QO_c + QOcount
    namey = []
    charlist = [str(i) for i in range(1, QIcount + 1)]
    for i in charlist:
        namey.append('QI' + i)
    prob.variables.add(obj=obj, types=ct, names=namey)
    # ===================================== Variable OC
    # this is another variable that doesnot appear in gams, in gams that use fenliu.
    # Here numOC can be replace by 2, because fenliu variable only 2, it has no relationship with the reality OC num.
    obj = [0]*numOC*numT
    ct  = ['C']*numOC*numT
    OCcount = numOC*numT
    OC_c = QI_c + QIcount
    namey = []
    charlist = [str(i) for i in range(1, OCcount + 1)]
    for i in charlist:
        namey.append('OC' + i)
    prob.variables.add(obj=obj, types=ct, names = namey)
    # ================= Variable OCINV
    obj = [0]*numOC*numT
    ct  = ['C']*numOC*numT
    OCINVcount = numOC*numT
    OCINV_c = OC_c + OCcount
    namey = []
    charlist = [str(i) for i in range(1, OCINVcount + 1)]
    for i in charlist:
        namey.append('OCINV' + i)
    prob.variables.add(obj=obj, types=ct, names = namey)
    # ===================Variable OCtankout
    obj = [0]*numOC*numT
    ct  = ['C']*numOC*numT
    OCtankoutcount = numOC*numT
    OCtankout_c = OCINV_c + OCINVcount
    namey = []
    charlist = [str(i) for i in range(1, OCtankoutcount + 1)]
    for i in charlist:
        namey.append('OCtankout' + i)
    prob.variables.add(obj=obj, types=ct, names = namey)
    #===========================Variable Q
    obj = [0]*numOC*numO*numT
    ct  = ['C']*numOC*numO*numT
    Qcount = numOC*numO*numT
    Q_c = OCtankout_c + OCtankoutcount
    namey = []
    charlist = [str(i) for i in range(1, Qcount + 1)]
    for i in charlist:
        namey.append('Q' + i)
    prob.variables.add(obj=obj, types=ct, names = namey)
    #===========================Variable OINV(O,T)
    obj = [0]*numO*numT
    ct  = ['C']*numO*numT
    OINVcount = numO*numT
    OINV_c = Q_c + Qcount
    namey = []
    charlist = [str(i) for i in range(1, OINVcount + 1)]
    for i in charlist:
        namey.append('OINV' + i)
    prob.variables.add(obj=obj, types=ct, names = namey)
    #===========================Variable Otankout(O,L,T)
    obj = [0]*numO*numL*numT
    ct  = ['C']*numO*numL*numT
    Otankoutcount = numO*numL*numT
    Otankout_c = OINV_c + OINVcount
    namey = []
    charlist = [str(i) for i in range(1, Otankoutcount + 1)]
    for i in charlist:
        namey.append('Otankout' + i)
    prob.variables.add(obj=obj, types=ct, names = namey)
    # ============================= Variable xQI1
    obj = [0]*numU*numM*numM*numT
    ct  = ['C']*numU*numM*numM*numT
    xQI1count = numU*numM*numM*numT
    xQI1_c = Otankout_c + Otankoutcount
    namey = []
    charlist = [str(i) for i in range(1, xQI1count + 1)]
    for i in charlist:
        namey.append('xQI1' + i)
    prob.variables.add(obj=obj, types=ct, names = namey)
    # ================================Variable xy(U,M,T)
    obj = [0]*numU*numM*numT
    ct  = ['C']*numU*numM*numT
    xycount = numU*numM*numT
    xy_c = xQI1_c + xQI1count
    namey = []
    charlist = [str(i) for i in range(1, xycount + 1)]
    for i in charlist:
        namey.append('xy' + i)
    prob.variables.add(obj=obj, types=ct, names = namey)
    # ================================Variable xyQI1_c(U,M,T)
    obj = [0]*numU*numM*numT
    ct  = ['C']*numU*numM*numT
    xyQI1count = numU*numM*numT
    xyQI1_c = xy_c + xycount
    namey = []
    charlist = [str(i) for i in range(1, xyQI1count + 1)]
    for i in charlist:
        namey.append('xyQI1' + i)
    prob.variables.add(obj=obj, types=ct, names = namey)
    # ================================Variable consta(1)
    obj = [0]*1
    ct  = ['C']*1
    constacount = 1
    consta_c = xyQI1_c + xyQI1count
    namey = []
    charlist = [str(i) for i in range(1, constacount + 1)]
    for i in charlist:
        namey.append('consta' + i)
    prob.variables.add(obj=obj, types=ct, names = namey)
    # ======================================unit mode sum y=1, unit no-mode y=0 ==========================
    names = "Constant_V"
    prob.linear_constraints.add(lin_expr=[[[consta_c], [1.0]]],senses="E", rhs=[1.0], names=[names])
    prob.objective.set_linear(consta_c, bp*sum(sum(DV1[:numL]))+sum(OCtank_ini)*0.5*apoc+sum(Otank_ini)*0.5*apo)
    i = 0
    for U in range(numU):
        if U==Ulist[0] or U==Ulist[1]:
            for T in Tlist:
                i += 1
                names = "Asumy1_"+str(i)
                prob.linear_constraints.add(lin_expr=[[[U*numM*numT+Mlist[0]*numT+T+y_c,
                                                        U*numM*numT+Mlist[1]*numT+T+y_c],[1.0, 1.0]]],
                                            senses="E", rhs=[1.0], names=[names])
        i = 0
        if U==Ulist[2] or U==Ulist[3] or U==Ulist[4]:
            for T in range(numT):
                i += 1
                names = "Fsumy1_" + str(i)
                prob.linear_constraints.add(lin_expr=[[[U*numM*numT+Mlist[0]*numT+T+y_c,
                                                        U*numM*numT+Mlist[1]*numT+T+y_c,
                                                        U*numM*numT+Mlist[2]*numT+T+y_c,
                                                        U*numM*numT+Mlist[3]*numT+T+y_c],[1.0, 1.0, 1.0, 1.0]]],
                                            senses="E", rhs=[1.0], names=[names])
        i = 0
        if U==Ulist[5] or U==Ulist[6]:
            for T in range(numT):
                i += 1
                names = "Hsumy1_" + str(i)
                prob.linear_constraints.add(lin_expr=[[[U*numM*numT+Mlist[0]*numT+T+y_c,
                                                        U*numM*numT+Mlist[1]*numT+T+y_c],[1.0, 1.0]]],
                                            senses="E", rhs=[1.0], names=[names])
        i = 0
        if U==Ulist[7] or U==Ulist[8]:
            for T in range(numT):
                i += 1
                names = "Rsumy1_" + str(i)
                prob.linear_constraints.add(lin_expr=[[[U*numM*numT+Mlist[0]*numT+T+y_c],[1.0]]],
                                            senses="E", rhs=[1.0], names=[names])
    # =================================== x<=y,unit no-translate state x=0.=======================
    i = 0
    for U in Ulist[0:2]:
        for M in Mlist[0:2]:
            for M1 in Mlist[0:2]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "Ax<=y_" + str(i)
                        if T != Tlist[0] and T != Tlist[-1]:
                            # x <= y when T is not the first and last period
                            prob.linear_constraints.add(
                                lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c,
                                            U * numM * numT + M1 * numT + T + y_c],
                                           [1.0, -1.0]]],
                                senses="L", rhs=[0], names=[names])
                        else:
                            # T =first and last period the x is 0
                            prob.linear_constraints.add(
                                lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c],
                                           [1.0]]],
                                senses="E", rhs=[0], names=[names])
                        if T > 0:
                            i += 1
                            names = "Ax+1<=y_" + str(i)
                            # x <= y when T is not the first and last period
                            prob.linear_constraints.add(
                                    lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T-1 + x_c,
                                                U * numM * numT + M1 * numT + T + y_c],
                                               [1.0, -1.0]]],
                                    senses="L", rhs=[0], names=[names])
    i = 0
    for U in Ulist[2:5]:
        for M in Mlist[0:4]:
            for M1 in Mlist[0:4]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "Fx<=y_" + str(i)
                        if T != Tlist[0] and T != Tlist[-1]:
                            # x <= y when T is not the first and last period
                            prob.linear_constraints.add(
                                lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c,
                                            U * numM * numT + M1 * numT + T + y_c],
                                           [1.0, -1.0]]],
                                senses="L", rhs=[0], names=[names])
                        else:
                            # T =first and last period the x is 0
                            prob.linear_constraints.add(
                                lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c],
                                           [1.0]]],
                                senses="E", rhs=[0], names=[names])
                        if T > 0:
                            i += 1
                            names = "Ax+1<=y_" + str(i)
                            # x <= y when T is not the first and last period
                            prob.linear_constraints.add(
                                    lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T-1 + x_c,
                                                U * numM * numT + M1 * numT + T + y_c],
                                               [1.0, -1.0]]],
                                    senses="L", rhs=[0], names=[names])
    i = 0
    for U in Ulist[5:7]:
        for M in Mlist[0:2]:
            for M1 in Mlist[0:2]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "Hx<=y_" + str(i)
                        if T != Tlist[0] and T != Tlist[-1]:
                            # x <= y when T is not the first and last period
                            prob.linear_constraints.add(
                                lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c,
                                            U * numM * numT + M1 * numT + T + y_c],
                                           [1.0, -1.0]]],
                                senses="L", rhs=[0], names=[names])
                        else:
                            # T =first and last period the x is 0
                            prob.linear_constraints.add(
                                lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c],
                                           [1.0]]],
                                senses="E", rhs=[0], names=[names])
                        if T > 0:
                            i += 1
                            names = "Ax+1<=y_" + str(i)
                            # x <= y when T is not the first and last period
                            prob.linear_constraints.add(
                                    lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T-1 + x_c,
                                                U * numM * numT + M1 * numT + T + y_c],
                                               [1.0, -1.0]]],
                                    senses="L", rhs=[0], names=[names])
    # ======================================== x <= y(T-TT) =========================================
    # TransVconst21(MATM,MATM1,T)$(ord(MATM)<>ord(MATM1)and ord(T)>TT('ATM',MATM,MATM1))..x('ATM',MATM,MATM1,T) =l=
    # y('ATM',MATM,T-TT('ATM',MATM,MATM1))  PS: ord() begin from one.
    # TransVconst31(MATM,MATM1,T)$(ord(MATM)<>ord(MATM1)and ord(T)<=TT('ATM',MATM,MATM1))..x('ATM',MATM,MATM1,T) =l=
    # y('ATM',MATM,'t1')
    i = 0
    for U in Ulist[0:2]:
        for M in Mlist[0:2]:
            for M1 in Mlist[0:2]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "Ax<=y(-TT)_" + str(i)
                        if T >= TTlist[0] and T != Tlist[-1]:
                            # x <= y(T-TT) when T is greater than TT. T from value 0.
                            prob.linear_constraints.add(
                                lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c,
                                            U * numM * numT + M * numT + T - TTlist[0] + y_c],
                                           [1.0, -1.0]]],
                                senses="L", rhs=[0], names=[names])
                        elif T < TTlist[0] and T > Tlist[0]:
                            # x <= y(1) when T is smaller than TT
                            prob.linear_constraints.add(
                                lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c,
                                            U * numM * numT + M * numT + 0 + y_c],
                                           [1.0, -1.0]]],
                                senses="L", rhs=[0], names=[names])
    i = 0
    for U in [Ulist[2]]:
        for M in Mlist[0:4]:
            for M1 in Mlist[0:4]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "Fx<=y(-TT)_" + str(i)
                        if T >= TTlist[1] and T != Tlist[-1]:
                            # x <= y(T-TT) when T is greater than TT. T from value 0.
                            prob.linear_constraints.add(
                                lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c,
                                            U * numM * numT + M * numT + T - TTlist[1] + y_c],
                                           [1.0, -1.0]]],
                                senses="L", rhs=[0], names=[names])
                        elif T < TTlist[1] and T > Tlist[0]:
                            # x <= y(1) when T is smaller than TT
                            prob.linear_constraints.add(
                                lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c,
                                            U * numM * numT + M * numT + 0 + y_c],
                                           [1.0, -1.0]]],
                                senses="L", rhs=[0], names=[names])
    i = 0
    for U in Ulist[3:5]:
        for M in Mlist[0:4]:
            for M1 in Mlist[0:4]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "HEx<=y(-TT)_" + str(i)
                        if T >= TTlist[2] and T != Tlist[-1]:
                            # x <= y(T-TT) when T is greater than TT. T from value 0.
                            prob.linear_constraints.add(
                                lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c,
                                            U * numM * numT + M * numT + T - TTlist[2] + y_c],
                                           [1.0, -1.0]]],
                                senses="L", rhs=[0], names=[names])
                        elif T < TTlist[2] and T > Tlist[0]:
                            # x <= y(1) when T is smaller than TT
                            prob.linear_constraints.add(
                                lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c,
                                            U * numM * numT + M * numT + 0 + y_c],
                                           [1.0, -1.0]]],
                                senses="L", rhs=[0], names=[names])
    i = 0
    for U in Ulist[5:7]:
        for M in Mlist[0:2]:
            for M1 in Mlist[0:2]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "Hx<=y(-TT)_" + str(i)
                        if T >= TTlist[2] and T != Tlist[-1]:
                            # x <= y(T-TT) when T is greater than TT. T from value 0.
                            prob.linear_constraints.add(
                                lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c,
                                            U * numM * numT + M * numT + T - TTlist[2] + y_c],
                                           [1.0, -1.0]]],
                                senses="L", rhs=[0], names=[names])
                        elif T < TTlist[2] and T > Tlist[0]:
                            # x <= y(1) when T is smaller than TT
                            prob.linear_constraints.add(
                                lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c,
                                            U * numM * numT + M * numT + 0 + y_c],
                                           [1.0, -1.0]]],
                                senses="L", rhs=[0], names=[names])
    # ======================================== minimum stay constraints ==============================
    # TransVconstMinS1(MATM,MATM1,T)$(ord(T)>1 and ord(MATM)<>ord(MATM1))..(TT('ATM',MATM,MATM1)+1)*
    # (y('ATM',MATM,T-1)+y('ATM',MATM1,T)-1) =l=
    # sum(T1$(ord(T1)>=ord(T)and ord(T1)-ord(T)< TT('ATM',MATM,MATM1)),x('ATM',MATM,MATM1,T1))
    # +y('ATM',MATM1,T+TT('ATM',MATM,MATM1))
    i = 0
    for U in Ulist[0:2]:
        for M in Mlist[0:2]:
            for M1 in Mlist[0:2]:
                if M1 != M:
                    for T in Tlist:
                        ind = []
                        val = []
                        i += 1
                        names = "AminS_" + str(i)
                        if T > Tlist[0] and T != Tlist[-1]:
                            ind.append(U * numM * numT + M * numT + T - 1 + y_c)
                            val.append(TTlist[0] + 0)
                            ind.append(U * numM * numT + M1 * numT + T + y_c)
                            val.append(TTlist[0] + 0)
                            for T1 in Tlist:
                                if T1 >= T and T1 - T < TTlist[0]:
                                    ind.append(U * numM * numM * numT + M * numM * numT + M1 * numT + T1 + x_c)
                                    val.append(-1.0)

                            prob.linear_constraints.add(lin_expr=[[ind, val]],
                                                        senses="L", rhs=[TTlist[0] + 0], names=[names])
                        elif T == Tlist[-1]:
                            prob.linear_constraints.add(lin_expr=[[[U * numM * numT + M1 * numT + T + y_c,
                                                                    U * numM * numT + M * numT + T - 1 + y_c],
                                                                   [1.0,1.0]]],
                                                        senses="L", rhs=[1], names=[names])
    i = 0
    for U in [Ulist[2]]:
        for M in Mlist[0:4]:
            for M1 in Mlist[0:4]:
                if M1 != M:
                    for T in Tlist:
                        ind = []
                        val = []
                        i += 1
                        names = "FminS_" + str(i)
                        if T > Tlist[0] and T != Tlist[-1]:
                            ind.append(U * numM * numT + M * numT + T - 1 + y_c)
                            val.append(TTlist[1] + 0)
                            ind.append(U * numM * numT + M1 * numT + T + y_c)
                            val.append(TTlist[1] + 0)
                            for T1 in Tlist:
                                if T1 >= T and T1 - T < TTlist[1]:
                                    ind.append(U * numM * numM * numT + M * numM * numT + M1 * numT + T1 + x_c)
                                    val.append(-1.0)

                            prob.linear_constraints.add(lin_expr=[[ind, val]],
                                                        senses="L", rhs=[TTlist[1] + 0], names=[names])
                        elif T == Tlist[-1]:
                            prob.linear_constraints.add(lin_expr=[[[U * numM * numT + M1 * numT + T + y_c,
                                                                    U * numM * numT + M * numT + T - 1 + y_c],
                                                                   [1.0,1.0]]],
                                                        senses="L", rhs=[1], names=[names])
    i = 0
    for U in Ulist[3:5]:
        for M in Mlist[0:4]:
            for M1 in Mlist[0:4]:
                if M1 != M:
                    for T in Tlist:
                        ind = []
                        val = []
                        i += 1
                        names = "HEminS_" + str(i)
                        if T > Tlist[0] and T != Tlist[-1]:
                            ind.append(U * numM * numT + M * numT + T - 1 + y_c)
                            val.append(TTlist[2] + 0)
                            ind.append(U * numM * numT + M1 * numT + T + y_c)
                            val.append(TTlist[2] + 0)
                            for T1 in Tlist:
                                if T1 >= T and T1 - T < TTlist[2]:
                                    ind.append(U * numM * numM * numT + M * numM * numT + M1 * numT + T1 + x_c)
                                    val.append(-1.0)

                            prob.linear_constraints.add(lin_expr=[[ind, val]],
                                                        senses="L", rhs=[TTlist[2] + 0], names=[names])
                        elif T == Tlist[-1]:
                            prob.linear_constraints.add(lin_expr=[[[U * numM * numT + M1 * numT + T + y_c,
                                                                    U * numM * numT + M * numT + T - 1 + y_c],
                                                                   [1.0,1.0]]],
                                                        senses="L", rhs=[1], names=[names])
    i = 0
    for U in Ulist[5:7]:
        for M in Mlist[0:2]:
            for M1 in Mlist[0:2]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "HminS_" + str(i)
                        ind = []
                        val = []
                        if T > Tlist[0] and T != Tlist[-1]:
                            ind.append(U * numM * numT + M * numT + T - 1 + y_c)
                            val.append(TTlist[2] + 0)
                            ind.append(U * numM * numT + M1 * numT + T + y_c)
                            val.append(TTlist[2] + 0)
                            for T1 in Tlist:
                                if T1 >= T and T1 - T < TTlist[2]:
                                    ind.append(U * numM * numM * numT + M * numM * numT + M1 * numT + T1 + x_c)
                                    val.append(-1.0)

                            prob.linear_constraints.add(lin_expr=[[ind, val]],
                                                        senses="L", rhs=[TTlist[2] + 0], names=[names])
                        elif T == Tlist[-1]:
                            prob.linear_constraints.add(lin_expr=[[[U * numM * numT + M1 * numT + T + y_c,
                                                                    U * numM * numT + M * numT + T - 1 + y_c],
                                                                   [1.0,1.0]]],
                                                        senses="L", rhs=[1], names=[names])
    # =========================================== yFCCU=yHDS=yETH ==============================
    i = 0
    for T in Tlist:
        for M in Mlist[0:4]:
            i += 1
            names = "SHXIA1_" + str(i)
            prob.linear_constraints.add(lin_expr=[[[Ulist[2]*numM*numT+M*numT+T+y_c,
                                                    Ulist[3]*numM*numT+M*numT+T+y_c],
                                                   [1.0,-1.0]]],
                                        senses="E", rhs=[0.0],names=[names])
    i = 0
    for T in Tlist:
        for M in Mlist[0:4]:
            i += 1
            names = "SHXIA2_" + str(i)
            prob.linear_constraints.add(lin_expr=[[[Ulist[3]*numM*numT+M*numT+T+y_c,
                                                    Ulist[4]*numM*numT+M*numT+T+y_c],
                                                   [1.0,-1.0]]],
                                        senses="E", rhs=[0.0],names=[names])
    #============================================ Unit output ================================
    # Production Contraints
    # ATM
    i = 0
    for U in [Ulist[0]]:
        for S in Slist:
            for T in Tlist:
                i += 1
                names = "AProC_" + str(i)
                ind = []
                val = []
                ind.append(U * numS * numT + S * numT + T + QO_c)
                val.append(-1)
                for M in Mlist[0:2]:
                    ind.append(U * numM * numT + M * numT + T + xyQI_c)
                    val.append(0.01 * Yield[U * numM * numS + M * numS + S])
                    for M1 in Mlist[0:2]:
                        if M1 != M:
                            ind.append(U*numM*numM*numT+M*numM*numT+M1*numT+T+xQI_c)
                            val.append(0.01*tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S])
                prob.linear_constraints.add(lin_expr=[[ind, val]],
                                            senses="E", rhs=[0], names=[names])
    # CDU
    i = 0
    for U in [Ulist[1]]:
        for S in Slist[0:2]:
            for T in Tlist:
                i += 1
                names = "CProC_" + str(i)
                ind = []
                val = []
                ind.append(U * numS * numT + S * numT + T + QO_c)
                val.append(-1)
                for M in Mlist[0:2]:
                    ind.append(U * numM * numT + M * numT + T + xyQI_c)
                    val.append(0.01 * Yield[U * numM * numS + M * numS + S])
                    for M1 in Mlist[0:2]:
                        if M1 != M:
                            ind.append(U*numM*numM*numT+M*numM*numT+M1*numT+T+xQI_c)
                            val.append(0.01*tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S])
                prob.linear_constraints.add(lin_expr=[[ind, val]],
                                            senses="E", rhs=[0], names=[names])
    # FCCU
    i = 0
    for U in [Ulist[2]]:
        for S in Slist[0:3]:
            for T in Tlist:
                i += 1
                names = "FProC_" + str(i)
                ind = []
                val = []
                ind.append(U * numS * numT + S * numT + T + QO_c)
                val.append(-1)
                for M in Mlist[0:4]:
                    ind.append(U * numM * numT + M * numT + T + xyQI_c)
                    val.append(0.01 * Yield[U * numM * numS + M * numS + S])
                    for M1 in Mlist[0:4]:
                        if M1 != M:
                            ind.append(U*numM*numM*numT+M*numM*numT+M1*numT+T+xQI_c)
                            val.append(0.01*tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S])
                prob.linear_constraints.add(lin_expr=[[ind, val]],
                                            senses="E", rhs=[0], names=[names])
    # ETH/HDS
    i = 0
    for U in Ulist[3:5]:
        for S in [Slist[0]]:
            for T in Tlist:
                i += 1
                names = "EHProC_" + str(i)
                ind = []
                val = []
                ind.append(U * numS * numT + S * numT + T + QO_c)
                val.append(-1)
                for M in Mlist[0:4]:
                    ind.append(U * numM * numT + M * numT + T + xyQI_c)
                    val.append(0.01 * Yield[U * numM * numS + M * numS + S])
                    for M1 in Mlist[0:4]:
                        if M1 != M:
                            ind.append(U*numM*numM*numT+M*numM*numT+M1*numT+T+xQI_c)
                            val.append(0.01*tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S])
                prob.linear_constraints.add(lin_expr=[[ind, val]],
                                            senses="E", rhs=[0], names=[names])
    # HTU1 unitProBla6(S,T)..QO('HTU1',S,T) =e= sum(MHTU1,sum(MHTU11,xQI('HTU1',MHTU1,MHTU11,T)*0.01*tYield('HTU1',
    # S,MHTU1,MHTU11)))+sum(MHTU11,xyQI('HTU1',MHTU11,T)*0.01*Yield('HTU1',S,MHTU11))
    i = 0
    for U in [Ulist[5]]:
        for S in [Slist[0]]:
            for T in Tlist:
                i += 1
                names = "HTU1ProC_" + str(i)
                ind = []
                val = []
                ind.append(U * numS * numT + S * numT + T + QO_c)
                val.append(-1)
                for M in Mlist[0:2]:
                    ind.append(U * numM * numT + M * numT + T + xyQI_c)
                    val.append(0.01 * Yield[U * numM * numS + M * numS + S])
                    for M1 in Mlist[0:2]:
                        if M1 != M:
                            ind.append(U*numM*numM*numT+M*numM*numT+M1*numT+T+xQI_c)
                            val.append(0.01*tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S])
                prob.linear_constraints.add(lin_expr=[[ind, val]],
                                            senses="E", rhs=[0], names=[names])
    # HTU2 unitProBla6(S,T)..QO('HTU1',S,T) =e= sum(MHTU1,sum(MHTU11,xQI('HTU1',MHTU1,MHTU11,T)*0.01*tYield('HTU1',
    # S,MHTU1,MHTU11)))+sum(MHTU11,xyQI('HTU1',MHTU11,T)*0.01*Yield('HTU1',S,MHTU11))
    i = 0
    for U in [Ulist[6]]:
        for S in Slist[0:2]:
            for T in Tlist:
                i += 1
                names = "HTU2ProC_" + str(i)
                ind = []
                val = []
                ind.append(U * numS * numT + S * numT + T + QO_c)
                val.append(-1)
                for M in Mlist[0:2]:
                    ind.append(U * numM * numT + M * numT + T + xyQI_c)
                    val.append(0.01 * Yield[U * numM * numS + M * numS + S])
                    for M1 in Mlist[0:2]:
                        if M1 != M:
                            ind.append(U*numM*numM*numT+M*numM*numT+M1*numT+T+xQI_c)
                            val.append(0.01*tYield[U*numM*numM*numS+M*numM*numS+M1*numS+S])
                prob.linear_constraints.add(lin_expr=[[ind, val]],
                                            senses="E", rhs=[0], names=[names])
    # RF  unitProBla(U,S,T)..QO(U,S,T) =e= QI(U,T)*Y(U,S,M1) --For this expression to define variable QI ahead.
    i = 0
    for U in [Ulist[7]]:
        for S in Slist[0:2]:
            for T in Tlist:
                i += 1
                names = "RProC_" + str(i)
                prob.linear_constraints.add(lin_expr=[[[U * numS * numT + S * numT + T + QO_c,
                                                        U * numT + T + QI_c],
                                                       [1.0,-0.01*Yield[U*numM*numS+Mlist[0]*numS+S]]]],
                                            senses="E", rhs=[0], names=[names])
    # MTBE  unitProBla(U,S,T)..QO(U,S,T) =e= QI(U,T)*Yield(U,S,M1)
    i = 0
    for U in [Ulist[8]]:
        for S in [Slist[0]]:
            for T in Tlist:
                i += 1
                names = "MProC_" + str(i)
                prob.linear_constraints.add(lin_expr=[[[U * numS * numT + S * numT + T + QO_c,
                                                        U * numT + T + QI_c],
                                                       [1.0,-0.01*Yield[U*numM*numS+Mlist[0]*numS+S]]]],
                                            senses="E", rhs=[0], names=[names])
    #============================================ Unit input =====================================
    # VCD = ATM_S4
    i = 0
    for T in Tlist:
        i += 1
        names = "AinP_" + str(i)
        prob.linear_constraints.add(lin_expr=[[[Ulist[1]*numT+T+QI_c,
                                                Ulist[0]*numS*numT+Slist[3]*numT+T+QO_c],
                                               [1.0,-1.0]]],
                                    senses="E", rhs=[0], names=[names])
    # FCCU = VCD_S2
    i = 0
    for T in Tlist:
        i += 1
        names = "FinP_" + str(i)
        prob.linear_constraints.add(lin_expr=[[[Ulist[2]*numT+T+QI_c,
                                                Ulist[1]*numS*numT+Slist[1]*numT+T+QO_c],
                                               [1.0,-1.0]]],
                                    senses="E", rhs=[0], names=[names])
    # ETH  =  HDS_S1 -HDS_gasoline
        # U /ATM 0,VCD 1,FCCU 2,ETH 3,HDS 4,HTU1 5,HTU2 6,RF 7,MTBE 8/
        # OC /C5 0,Reformate 1,MTBE 2,HDS 3,Etherified 4,diesel1 5,diesel2 6,Lightdi 7/
    i = 0
    for T in Tlist:
        i += 1
        names = "EinP_" + str(i)
        prob.linear_constraints.add(lin_expr=[[[Ulist[3]*numT+T+QI_c,
                                                Ulist[4]*numS*numT+Slist[0]*numT+T+QO_c,
                                                OClist[3]*numT+T+OC_c],
                                               [1.0,-1.0,1.0]]],
                                    senses="E", rhs=[0], names=[names])
    # HDS = FCCU_S3
    i = 0
    for T in Tlist:
        i += 1
        names = "HinP_" + str(i)
        prob.linear_constraints.add(lin_expr=[[[Ulist[4]*numT+T+QI_c,
                                                Ulist[2]*numS*numT+Slist[2]*numT+T+QO_c],
                                               [1.0,-1.0]]],
                                    senses="E", rhs=[0], names=[names])
    # HTU1 = ATM_S2 - Ligthedi
    i = 0
    for T in Tlist:
        i += 1
        names = "H1inP_" + str(i)
        prob.linear_constraints.add(lin_expr=[[[Ulist[5]*numT+T+QI_c,
                                                Ulist[0]*numS*numT+Slist[1]*numT+T+QO_c,
                                                OClist[7]*numT+T+OC_c],
                                               [1.0,-1.0,1.0]]],
                                    senses="E", rhs=[0], names=[names])
    # HTU2 = ATM_S3 + VCD_S1 + FCCU_S1
    i = 0
    for T in Tlist:
        i += 1
        names = "H2inP_" + str(i)
        prob.linear_constraints.add(lin_expr=[[[Ulist[6]*numT+T+QI_c,
                                                Ulist[0]*numS*numT+Slist[2]*numT+T+QO_c,
                                                Ulist[1]*numS*numT+Slist[0]*numT+T+QO_c,
                                                Ulist[2]*numS*numT+Slist[0]*numT+T+QO_c],
                                               [-1.0,1.0,1.0,1.0]]],
                                    senses="E", rhs=[0], names=[names])
    # RF = ATM_S1 + HTU2_S1
    i = 0
    for T in Tlist:
        i += 1
        names = "RinP_" + str(i)
        prob.linear_constraints.add(lin_expr=[[[Ulist[7]*numT+T+QI_c,
                                                Ulist[0]*numS*numT+Slist[0]*numT+T+QO_c,
                                                Ulist[6]*numS*numT+Slist[0]*numT+T+QO_c],
                                               [-1.0,1.0,1.0]]],
                                    senses="E", rhs=[0], names=[names])
    # MTBE = FCCU_S2
    i = 0
    for T in Tlist:
        i += 1
        names = "MinP_" + str(i)
        prob.linear_constraints.add(lin_expr=[[[Ulist[8]*numT+T+QI_c,
                                                Ulist[2]*numS*numT+Slist[1]*numT+T+QO_c],
                                               [-1.0,1.0]]],
                                    senses="E", rhs=[0], names=[names])
    #================================== OCINV ================================
    #                                  Volume State Function of gasoline oil tank  ===============================
    i = 0
    i += 1
    names = "Volume_OCtank" + str(0) + " " + str(i)
    ind = []
    val = []
    ind.append(OClist[0] * numT + 0 + OCINV_c)
    val.append(1.0)
    ind.append(Ulist[7] * numS * numT + Slist[0] * numT + 0 + QO_c)
    val.append(-1.0 * hours)
    ind.append(OClist[0] * numT + 0 + OCtankout_c)
    val.append(1.0 * hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[0]], names=[names])
    for T in Tlist[1:]:
        i += 1
        names = "Volume_OCtank" + str(0) + " " + str(i)
        ind = []
        val = []
        ind.append(OClist[0] * numT + T + OCINV_c)
        val.append(1.0)
        ind.append(OClist[0] * numT + T-1 + OCINV_c)
        val.append(-1.0)
        ind.append(Ulist[7] * numS * numT + Slist[0] * numT + T + QO_c)
        val.append(-1.0 * hours)
        ind.append(OClist[0] * numT + T + OCtankout_c)
        val.append(1.0 * hours)
        prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0], names=[names])
    i = 0
    i += 1
    names = "Volume_OCtank" + str(1) + " " + str(i)
    ind = []
    val = []
    ind.append(OClist[1] * numT + 0 + OCINV_c)
    val.append(1.0)
    ind.append(Ulist[7] * numS * numT + Slist[1] * numT + 0 + QO_c)
    val.append(-1.0 * hours)
    ind.append(OClist[1] * numT + 0 + OCtankout_c)
    val.append(1.0 * hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[1]], names=[names])
    for T in Tlist[1:]:
        i += 1
        names = "Volume_OCtank" + str(1) + " " + str(i)
        ind = []
        val = []
        ind.append(OClist[1] * numT + T + OCINV_c)
        val.append(1.0)
        ind.append(OClist[1] * numT + T-1 + OCINV_c)
        val.append(-1.0)
        ind.append(Ulist[7] * numS * numT + Slist[1] * numT + T + QO_c)
        val.append(-1.0 * hours)
        ind.append(OClist[1] * numT + T + OCtankout_c)
        val.append(1.0 * hours)
        prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0], names=[names])
    i = 0
    i += 1
    names = "Volume_OCtank" + str(2) + " " + str(i)
    ind = []
    val = []
    ind.append(OClist[2] * numT + 0 + OCINV_c)
    val.append(1.0)
    ind.append(Ulist[8] * numS * numT + Slist[0] * numT + 0 + QO_c)
    val.append(-1.0 * hours)
    ind.append(OClist[2] * numT + 0 + OCtankout_c)
    val.append(1.0 * hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[2]], names=[names])
    for T in Tlist[1:]:
        i += 1
        names = "Volume_OCtank" + str(2) + " " + str(i)
        ind = []
        val = []
        ind.append(OClist[2] * numT + T + OCINV_c)
        val.append(1.0)
        ind.append(OClist[2] * numT + T-1 + OCINV_c)
        val.append(-1.0)
        ind.append(Ulist[8] * numS * numT + Slist[0] * numT + T + QO_c)
        val.append(-1.0 * hours)
        ind.append(OClist[2] * numT + T + OCtankout_c)
        val.append(1.0 * hours)
        prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0], names=[names])
    i = 0
    i += 1
    names = "Volume_OCtank" + str(3) + " " + str(i)
    ind = []
    val = []
    ind.append(OClist[3] * numT + 0 + OCINV_c)
    val.append(1.0)
    ind.append(OClist[3] * numT + 0 + OC_c)
    val.append(-1.0 * hours)
    ind.append(OClist[3] * numT + 0 + OCtankout_c)
    val.append(1.0 * hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[3]], names=[names])
    for T in Tlist[1:]:
        i += 1
        names = "Volume_OCtank" + str(3) + " " + str(i)
        ind = []
        val = []
        ind.append(OClist[3] * numT + T + OCINV_c)
        val.append(1.0)
        ind.append(OClist[3] * numT + T-1 + OCINV_c)
        val.append(-1.0)
        ind.append(OClist[3] * numT + T + OC_c)
        val.append(-1.0 * hours)
        ind.append(OClist[3] * numT + T + OCtankout_c)
        val.append(1.0 * hours)
        prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0], names=[names])
    # # HDS = HDSint + OC_HDS - HDSoutput  OC variable is not appear in gams.
    # i = 0
    # for T in Tlist:
    #     i += 1
    #     names = "HDINV_" + str(i)
    #     prob.linear_constraints.add(lin_expr=[[[OClist[3]*numT+T+OCINV_c,
    #                                             OClist[3]*numT+T+OCINVint_c,
    #                                             OClist[3]*numT+T+OC_c,
    #                                             OClist[3]*numT+T+OCtankout_c],
    #                                            [-1.0,1.0,1.0*hours,-1.0*hours]]],
    #                                 senses="E", rhs=[0], names=[names])
    i = 0
    i += 1
    names = "Volume_OCtank" + str(4) + " " + str(i)
    ind = []
    val = []
    ind.append(OClist[4] * numT + 0 + OCINV_c)
    val.append(1.0)
    ind.append(Ulist[3] * numS * numT + Slist[0] * numT + 0 + QO_c)
    val.append(-1.0 * hours)
    ind.append(OClist[4] * numT + 0 + OCtankout_c)
    val.append(1.0 * hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[4]], names=[names])
    for T in Tlist[1:]:
        i += 1
        names = "Volume_OCtank" + str(4) + " " + str(i)
        ind = []
        val = []
        ind.append(OClist[4] * numT + T + OCINV_c)
        val.append(1.0)
        ind.append(OClist[4] * numT + T-1 + OCINV_c)
        val.append(-1.0)
        ind.append(Ulist[3] * numS * numT + Slist[0] * numT + T + QO_c)
        val.append(-1.0 * hours)
        ind.append(OClist[4] * numT + T + OCtankout_c)
        val.append(1.0 * hours)
        prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0], names=[names])
    # # Etherified = Etherifiedint + QO_ETH_S1 - Etherifiedoutput
    # i = 0
    # for T in Tlist:
    #     i += 1
    #     names = "EtINV_" + str(i)
    #     prob.linear_constraints.add(lin_expr=[[[OClist[4]*numT+T+OCINV_c,
    #                                             OClist[4]*numT+T+OCINVint_c,
    #                                             Ulist[3]*numS*numT+Slist[0]*numT+T+QO_c,
    #                                             OClist[4]*numT+T+OCtankout_c],
    #                                            [-1.0,1.0,1.0*hours,-1.0*hours]]],
    #                                 senses="E", rhs=[0], names=[names])
    i = 0
    i += 1
    names = "Volume_OCtank" + str(5) + " " + str(i)
    ind = []
    val = []
    ind.append(OClist[5] * numT + 0 + OCINV_c)
    val.append(1.0)
    # ind.append(Ulist[5] * numS * numT + Slist[0] * numT + 0 + QO_c)
    # val.append(-1.0 * hours)
    ind.append(Ulist[6] * numS * numT + Slist[1] * numT + 0 + QO_c)
    val.append(-1.0 * hours)
    ind.append(OClist[5] * numT + 0 + OCtankout_c)
    val.append(1.0 * hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[5]], names=[names])
    for T in Tlist[1:]:
        i += 1
        names = "Volume_OCtank" + str(5) + " " + str(i)
        ind = []
        val = []
        ind.append(OClist[5] * numT + T + OCINV_c)
        val.append(1.0)
        ind.append(OClist[5] * numT + T-1 + OCINV_c)
        val.append(-1.0)
        # ind.append(Ulist[5] * numS * numT + Slist[0] * numT + T + QO_c)
        # val.append(-1.0 * hours)
        ind.append(Ulist[6] * numS * numT + Slist[1] * numT + T + QO_c)
        val.append(-1.0 * hours)
        ind.append(OClist[5] * numT + T + OCtankout_c)
        val.append(1.0 * hours)
        prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0], names=[names])
    # # diesel1 = diesel1int + QO_HTU1_S1 - diesel1output
    # i = 0
    # for T in Tlist:
    #     i += 1
    #     names = "d1INV_" + str(i)
    #     prob.linear_constraints.add(lin_expr=[[[OClist[5]*numT+T+OCINV_c,
    #                                             OClist[5]*numT+T+OCINVint_c,
    #                                             Ulist[5]*numS*numT+Slist[0]*numT+T+QO_c,
    #                                             OClist[5]*numT+T+OCtankout_c],
    #                                            [-1.0,1.0,1.0*hours,-1.0*hours]]],
    #                                 senses="E", rhs=[0], names=[names])
    i = 0
    i += 1
    names = "Volume_OCtank" + str(6) + " " + str(i)
    ind = []
    val = []
    ind.append(OClist[6] * numT + 0 + OCINV_c)
    val.append(1.0)
    ind.append(Ulist[5] * numS * numT + Slist[0] * numT + 0 + QO_c)
    val.append(-1.0 * hours)
    ind.append(OClist[6] * numT + 0 + OCtankout_c)
    val.append(1.0 * hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[6]], names=[names])
    for T in Tlist[1:]:
        i += 1
        names = "Volume_OCtank" + str(6) + " " + str(i)
        ind = []
        val = []
        ind.append(OClist[6] * numT + T + OCINV_c)
        val.append(1.0)
        ind.append(OClist[6] * numT + T-1 + OCINV_c)
        val.append(-1.0)
        ind.append(Ulist[5] * numS * numT + Slist[0] * numT + T + QO_c)
        val.append(-1.0 * hours)
        ind.append(OClist[6] * numT + T + OCtankout_c)
        val.append(1.0 * hours)
        prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0], names=[names])
    # # diesel2 = diesel2int + QO_HTU2_S2 - diesel2output
    # i = 0
    # for T in Tlist:
    #     i += 1
    #     names = "d2INV_" + str(i)
    #     prob.linear_constraints.add(lin_expr=[[[OClist[6]*numT+T+OCINV_c,
    #                                             OClist[6]*numT+T+OCINVint_c,
    #                                             Ulist[6]*numS*numT+Slist[1]*numT+T+QO_c,
    #                                             OClist[6]*numT+T+OCtankout_c],
    #                                            [-1.0,1.0,1.0*hours,-1.0*hours]]],
    #                                 senses="E", rhs=[0], names=[names])
    i = 0
    i += 1
    names = "Volume_OCtank" + str(7) + " " + str(i)
    ind = []
    val = []
    ind.append(OClist[7] * numT + 0 + OCINV_c)
    val.append(1.0)
    ind.append(OClist[7] * numT + 0 + OC_c)
    val.append(-1.0 * hours)
    ind.append(OClist[7] * numT + 0 + OCtankout_c)
    val.append(1.0 * hours)
    prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[OCtank_ini[7]], names=[names])
    for T in Tlist[1:]:
        i += 1
        names = "Volume_OCtank" + str(7) + " " + str(i)
        ind = []
        val = []
        ind.append(OClist[7] * numT + T + OCINV_c)
        val.append(1.0)
        ind.append(OClist[7] * numT + T-1 + OCINV_c)
        val.append(-1.0)
        ind.append(OClist[7] * numT + T + OC_c)
        val.append(-1.0 * hours)
        ind.append(OClist[7] * numT + T + OCtankout_c)
        val.append(1.0 * hours)
        prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0], names=[names])
    # # Lightdi = Lightdiint + OC_Lightdi - Lightdioutput
    # i = 0
    # for T in Tlist:
    #     i += 1
    #     names = "LiINV_" + str(i)
    #     prob.linear_constraints.add(lin_expr=[[[OClist[7]*numT+T+OCINV_c,
    #                                             OClist[7]*numT+T+OCINVint_c,
    #                                             OClist[7]*numT+T+OC_c,
    #                                             OClist[7]*numT+T+OCtankout_c],
    #                                            [-1.0,1.0,1.0*hours,-1.0*hours]]],
    #                                 senses="E", rhs=[0], names=[names])
    #================================= OCINVint ========================================
    # ================================= OC and O ========================================
    # OC1andO1    sum(O1,Q1(OC1,O1,T)) =E= OCtankout(OC1,T)
    i = 0
    for OC in OClist[0:5]:
        for T in Tlist:
            i += 1
            names = "OC1andO1_" + str(i)
            ind = []
            val = []
            for O in Olist[0:5]:
                ind.append(OC*numO*numT+O*numT+T+Q_c)
                val.append(1.0)
            ind.append(OC*numT+T+OCtankout_c)
            val.append(-1.0)
            prob.linear_constraints.add(lin_expr=[[ind,val]],
                                            senses="E", rhs=[0], names=[names])
    # OC2andO2    sum(O2,Q2(OC2,O2,T)) =E= OCtankout(OC2,T)
    i = 0
    for OC in OClist[5:8]:
        for T in Tlist:
            i += 1
            names = "OC2andO2_" + str(i)
            ind = []
            val = []
            for O in Olist[5:8]:
                ind.append(OC*numO*numT+O*numT+T+Q_c)
                val.append(1.0)
            ind.append(OC*numT+T+OCtankout_c)
            val.append(-1.0)
            prob.linear_constraints.add(lin_expr=[[ind,val]],
                                            senses="E", rhs=[0], names=[names])
    # ================================= OINV ========================================
    #OINV(O1,T) =e= OINVint(O1,T)+ sum(OC1,Q1(OC1,O1,T)*hours)- sum(L,Otankout(O1,L,T)*hours)
    for O in Olist[0:5]:
        i = 0
        i += 1
        names = "Volume_Otank" + str(O) + " " + str(i)
        ind = []
        val = []
        ind.append(O * numT + 0 + OINV_c)
        val.append(1.0)
        for OC in OClist[0:5]:
            ind.append(OC * numO * numT + O * numT + 0 + Q_c)
            val.append(-1.0 * hours)
        for L in Llist:
            ind.append(O * numL * numT + L * numT + 0 + Otankout_c)
            val.append(hours)
        prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[Otank_ini[O]], names=[names])
        for T in Tlist[1:]:
            i += 1
            names = "Volume_Otank " + str(O) + " " + str(i)
            ind = []
            val = []
            ind.append(O * numT + T + OINV_c)
            val.append(1.0)
            ind.append(O * numT + T-1 + OINV_c)
            val.append(-1.0)
            for OC in OClist[0:5]:
                ind.append(OC * numO * numT + O * numT + T + Q_c)
                val.append(-1.0 * hours)
            for L in Llist:
                ind.append(O * numL * numT + L * numT + T + Otankout_c)
                val.append(hours)
            prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    for O in Olist[5:8]:
        i = 0
        i += 1
        names = "Volume_Otank" + str(O) + " " + str(i)
        ind = []
        val = []
        ind.append(O * numT + 0 + OINV_c)
        val.append(1.0)
        for OC in OClist[5:8]:
            ind.append(OC * numO * numT + O * numT + 0 + Q_c)
            val.append(-1.0 * hours)
        for L in Llist:
            ind.append(O * numL * numT + L * numT + 0 + Otankout_c)
            val.append(hours)
        prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[Otank_ini[O]], names=[names])
        for T in Tlist[1:]:
            i += 1
            names = "Volume_Otank " + str(O) + " " + str(i)
            ind = []
            val = []
            ind.append(O * numT + T + OINV_c)
            val.append(1.0)
            ind.append(O * numT + T-1 + OINV_c)
            val.append(-1.0)
            for OC in OClist[5:8]:
                ind.append(OC * numO * numT + O * numT + T + Q_c)
                val.append(-1.0 * hours)
            for L in Llist:
                ind.append(O * numL * numT + L * numT + T + Otankout_c)
                val.append(hours)
            prob.linear_constraints.add(lin_expr=[[ind, val]], senses="E", rhs=[0.0], names=[names])
    #================================= OINVint ========================================
    # ================================= PROLimit ========================================
    # PROLimit1S(O1,T)  sum(OC1,PRO('S',OC1)*Q1(OC1,O1,T)) =L= PROMAX('S',O1)*sum(OC1,Q1(OC1,O1,T))
    # P /RON,CN,S,CPF/
    i = 0
    for O in Olist[0:5]:
        for T in Tlist:
            ind = []
            val = []
            names = []
            for OC in OClist[0:5]:
                ind.append(OC * numO * numT + O * numT + T + Q_c)
                # for 'S' property
                val.append(PRO[Plist[2] * numOC + OC] - PROMAX[Plist[2] * numO + O])
            i += 1
            names.append("PROlimit1S_" + str(i))
            prob.linear_constraints.add(lin_expr=[[ind, val]],
                                        senses="L", rhs=[0], names=names)

    # PROLimit1RON(O1,T) sum(OC1,PRO('RON',OC1)*Q1(OC1,O1,T)) =G= PROMIN('RON',O1)*sum(OC1,Q1(OC1,O1,T))
    i = 0
    for O in Olist[0:5]:
        for T in Tlist:
            i += 1
            names = "PROlimitRON_" + str(i)
            ind = []
            val = []
            for OC in OClist[0:5]:
                ind.append(OC * numO * numT + O * numT + T + Q_c)
                # for 'RON' property
                val.append(PRO[Plist[0] * numOC + OC] - PROMIN[Plist[0] * numO + O])
            prob.linear_constraints.add(lin_expr=[[ind, val]],
                                        senses="G", rhs=[0], names=[names])
    # PROLimit2S(O2,T) sum(OC2,PRO('S',OC2)*Q2(OC2,O2,T)) =L= PROMAX('S',O2)*sum(OC2,Q2(OC2,O2,T))
    i = 0
    for O in Olist[5:8]:
        for T in Tlist:
            i += 1
            names = "PROlimit2S_" + str(i)
            ind = []
            val = []
            for OC in OClist[5:8]:
                ind.append(OC * numO * numT + O * numT + T + Q_c)
                # for 'S' property
                val.append(PRO[Plist[2] * numOC + OC] - PROMAX[Plist[2] * numO + O])
            prob.linear_constraints.add(lin_expr=[[ind, val]],
                                        senses="L", rhs=[0], names=[names])
    # PROLimit2CN(O2,T) sum(OC2,PRO('CN',OC2)*Q2(OC2,O2,T)) =G= PROMIN('CN',O2)*sum(OC2,Q2(OC2,O2,T))
    i = 0
    for O in Olist[5:8]:
        for T in Tlist:
            i += 1
            names = "PROlimitCN_" + str(i)
            ind = []
            val = []
            for OC in OClist[5:8]:
                ind.append(OC * numO * numT + O * numT + T + Q_c)
                # for 'CN' property
                val.append(PRO[Plist[1] * numOC + OC] - PROMIN[Plist[1] * numO + O])
            prob.linear_constraints.add(lin_expr=[[ind, val]],
                                        senses="G", rhs=[0], names=[names])
    # PROLimit2CPF(O2,T) sum(OC2,PRO('CPF',OC2)*Q2(OC2,O2,T)) =L= PROMAX('CPF',O2)*sum(OC2,Q2(OC2,O2,T))
    i = 0
    for O in Olist[5:8]:
        for T in Tlist:
            i += 1
            names = "PROlimitF_" + str(i)
            ind = []
            val = []
            for OC in OClist[5:8]:
                ind.append(OC * numO * numT + O * numT + T + Q_c)
                # for 'CPF' property
                val.append(PRO[Plist[3] * numOC + OC] - PROMAX[Plist[3] * numO + O])
            prob.linear_constraints.add(lin_expr=[[ind, val]],
                                        senses="L", rhs=[0], names=[names])
    # ======================================= OCinOlimit =================================
    #OCinOlimit11(OC1,O1,T) sum(OC1_,Q1(OC1_,O1,T))*rMIN(OC1,O1) =L= Q1(OC1,O1,T) ---ratio limit---
    i = 0
    for OC in OClist[0:5]:
        for O in Olist[0:5]:
            for T in Tlist:
                ind = []
                val = []
                names = []
                for OC1 in OClist[0:5]:
                    if OC1 == OC:
                        ind.append(OC1 * numO * numT + O * numT + T + Q_c)
                        val.append(rMIN[OC * numO + O]-1.0)
                    else:
                        ind.append(OC1 * numO * numT + O * numT + T + Q_c)
                        val.append(rMIN[OC * numO + O])
                i += 1
                names.append("OCinO1MIN_" + str(i))
                prob.linear_constraints.add(lin_expr=[[ind, val]],
                                            senses="L", rhs=[0],names=names)
    #OCinOlimit12(OC1,O1,T) sum(OC1_,Q1(OC1_,O1,T))*rMAX(OC1,O1)    =G= Q1(OC1,O1,T)
    i = 0
    for OC in OClist[0:5]:
        for O in Olist[0:5]:
            for T in Tlist:
                ind = []
                val = []
                names = []
                for OC1 in OClist[0:5]:
                    if OC1 == OC:
                        ind.append(OC1 * numO * numT + O * numT + T + Q_c)
                        val.append(rMAX[OC * numO + O]-1.0)
                    else:
                        ind.append(OC1 * numO * numT + O * numT + T + Q_c)
                        val.append(rMAX[OC * numO + O])
                i += 1
                names.append("OCinOlimit1MAX_" + str(i))
                prob.linear_constraints.add(lin_expr=[[ind, val]],
                                            senses="G", rhs=[0],names=names)

    # OCinOlimit21(OC2, O2, T) sum(OC2_, Q2(OC2_, O2, T)) * rMIN(OC2, O2) = L = Q2(OC2, O2, T) ---ratio limit---
    i = 0
    for OC in OClist[5:8]:
        for O in Olist[5:8]:
            for T in Tlist:
                i += 1
                names = "OCinOlimit2MIN_" + str(i)
                ind = []
                val = []
                for OC1 in OClist[5:8]:
                    if OC1 == OC:
                        ind.append(OC1 * numO * numT + O * numT + T + Q_c)
                        val.append(rMIN[OC * numO + O]-1.0)
                    else:
                        ind.append(OC1 * numO * numT + O * numT + T + Q_c)
                        val.append(rMIN[OC * numO + O])
                prob.linear_constraints.add(lin_expr=[[ind, val]],
                                            senses="L", rhs=[0],names=[names])
    #OCinOlimit22(OC2,O2,T).. sum(OC2_,Q2(OC2_,O2,T))*rMAX(OC2,O2)    =G= Q2(OC2,O2,T)
    i = 0
    for OC in OClist[5:8]:
        for O in Olist[5:8]:
            for T in Tlist:
                i += 1
                names = "OCinOlimit2MAX_" + str(i)
                ind = []
                val = []
                for OC1 in OClist[5:8]:
                    if OC1 == OC:
                        ind.append(OC1 * numO * numT + O * numT + T + Q_c)
                        val.append(rMAX[OC * numO + O]-1.0)
                    else:
                        ind.append(OC1 * numO * numT + O * numT + T + Q_c)
                        val.append(rMAX[OC * numO + O])
                prob.linear_constraints.add(lin_expr=[[ind, val]],
                                            senses="G", rhs=[0],names=[names])

    # ======================================== Otankout in L limit =============================
    i = 0
    for L in Llist:
        for O in Olist:
            i += 1
            names = "OinL_" + str(i)
            ind = []
            val = []
            for T in Tlist:
                if T >= DS_num[L,0] and T <= DS_num[L,1]:
                    ind.append(O*numL*numT+L*numT+T+Otankout_c)
                    val.append(hours)
                else:
                    prob.linear_constraints.add(lin_expr=[[[O*numL*numT+L*numT+T+Otankout_c], [1]]],
                                                senses="E", rhs=[0],names=[names])
            prob.linear_constraints.add(lin_expr=[[ind, val]],
                                        senses="L", rhs=[DV1[L,O]],names=[names])
    # ======================================== BiTermFun =======================================

    # BiTermFun11(MATM,MATM1,T)..  xQI('ATM',MATM,MATM1,T)+xQI1('ATM',MATM,MATM1,T) =E= QI('ATM',T)
    i = 0
    for U in Ulist[0:2]:
        for M in Mlist[0:2]:
            for M1 in Mlist[0:2]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "Bi1_" + str(i)
                        prob.linear_constraints.add(
                            lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + xQI_c,
                                        U * numM * numM * numT + M * numM * numT + M1 * numT + T + xQI1_c,
                                        U * numT + T + QI_c, ],
                                       [1.0, 1.0, -1.0]]],
                            senses="E", rhs=[0],names=[names])
    #BiTermFun13(MFCCU,MFCCU1,T).. xQI('FCCU',MFCCU,MFCCU1,T)+xQI1('FCCU',MFCCU,MFCCU1,T) =E= QI('FCCU',T)
    for U in Ulist[2:5]:
        for M in Mlist[0:4]:
            for M1 in Mlist[0:4]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "Bi1_" + str(i)
                        prob.linear_constraints.add(
                            lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + xQI_c,
                                        U * numM * numM * numT + M * numM * numT + M1 * numT + T + xQI1_c,
                                        U * numT + T + QI_c, ],
                                       [1.0, 1.0, -1.0]]],
                            senses="E", rhs=[0],names=[names])
    #BiTermFun16(MHTU1,MHTU11,T)..xQI('HTU1',MHTU1,MHTU11,T)+xQI1('HTU1',MHTU1,MHTU11,T) =E= QI('HTU1',T)
    for U in Ulist[5:7]:
        for M in Mlist[0:2]:
            for M1 in Mlist[0:2]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "Bi1_" + str(i)
                        prob.linear_constraints.add(
                            lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + xQI_c,
                                        U * numM * numM * numT + M * numM * numT + M1 * numT + T + xQI1_c,
                                        U * numT + T + QI_c, ],
                                       [1.0, 1.0, -1.0]]],
                            senses="E", rhs=[0],names=[names])
    # ============================================ BiTermFun 2 ==============================
    # BiTermFun21(MATM,MATM1,T)..xQI('ATM',MATM,MATM1,T) =L= x('ATM',MATM,MATM1,T)*QIinputL('ATM','MAX')
    i = 0
    for U in Ulist[0:2]:
        for M in Mlist[0:2]:
            for M1 in Mlist[0:2]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "Bi2_" + str(i)
                        prob.linear_constraints.add(
                            lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + xQI_c,
                                        U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c],
                                       [1.0, -QIinputL[U*2+1]]]],
                            senses="L", rhs=[0],names=[names])
    # BiTermFun23(MFCCU,MFCCU1,T)..xQI('FCCU',MFCCU,MFCCU1,T) =L= x('FCCU',MFCCU,MFCCU1,T)*QIinputL('FCCU','MAX')
    for U in Ulist[2:5]:
        for M in Mlist[0:4]:
            for M1 in Mlist[0:4]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "Bi2_" + str(i)
                        prob.linear_constraints.add(
                            lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + xQI_c,
                                        U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c],
                                       [1.0, -QIinputL[U*2+1]]]],
                            senses="L", rhs=[0],names=[names])
    # BiTermFun26(MHTU1,MHTU11,T)..xQI('HTU1',MHTU1,MHTU11,T) =L= x('HTU1',MHTU1,MHTU11,T)*QIinputL('HTU1','MAX')
    for U in Ulist[5:7]:
        for M in Mlist[0:2]:
            for M1 in Mlist[0:2]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "Bi2_" + str(i)
                        prob.linear_constraints.add(
                            lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + xQI_c,
                                        U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c],
                                       [1.0, -QIinputL[U*2+1]]]],
                            senses="L", rhs=[0],names=[names])
    # ================================================ BiTermFun 3 =================================
    # BiTermFun31(MATM,MATM1,T)..xQI1('ATM',MATM,MATM1,T) =L= (1-x('ATM',MATM,MATM1,T))*QIinputL('ATM','MAX')
    i = 0
    for U in Ulist[0:2]:
        for M in Mlist[0:2]:
            for M1 in Mlist[0:2]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "Bi3_" + str(i)
                        prob.linear_constraints.add(
                            lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + xQI1_c,
                                        U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c],
                                       [1.0, QIinputL[U*2+1]]]],
                            senses="L", rhs=[QIinputL[U*2+1]],names=[names])
    # BiTermFun33(MFCCU,MFCCU1,T)..xQI1('FCCU',MFCCU,MFCCU1,T) =L= (1-x('FCCU',MFCCU,MFCCU1,T))*QIinputL('FCCU','MAX')
    for U in Ulist[2:5]:
        for M in Mlist[0:4]:
            for M1 in Mlist[0:4]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "Bi3_" + str(i)
                        prob.linear_constraints.add(
                            lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + xQI1_c,
                                        U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c],
                                       [1.0, QIinputL[U*2+1]]]],
                            senses="L", rhs=[QIinputL[U*2+1]],names=[names])
    # BiTermFun36(MHTU1,MHTU11,T)..xQI1('HTU1',MHTU1,MHTU11,T) =L= (1-x('HTU1',MHTU1,MHTU11,T))*QIinputL('HTU1','MAX')
    for U in Ulist[5:7]:
        for M in Mlist[0:2]:
            for M1 in Mlist[0:2]:
                if M1 != M:
                    for T in Tlist:
                        i += 1
                        names = "Bi3_" + str(i)
                        prob.linear_constraints.add(
                            lin_expr=[[[U * numM * numM * numT + M * numM * numT + M1 * numT + T + xQI1_c,
                                        U * numM * numM * numT + M * numM * numT + M1 * numT + T + x_c],
                                       [1.0, QIinputL[U*2+1]]]],
                            senses="L", rhs=[QIinputL[U*2+1]],names=[names])
    # ========================================== TriTermFun ===============================
    # TriTermFun11(MATM,T)..xy('ATM',MATM,T) =L= y('ATM',MATM,T)
    i = 0
    for U in Ulist[0:2]:
        for M in Mlist[0:2]:
            for T in Tlist:
                i += 1
                names = "Tri1_" + str(i)
                prob.linear_constraints.add(
                            lin_expr=[[[U * numM * numT + M * numT + T + xy_c,
                                        U * numM * numT + M * numT + T + y_c],
                                       [1.0, -1.0]]],
                            senses="L", rhs=[0],names=[names])
    # TriTermFun13(MFCCU,T)..xy('FCCU',MFCCU,T) =L= y('FCCU',MFCCU,T)
    for U in Ulist[2:5]:
        for M in Mlist[0:4]:
            for T in Tlist:
                i += 1
                names = "Tri1_" + str(i)
                prob.linear_constraints.add(
                            lin_expr=[[[U * numM * numT + M * numT + T + xy_c,
                                        U * numM * numT + M * numT + T + y_c],
                                       [1.0, -1.0]]],
                            senses="L", rhs=[0],names=[names])
    # TriTermFun16(MHTU1,T)..xy('HTU1',MHTU1,T) =L= y('HTU1',MHTU1,T)
    for U in Ulist[5:7]:
        for M in Mlist[0:2]:
            for T in Tlist:
                i += 1
                names = "Tri1_" + str(i)
                prob.linear_constraints.add(
                            lin_expr=[[[U * numM * numT + M * numT + T + xy_c,
                                        U * numM * numT + M * numT + T + y_c],
                                       [1.0, -1.0]]],
                            senses="L", rhs=[0],names=[names])
    # ========================================= TriTermFun 2 ===============================
    # TriTermFun21(MATM1,T)..xy('ATM',MATM1,T) =L= 1-sum(MATM,x('ATM',MATM,MATM1,T))
    i =0
    for U in Ulist[0:2]:
        for M in Mlist[0:2]:
            for T in Tlist:
                i += 1
                names = "Tri2_" + str(i)
                ind = []
                val = []
                for M1 in Mlist[0:2]:
                    if M1!= M:
                        ind.append(U * numM * numM * numT + M1 * numM * numT + M * numT + T + x_c)
                        val.append(1.0)
                ind.append(U * numM * numT + M * numT + T + xy_c)
                val.append(1.0)
                prob.linear_constraints.add(lin_expr=[[ind,val]], senses="L", rhs=[1],names=[names])
    # TriTermFun23(MFCCU1,T)..xy('FCCU',MFCCU1,T) =L= 1-sum(MFCCU,x('FCCU',MFCCU,MFCCU1,T))
    for U in Ulist[2:5]:
        for M in Mlist[0:4]:
            for T in Tlist:
                i += 1
                names = "Tri2_" + str(i)
                ind = []
                val = []
                for M1 in Mlist[0:4]:
                    if M1!= M:
                        ind.append(U * numM * numM * numT + M1 * numM * numT + M * numT + T + x_c)
                        val.append(1.0)
                ind.append(U * numM * numT + M * numT + T + xy_c)
                val.append(1.0)
                prob.linear_constraints.add(lin_expr=[[ind,val]], senses="L", rhs=[1],names=[names])
    # TriTermFun26(MHTU11,T)..xy('HTU1',MHTU11,T) =L= 1-sum(MHTU1,x('HTU1',MHTU1,MHTU11,T))
    for U in Ulist[5:7]:
        for M in Mlist[0:2]:
            for T in Tlist:
                i += 1
                names = "Tri2_" + str(i)
                ind = []
                val = []
                for M1 in Mlist[0:2]:
                    if M1!= M:
                        ind.append(U * numM * numM * numT + M1 * numM * numT + M * numT + T + x_c)
                        val.append(1.0)
                ind.append(U * numM * numT + M * numT + T + xy_c)
                val.append(1.0)
                prob.linear_constraints.add(lin_expr=[[ind,val]], senses="L", rhs=[1],names=[names])
    # ========================================== TriTermFun 3 ========================
    # TriTermFun31(MATM1,T)..xy('ATM',MATM1,T) =G= y('ATM',MATM1,T)+(1-sum(MATM,x('ATM',MATM,MATM1,T)))-1
    i = 0
    for U in Ulist[0:2]:
        for M in Mlist[0:2]:
            for T in Tlist:
                i += 1
                names = "Tri3_" + str(i)
                ind = []
                val = []
                for M1 in Mlist[0:2]:
                    if M1!= M:
                        ind.append(U * numM * numM * numT + M1 * numM * numT + M * numT + T + x_c)
                        val.append(1.0)
                ind.append(U * numM * numT + M * numT + T + xy_c)
                ind.append(U * numM * numT + M * numT + T + y_c)
                val.append(1.0)
                val.append(-1)
                prob.linear_constraints.add(lin_expr=[[ind,val]], senses="G", rhs=[0],names=[names])
    # TriTermFun33(MFCCU1,T)..xy('FCCU',MFCCU1,T) =G= y('FCCU',MFCCU1,T)+(1-sum(MFCCU,x('FCCU',MFCCU,MFCCU1,T)))-1
    for U in Ulist[2:5]:
        for M in Mlist[0:4]:
            for T in Tlist:
                i += 1
                names = "Tri3_" + str(i)
                ind = []
                val = []
                for M1 in Mlist[0:4]:
                    if M1!= M:
                        ind.append(U * numM * numM * numT + M1 * numM * numT + M * numT + T + x_c)
                        val.append(1.0)
                ind.append(U * numM * numT + M * numT + T + xy_c)
                ind.append(U * numM * numT + M * numT + T + y_c)
                val.append(1.0)
                val.append(-1)
                prob.linear_constraints.add(lin_expr=[[ind,val]], senses="G", rhs=[0],names=[names])
    # TriTermFun36(MHTU11,T)..xy('HTU1',MHTU11,T) =G= y('HTU1',MHTU11,T)+(1-sum(MHTU1,x('HTU1',MHTU1,MHTU11,T)))-1
    for U in Ulist[5:7]:
        for M in Mlist[0:2]:
            for T in Tlist:
                i += 1
                names = "Tri3_" + str(i)
                ind = []
                val = []
                for M1 in Mlist[0:2]:
                    if M1!= M:
                        ind.append(U * numM * numM * numT + M1 * numM * numT + M * numT + T + x_c)
                        val.append(1.0)
                ind.append(U * numM * numT + M * numT + T + xy_c)
                ind.append(U * numM * numT + M * numT + T + y_c)
                val.append(1.0)
                val.append(-1)
                prob.linear_constraints.add(lin_expr=[[ind,val]], senses="G", rhs=[0],names=[names])
    # ========================================= TriTermFun 4 ========================
    # TriTermFun41(MATM1,T)..xyQI('ATM',MATM1,T)+xyQI1('ATM',MATM1,T) =E= QI('ATM',T)
    i = 0
    for U in Ulist[0:2]:
        for M in Mlist[0:2]:
            for T in Tlist:
                i += 1
                names = "Tri4_" + str(i)
                prob.linear_constraints.add(lin_expr=[[[U*numM*numT+M*numT+T+xyQI_c,
                                                        U * numM * numT + M * numT + T + xyQI1_c,
                                                        U * numT + T + QI_c],
                                                       [1.0,1.0,-1.0]]], senses="E", rhs=[0],names=[names])
    # TriTermFun43(MFCCU1,T)..xyQI('FCCU',MFCCU1,T)+xyQI1('FCCU',MFCCU1,T) =E= QI('FCCU',T)
    for U in Ulist[2:5]:
        for M in Mlist[0:4]:
            for T in Tlist:
                i += 1
                names = "Tri4_" + str(i)
                prob.linear_constraints.add(lin_expr=[[[U*numM*numT+M*numT+T+xyQI_c,
                                                        U * numM * numT + M * numT + T + xyQI1_c,
                                                        U * numT + T + QI_c],
                                                       [1.0,1.0,-1.0]]], senses="E", rhs=[0],names=[names])
    # TriTermFun46(MHTU11,T)..xyQI('HTU1',MHTU11,T)+xyQI1('HTU1',MHTU11,T) =E= QI('HTU1',T)
    for U in Ulist[5:7]:
        for M in Mlist[0:2]:
            for T in Tlist:
                i += 1
                names = "Tri4_" + str(i)
                prob.linear_constraints.add(lin_expr=[[[U*numM*numT+M*numT+T+xyQI_c,
                                                        U * numM * numT + M * numT + T + xyQI1_c,
                                                        U * numT + T + QI_c],
                                                       [1.0,1.0,-1.0]]], senses="E", rhs=[0],names=[names])
    # =========================================== TriTermFun 5 ========================
    # TriTermFun51(MATM1,T)..xyQI('ATM',MATM1,T) =L= xy('ATM',MATM1,T)*QIinputL('ATM','MAX')
    i = 0
    for U in Ulist[0:2]:
        for M in Mlist[0:2]:
            for T in Tlist:
                i += 1
                names = "Tri5_" + str(i)
                prob.linear_constraints.add(lin_expr=[[[U * numM * numT + M * numT + T + xyQI_c,
                                                        U * numM * numT + M * numT + T + xy_c],
                                                       [1.0,-300.]]], senses="L", rhs=[0],names=[names])
    # TriTermFun53(MFCCU1,T)..xyQI('FCCU',MFCCU1,T) =L= xy('FCCU',MFCCU1,T)*QIinputL('FCCU','MAX')
    for U in Ulist[2:5]:
        for M in Mlist[0:4]:
            for T in Tlist:
                i += 1
                names = "Tri5_" + str(i)
                prob.linear_constraints.add(lin_expr=[[[U * numM * numT + M * numT + T + xyQI_c,
                                                        U * numM * numT + M * numT + T + xy_c],
                                                       [1.0,-QIinputL[U*2+1]]]], senses="L", rhs=[0],names=[names])
    # TriTermFun56(MHTU11,T)..xyQI('HTU1',MHTU11,T) =L= xy('HTU1',MHTU11,T)*QIinputL('HTU1','MAX')
    for U in Ulist[5:7]:
        for M in Mlist[0:2]:
            for T in Tlist:
                i += 1
                names = "Tri5_" + str(i)
                prob.linear_constraints.add(lin_expr=[[[U * numM * numT + M * numT + T + xyQI_c,
                                                        U * numM * numT + M * numT + T + xy_c],
                                                       [1.0,-QIinputL[U*2+1]]]], senses="L", rhs=[0],names=[names])
    # =========================================== TriTermFun 6 ========================
    # TriTermFun61(MATM1,T)..xyQI1('ATM',MATM1,T) =L= (1-xy('ATM',MATM1,T))*QIinputL('ATM','MAX')
    i = 0
    for U in Ulist[0:2]:
        for M in Mlist[0:2]:
            for T in Tlist:
                i += 1
                names = "Tri6_" + str(i)
                prob.linear_constraints.add(lin_expr=[[[U * numM * numT + M * numT + T + xyQI1_c,
                                                        U * numM * numT + M * numT + T + xy_c],
                                                       [1.0,QIinputL[U*2+1]]]],
                                            senses="L", rhs=[QIinputL[U*2+1]],names=[names])
    # TriTermFun63(MFCCU1,T)..xyQI1('FCCU',MFCCU1,T) =L= (1-xy('FCCU',MFCCU1,T))*QIinputL('FCCU','MAX')
    for U in Ulist[2:5]:
        for M in Mlist[0:4]:
            for T in Tlist:
                i += 1
                names = "Tri6_" + str(i)
                prob.linear_constraints.add(lin_expr=[[[U * numM * numT + M * numT + T + xyQI1_c,
                                                        U * numM * numT + M * numT + T + xy_c],
                                                       [1.0,QIinputL[U*2+1]]]],
                                            senses="L", rhs=[QIinputL[U*2+1]],names=[names])
    # TriTermFun66(MHTU11,T)..xyQI1('HTU1',MHTU11,T) =L= (1-xy('HTU1',MHTU11,T))*QIinputL('HTU1','MAX')
    for U in Ulist[5:7]:
        for M in Mlist[0:2]:
            for T in Tlist:
                i += 1
                names = "Tri6_" + str(i)
                prob.linear_constraints.add(lin_expr=[[[U * numM * numT + M * numT + T + xyQI1_c,
                                                        U * numM * numT + M * numT + T + xy_c],
                                                       [1.0,QIinputL[U*2+1]]]],
                                            senses="L", rhs=[QIinputL[U*2+1]],names=[names])
    # # ================================= Feasibility ===============================================

    prob.variables.set_lower_bounds(zip(range(xQI_c, xQIcount + xQI_c), [0] * xQIcount))
    prob.variables.set_upper_bounds(zip(range(xQI_c, xQIcount + xQI_c), [300] * xQIcount))
    prob.variables.set_lower_bounds(zip(range(xyQI_c, xyQIcount + xyQI_c), [0] * xyQIcount))
    prob.variables.set_upper_bounds(zip(range(xyQI_c, xyQIcount + xyQI_c), [300] * xyQIcount))
    prob.variables.set_lower_bounds(zip(range(QO_c, QOcount + QO_c), [0] * QOcount))
    prob.variables.set_upper_bounds(zip(range(QO_c, QOcount + QO_c), [300] * QOcount))
    prob.variables.set_lower_bounds(zip(range(QI_c, QIcount + QI_c), [0] * QIcount))
    prob.variables.set_upper_bounds(zip(range(QI_c, QIcount + QI_c), [300] * QIcount))
    for T in Tlist:
        prob.variables.set_lower_bounds([(Ulist[0]*numT+T+QI_c,200),
                                         (Ulist[3] * numT + T + QI_c, 5),
                                         (Ulist[5]*numT+T+QI_c,5)])#
    prob.variables.set_lower_bounds(zip(range(OC_c, OCcount + OC_c), [0] * OCcount))
    prob.variables.set_upper_bounds(zip(range(OC_c, OCcount + OC_c), [300] * OCcount))
    prob.variables.set_lower_bounds(zip(range(OCINV_c, OCINVcount + OCINV_c), [0] * OCINVcount))
    prob.variables.set_upper_bounds(zip(range(OCINV_c, OCINVcount + OCINV_c), [4000] * OCINVcount))
    prob.variables.set_lower_bounds(zip(range(OCtankout_c, OCtankoutcount + OCtankout_c), [0] * OCtankoutcount))
    prob.variables.set_upper_bounds(zip(range(OCtankout_c, OCtankoutcount + OCtankout_c), [500] * OCtankoutcount))
    prob.variables.set_lower_bounds(zip(range(Q_c, Qcount + Q_c), [0] * Qcount))
    prob.variables.set_upper_bounds(zip(range(Q_c, Qcount + Q_c), [FOCOmax] * Qcount))
    prob.variables.set_lower_bounds(zip(range(OINV_c, OINVcount + OINV_c), [0] * OINVcount))
    prob.variables.set_upper_bounds(zip(range(OINV_c, OINVcount + OINV_c), [2000] * OINVcount))
    prob.variables.set_lower_bounds(zip(range(Otankout_c, Otankoutcount + Otankout_c), [0] * Otankoutcount))
    prob.variables.set_upper_bounds(zip(range(Otankout_c, Otankoutcount + Otankout_c), [FOout_MAX] * Otankoutcount))
    prob.variables.set_lower_bounds(zip(range(xy_c, xycount + xy_c), [0] * xycount))
    prob.variables.set_upper_bounds(zip(range(xy_c, xycount + xy_c), [1] * xycount))
    prob.variables.set_lower_bounds(zip(range(y_c, y_c + ycount), Mode))
    prob.variables.set_upper_bounds(zip(range(y_c, y_c + ycount), Mode))
    # for T in Tlist:
    #     prob.variables.set_lower_bounds(0*numT+T+QI_c, QI_atm[T])
    #     prob.variables.set_upper_bounds(0*numT+T+QI_c, QI_atm[T])
    #     prob.variables.set_lower_bounds(3*numT+T+QI_c, QI_eth[T])
    #     prob.variables.set_upper_bounds(3*numT+T+QI_c, QI_eth[T])
    #     prob.variables.set_lower_bounds(5*numT+T+QI_c, QI_htu1[T])
    #     prob.variables.set_upper_bounds(5*numT+T+QI_c, QI_htu1[T])
    # ========================================= objection coefficients ===========================
    #ObjectFunction..Object = e = sum(T, QI('ATM', T) * OPC +   ---- mode M should be different -----
    #                                 sum(U, sum(M, sum(M1, xQI(U, M, M1, T) * tOpCost(U, M,M1))))+
    #                                 sum(U, sum(M1, xyQI(U, M1, T) * OpCost(U, M1))))+
    #                             sum(T, ap * (sum(O, OINV(O, T)) + sum(OC, OCINV(OC, T))))+
    #                             sum(L, sum(O, bp * (R(L, O) - sum(T, Otankout(O, L, T)))));
    for T in Tlist:
        prob.objective.set_linear(Ulist[0] * numT + T + QI_c, OPC*hours)
    for T in Tlist:
        for U in Ulist[0:2]:
            for M in Mlist[0:2]:
                for M1 in Mlist[0:2]:
                    if M1 != M:
                        prob.objective.set_linear(U * numM * numM * numT + M * numM * numT + M1 * numT + T + xQI_c,
                                                  tOpCost[U * numM * numM + M * numM + M1]*hours)
    for T in Tlist:
        for U in Ulist[2:5]:
            for M in Mlist[0:4]:
                for M1 in Mlist[0:4]:
                    if M1 != M:
                        prob.objective.set_linear(U * numM * numM * numT + M * numM * numT + M1 * numT + T + xQI_c,
                                                  tOpCost[U * numM * numM + M * numM + M1]*hours)
    for T in Tlist:
        for U in Ulist[5:7]:
            for M in Mlist[0:2]:
                for M1 in Mlist[0:2]:
                    if M1 != M:
                        prob.objective.set_linear(U * numM * numM * numT + M * numM * numT + M1 * numT + T + xQI_c,
                                                  tOpCost[U * numM * numM + M * numM + M1]*hours)
    for T in Tlist:
        for U in Ulist[0:2]:
            for M in Mlist[0:2]:
                prob.objective.set_linear(U * numM * numT + M * numT +  T + xyQI_c,
                                                  OpCost[U * numM + M]*hours)
    for T in Tlist:
        for U in Ulist[2:5]:
            for M in Mlist[0:4]:
                prob.objective.set_linear(U * numM * numT + M * numT +  T + xyQI_c,
                                                  OpCost[U * numM + M]*hours)
    for T in Tlist:
        for U in Ulist[5:7]:
            for M in Mlist[0:2]:
                prob.objective.set_linear(U * numM * numT + M * numT +  T + xyQI_c,
                                                  OpCost[U * numM + M]*hours)
    for T in Tlist:
        prob.objective.set_linear([(Ulist[7] * numT + T + QI_c, OpCost[Ulist[7] * numM + Mlist[0]]*hours),
                                   (Ulist[8] * numT + T + QI_c, OpCost[Ulist[8] * numM + Mlist[0]]*hours)])
    for T in Tlist:
        for O in Olist:
            if T == Tlist[-1]:  # initial invertory is zero
                prob.objective.set_linear(O * numT + T + OINV_c, 0.5*apo)
            else:
                prob.objective.set_linear(O * numT + T + OINV_c, apo)
        for OC in OClist:
            if T == Tlist[-1]:    # initial invertory is zero
                prob.objective.set_linear(OC * numT + T + OCINV_c, 0.5*apoc)
            else:
                prob.objective.set_linear(OC * numT + T + OCINV_c, apoc)
    for L in Llist:
        for O in Olist:
            for T in Tlist:
                prob.objective.set_linear(O * numL * numT + L * numT + T + Otankout_c, -bp*hours)#+T*10
    # ================================= SET QI/OC/xQI/xyQI/xQI1/xyQI1 BOUND ===========================
    # # ================================= SET QI/OC/xQI/xyQI/xQI1/xyQI1 BOUND ===========================
    # maxyield = []
    # for M in Mlist[0:2]:
    #     maxyield.append(Yield[Ulist[0] * numM * numS + M * numS + Slist[3]])    # from Ulist[0]-ATM-S4
    # prob.variables.set_upper_bounds(zip(range(Ulist[1]*numT+QI_c,Ulist[1]*numT+numT+QI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[0]*numT+QI_c)*max(maxyield)*0.01]*numT)) # set QI-Ulist[1]-VCD-max
    # prob.variables.set_lower_bounds(zip(range(Ulist[1]*numT+QI_c,Ulist[1]*numT+numT+QI_c),
    #                 [prob.variables.get_lower_bounds(Ulist[0]*numT+QI_c)*min(maxyield)*0.01]*numT)) # set QI-Ulist[1]-VCD-min
    # prob.variables.set_upper_bounds(zip(range(Ulist[1]*numM*numM*numT+xQI_c,Ulist[2]*numM*numM*numT+xQI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[1]*numT+QI_c)]*numM*numM*numT)) # set xQI-Ulist[1]-VCD-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[1]*numM*numM*numT+xQI1_c,Ulist[2]*numM*numM*numT+xQI1_c),
    #                 [prob.variables.get_upper_bounds(Ulist[1]*numT+QI_c)]*numM*numM*numT)) # set xQI1-Ulist[1]-VCD-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[1]*numM*numT+xyQI_c,Ulist[2]*numM*numT+xyQI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[1]*numT+QI_c)]*numM*numT)) # set xyQI-Ulist[1]-VCD-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[1]*numM*numT+xyQI1_c,Ulist[2]*numM*numT+xyQI1_c),
    #                 [prob.variables.get_upper_bounds(Ulist[1]*numT+QI_c)]*numM*numT)) # set xyQI1-Ulist[1]-VCD-max
    # print "QI-VCD-MAX : ",prob.variables.get_upper_bounds(Ulist[1]*numT+QI_c)," = ",\
    #     prob.variables.get_upper_bounds(Ulist[0]*numT+QI_c)*64.534*0.01
    # print "QI-VCD-MIN : ", prob.variables.get_lower_bounds(Ulist[1] * numT + QI_c), " = ", \
    #     prob.variables.get_lower_bounds(Ulist[0] * numT + QI_c)*61.754*0.01
    # print "xQI-VCD-MAX : ",prob.variables.get_upper_bounds(Ulist[1]*numM*numM*numT+xQI_c)," = ",\
    #     prob.variables.get_upper_bounds(Ulist[1]*numT+QI_c)
    # print "xQI1-VCD-MAX : ", prob.variables.get_upper_bounds(Ulist[1]*numM*numM * numT + xQI1_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[1] * numT + QI_c)
    # print "xyQI-VCD-MAX : ", prob.variables.get_upper_bounds(Ulist[1] * numM * numT + xyQI_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[1] * numT + QI_c)
    # print "xyQI1-VCD-MAX : ", prob.variables.get_upper_bounds(Ulist[1] * numM * numT + xyQI1_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[1] * numT + QI_c)
    #
    # maxyield = []
    # for M in Mlist[0:2]:
    #     maxyield.append(Yield[Ulist[1] * numM * numS + M * numS + Slist[1]])   # from Ulist[1]-VCD-S2
    # prob.variables.set_upper_bounds(zip(range(Ulist[2]*numT+QI_c,Ulist[2]*numT+numT+QI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[1]*numT+QI_c)*max(maxyield)*0.01]*numT)) # set QI-Ulist[2]-FCCU-max
    # prob.variables.set_lower_bounds(zip(range(Ulist[2]*numT+QI_c,Ulist[2]*numT+numT+QI_c),
    #                 [prob.variables.get_lower_bounds(Ulist[1]*numT+QI_c)*min(maxyield)*0.01]*numT)) # set QI-Ulist[2]-FCCU-min
    # prob.variables.set_upper_bounds(zip(range(Ulist[2]*numM*numM*numT+xQI_c,Ulist[3]*numM*numM*numT+xQI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[2]*numT+QI_c)]*numM*numM*numT)) # set xQI-Ulist[2]-FCCU-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[2]*numM*numM*numT+xQI1_c,Ulist[3]*numM*numM*numT+xQI1_c),
    #                 [prob.variables.get_upper_bounds(Ulist[2]*numT+QI_c)]*numM*numM*numT)) # set xQI1-Ulist[2]-FCCU-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[2]*numM*numT+xyQI_c,Ulist[3]*numM*numT+xyQI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[2]*numT+QI_c)]*numM*numT)) # set xyQI-Ulist[2]-FCCU-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[2]*numM*numT+xyQI1_c,Ulist[3]*numM*numT+xyQI1_c),
    #                 [prob.variables.get_upper_bounds(Ulist[2]*numT+QI_c)]*numM*numT)) # set xyQI1-Ulist[2]-FCCU-max
    # print "QI-FCCU-MAX : ",prob.variables.get_upper_bounds(Ulist[2]*numT+QI_c)," = ",\
    #     prob.variables.get_upper_bounds(Ulist[1]*numT+QI_c)*37.532*0.01
    # print "QI-FCCU-MIN : ", prob.variables.get_lower_bounds(Ulist[2] * numT + QI_c), " = ", \
    #     prob.variables.get_lower_bounds(Ulist[1] * numT + QI_c)*35.652*0.01
    # print "xQI-FCCU-MAX : ",prob.variables.get_upper_bounds(Ulist[2]*numM*numM*numT+xQI_c)," = ",\
    #     prob.variables.get_upper_bounds(Ulist[2]*numT+QI_c)
    # print "xQI1-FCCU-MAX : ", prob.variables.get_upper_bounds(Ulist[2]*numM*numM * numT + xQI1_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[2] * numT + QI_c)
    # print "xyQI-FCCU-MAX : ", prob.variables.get_upper_bounds(Ulist[2] * numM * numT + xyQI_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[2] * numT + QI_c)
    # print "xyQI1-FCCU-MAX : ", prob.variables.get_upper_bounds(Ulist[2] * numM * numT + xyQI1_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[2] * numT + QI_c)
    #
    # maxyield = []
    # for M in Mlist[0:4]:
    #     maxyield.append(Yield[Ulist[2] * numM * numS + M * numS + Slist[2]])   # from Ulist[2]-FCCU-S3
    # prob.variables.set_upper_bounds(zip(range(Ulist[4]*numT+QI_c,Ulist[4]*numT+numT+QI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[2]*numT+QI_c)*max(maxyield)*0.01]*numT)) # set QI-Ulist[4]-HDS-max
    # prob.variables.set_lower_bounds(zip(range(Ulist[4]*numT+QI_c,Ulist[4]*numT+numT+QI_c),
    #                 [prob.variables.get_lower_bounds(Ulist[2]*numT+QI_c)*min(maxyield)*0.01]*numT)) # set QI-Ulist[4]-HDS-min
    # prob.variables.set_upper_bounds(zip(range(Ulist[4]*numM*numM*numT+xQI_c,Ulist[5]*numM*numM*numT+xQI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[4]*numT+QI_c)]*numM*numM*numT)) # set xQI-Ulist[4]-HDS-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[4]*numM*numM*numT+xQI1_c,Ulist[5]*numM*numM*numT+xQI1_c),
    #                 [prob.variables.get_upper_bounds(Ulist[4]*numT+QI_c)]*numM*numM*numT)) # set xQI1-Ulist[4]-HDS-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[4]*numM*numT+xyQI_c,Ulist[5]*numM*numT+xyQI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[4]*numT+QI_c)]*numM*numT)) # set xyQI-Ulist[4]-HDS-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[4]*numM*numT+xyQI1_c,Ulist[5]*numM*numT+xyQI1_c),
    #                 [prob.variables.get_upper_bounds(Ulist[4]*numT+QI_c)]*numM*numT)) # set xyQI1-Ulist[4]-HDS-max
    # print "QI-HDS-MAX : ", prob.variables.get_upper_bounds(Ulist[4] * numT + QI_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[2] * numT + QI_c) * 45.664 * 0.01
    # print "QI-HDS-MIN : ", prob.variables.get_lower_bounds(Ulist[4] * numT + QI_c), " = ", \
    #     prob.variables.get_lower_bounds(Ulist[2] * numT + QI_c) * 39.580 * 0.01
    # print "xQI-HDS-MAX : ", prob.variables.get_upper_bounds(Ulist[4] * numM * numM * numT + xQI_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[4] * numT + QI_c)
    # print "xQI1-HDS-MAX : ", prob.variables.get_upper_bounds(Ulist[4] * numM * numM * numT + xQI1_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[4] * numT + QI_c)
    # print "xyQI-HDS-MAX : ", prob.variables.get_upper_bounds(Ulist[4] * numM * numT + xyQI_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[4] * numT + QI_c)
    # print "xyQI1-HDS-MAX : ", prob.variables.get_upper_bounds(Ulist[4] * numM * numT + xyQI1_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[4] * numT + QI_c)
    # maxyield = []
    # for M in Mlist[0:4]:
    #     maxyield.append(Yield[Ulist[2] * numM * numS + M * numS + Slist[1]])  # from Ulist[2]-FCCU-S2
    # prob.variables.set_upper_bounds(zip(range(Ulist[8]*numT+QI_c,Ulist[8]*numT+numT+QI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[2]*numT+QI_c)*max(maxyield)*0.01]*numT)) # set QI-Ulist[8]-MTBE-max
    # prob.variables.set_lower_bounds(zip(range(Ulist[8]*numT+QI_c,Ulist[8]*numT+numT+QI_c),
    #                 [prob.variables.get_lower_bounds(Ulist[2]*numT+QI_c)*min(maxyield)*0.01]*numT)) # set QI-Ulist[8]-MTBE-min
    # print "QI-MTBE-MAX : ", prob.variables.get_upper_bounds(Ulist[8] * numT + QI_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[2] * numT + QI_c) * 5.02 * 0.01
    # print "QI-MTBE-MIN : ", prob.variables.get_lower_bounds(Ulist[8] * numT + QI_c), " = ", \
    #     prob.variables.get_lower_bounds(Ulist[2] * numT + QI_c) * 4.13 * 0.01
    #
    # maxyield1 = []
    # maxyield2 = []
    # maxyield3 = []
    # for M in Mlist[0:2]:
    #     maxyield1.append(Yield[Ulist[0] * numM * numS + M * numS + Slist[2]])  # from Ulist[0]-ATM-S3
    # for M in Mlist[0:2]:
    #     maxyield2.append(Yield[Ulist[1] * numM * numS + M * numS + Slist[0]])  # from Ulist[1]-VCD-S1
    # for M in Mlist[0:4]:
    #     maxyield3.append(Yield[Ulist[2] * numM * numS + M * numS + Slist[0]])  # from Ulist[2]-FCCU-S1
    # prob.variables.set_upper_bounds(zip(range(Ulist[6]*numT+QI_c,Ulist[6]*numT+numT+QI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[0]*numT+QI_c)*max(maxyield1)*0.01+
    #                  prob.variables.get_upper_bounds(Ulist[1]*numT+QI_c)*max(maxyield2)*0.01+
    #                  prob.variables.get_upper_bounds(Ulist[2]*numT+QI_c)*max(maxyield3)*0.01]*numT)) # set QI-Ulist[6]-HTU2-max
    # prob.variables.set_lower_bounds(zip(range(Ulist[6]*numT+QI_c,Ulist[6]*numT+numT+QI_c),
    #                 [prob.variables.get_lower_bounds(Ulist[0]*numT+QI_c)*min(maxyield1)*0.01+
    #                  prob.variables.get_lower_bounds(Ulist[1]*numT+QI_c)*min(maxyield2)*0.01+
    #                  prob.variables.get_lower_bounds(Ulist[2]*numT+QI_c)*min(maxyield3)*0.01]*numT)) # set QI-Ulist[6]-HTU2-min
    # prob.variables.set_upper_bounds(zip(range(Ulist[6]*numM*numM*numT+xQI_c,Ulist[7]*numM*numM*numT+xQI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[6]*numT+QI_c)]*numM*numM*numT)) # set xQI-Ulist[6]-HTU2-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[6]*numM*numM*numT+xQI1_c,Ulist[7]*numM*numM*numT+xQI1_c),
    #                 [prob.variables.get_upper_bounds(Ulist[6]*numT+QI_c)]*numM*numM*numT)) # set xQI1-Ulist[6]-HTU2-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[6]*numM*numT+xyQI_c,Ulist[7]*numM*numT+xyQI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[6]*numT+QI_c)]*numM*numT)) # set xyQI-Ulist[6]-HTU2-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[6]*numM*numT+xyQI1_c,Ulist[7]*numM*numT+xyQI1_c),
    #                 [prob.variables.get_upper_bounds(Ulist[6]*numT+QI_c)]*numM*numT)) # set xyQI1-Ulist[6]-HTU2-max
    # print "QI-HTU2-MAX : ",prob.variables.get_upper_bounds(Ulist[6]*numT+QI_c)," = ",\
    #                         prob.variables.get_upper_bounds(Ulist[0]*numT+QI_c)*9.267*0.01," + ",\
    #                         prob.variables.get_upper_bounds(Ulist[1]*numT+QI_c)*12.580*0.01," + ",\
    #                         prob.variables.get_upper_bounds(Ulist[2]*numT+QI_c)*26.683*0.01
    # print "QI-HTU2-MIN : ",prob.variables.get_lower_bounds(Ulist[6]*numT+QI_c)," = ",\
    #                         prob.variables.get_lower_bounds(Ulist[0]*numT+QI_c)*8.109*0.01," + ",\
    #                         prob.variables.get_lower_bounds(Ulist[1]*numT+QI_c)*11.286*0.01," + ",\
    #                         prob.variables.get_lower_bounds(Ulist[2]*numT+QI_c)*22.216*0.01
    # print "xQI-HTU2-MAX : ", prob.variables.get_upper_bounds(Ulist[6] * numM * numM * numT + xQI_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[6] * numT + QI_c)
    # print "xQI1-HTU2-MAX : ", prob.variables.get_upper_bounds(Ulist[6] * numM * numM * numT + xQI1_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[6] * numT + QI_c)
    # print "xyQI-HTU2-MAX : ", prob.variables.get_upper_bounds(Ulist[6] * numM * numT + xyQI_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[6] * numT + QI_c)
    # print "xyQI1-HTU2-MAX : ", prob.variables.get_upper_bounds(Ulist[6] * numM * numT + xyQI1_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[6] * numT + QI_c)
    # maxyield = []
    # for M in Mlist[0:2]:
    #     maxyield.append(Yield[Ulist[0] * numM * numS + M * numS + Slist[1]])     # from Ulist[0]-ATM-S2
    # prob.variables.set_upper_bounds(zip(range(Ulist[5]*numT+QI_c,Ulist[5]*numT+numT+QI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[0]*numT+QI_c)*max(maxyield)*0.01]*numT)) # set QI-Ulist[5]-HTU1-max
    # prob.variables.set_upper_bounds(zip(range(OClist[7]*numT+OC_c,Ulist[7]*numT+numT+OC_c),
    #                 [prob.variables.get_upper_bounds(Ulist[0]*numT+QI_c)*max(maxyield)*0.01-5.0]*numT)) # set OC[7]-Light diesel-max
    # prob.variables.set_lower_bounds(zip(range(Ulist[5]*numT+QI_c,Ulist[5]*numT+numT+QI_c),
    #                 [5.0]*numT))                                                                       # set QI-Ulist[5]-HTU1-min
    # prob.variables.set_lower_bounds(zip(range(OClist[7]*numT+OC_c,Ulist[7]*numT+numT+OC_c),
    #                 [0.0]*numT)) # set OC[7]-Light diesel-min
    # prob.variables.set_upper_bounds(zip(range(Ulist[5]*numM*numM*numT+xQI_c,Ulist[6]*numM*numM*numT+xQI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[5]*numT+QI_c)]*numM*numM*numT)) # set xQI-Ulist[5]-HTU1-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[5]*numM*numM*numT+xQI1_c,Ulist[6]*numM*numM*numT+xQI1_c),
    #                 [prob.variables.get_upper_bounds(Ulist[5]*numT+QI_c)]*numM*numM*numT)) # set xQI1-Ulist[5]-HTU1-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[5]*numM*numT+xyQI_c,Ulist[6]*numM*numT+xyQI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[5]*numT+QI_c)]*numM*numT)) # set xyQI-Ulist[5]-HTU1-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[5]*numM*numT+xyQI1_c,Ulist[6]*numM*numT+xyQI1_c),
    #                 [prob.variables.get_upper_bounds(Ulist[5]*numT+QI_c)]*numM*numT)) # set xyQI1-Ulist[5]-HTU1-max
    # print "QI-HTU1-MAX : ", prob.variables.get_upper_bounds(Ulist[5] * numT + QI_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[0] * numT + QI_c) * 19.403 * 0.01
    # print "QI-HTU1-MIN : ", prob.variables.get_lower_bounds(Ulist[5] * numT + QI_c), " = ",5.0
    # print "xQI-HTU1-MAX : ", prob.variables.get_upper_bounds(Ulist[5] * numM * numM * numT + xQI_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[5] * numT + QI_c)
    # print "xQI1-HTU1-MAX : ", prob.variables.get_upper_bounds(Ulist[5] * numM * numM * numT + xQI1_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[5] * numT + QI_c)
    # print "xyQI-HTU1-MAX : ", prob.variables.get_upper_bounds(Ulist[5] * numM * numT + xyQI_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[5] * numT + QI_c)
    # print "xyQI1-HTU1-MAX : ", prob.variables.get_upper_bounds(Ulist[5] * numM * numT + xyQI1_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[5] * numT + QI_c)
    # print "OC-Light-MAX : ", prob.variables.get_upper_bounds(OClist[7]*numT+OC_c)," = ",\
    #     prob.variables.get_upper_bounds(Ulist[0]*numT+QI_c)*19.403*0.01," - ",5.0
    #
    # maxyield1 = []
    # maxyield2 = []
    # for M in Mlist[0:2]:
    #     maxyield1.append(Yield[Ulist[0] * numM * numS + M * numS + Slist[0]])   # from Ulist[0]-ATM-S1
    # for M in Mlist[0:2]:
    #     maxyield2.append(Yield[Ulist[6] * numM * numS + M * numS + Slist[0]])   # from Ulist[6]-HTU2-S1
    # prob.variables.set_upper_bounds(zip(range(Ulist[7]*numT+QI_c,Ulist[7]*numT+numT+QI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[0]*numT+QI_c)*max(maxyield1)*0.01+
    #                  prob.variables.get_upper_bounds(Ulist[6]*numT+QI_c)*max(maxyield2)*0.01]*numT)) # set QI-Ulist[7]-RF-max
    # prob.variables.set_lower_bounds(zip(range(Ulist[7]*numT+QI_c,Ulist[7]*numT+numT+QI_c),
    #                 [prob.variables.get_lower_bounds(Ulist[0]*numT+QI_c)*min(maxyield1)*0.01+
    #                  prob.variables.get_lower_bounds(Ulist[6]*numT+QI_c)*min(maxyield2)*0.01]*numT)) # set QI-Ulist[7]-RF-min
    # print "QI-RF-MAX : ", prob.variables.get_upper_bounds(Ulist[7] * numT + QI_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[0] * numT + QI_c) * 7.008 * 0.01," + ",\
    #     prob.variables.get_upper_bounds(Ulist[6]*numT+QI_c)*9.0*0.01
    # print "QI-RF-MIN : ", prob.variables.get_lower_bounds(Ulist[7] * numT + QI_c), " = ", \
    #     prob.variables.get_lower_bounds(Ulist[0] * numT + QI_c) * 4.576 * 0.01," + ",\
    #     prob.variables.get_lower_bounds(Ulist[6]*numT+QI_c)*4.0*0.01
    # maxyield = []
    # for M in Mlist[0:4]:
    #     maxyield.append(Yield[Ulist[4] * numM * numS + M * numS + Slist[0]])   # from Ulist[4]-HDS-S0
    # prob.variables.set_upper_bounds(zip(range(Ulist[3]*numT+QI_c,Ulist[3]*numT+numT+QI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[4]*numT+QI_c)*max(maxyield)*0.01]*numT)) # set QI-Ulist[3]-ETH-max
    # prob.variables.set_upper_bounds(zip(range(OClist[3]*numT+OC_c,OClist[3]*numT+numT+OC_c),
    #                 [prob.variables.get_upper_bounds(Ulist[4]*numT+QI_c)*max(maxyield)*0.01-5.0]*numT)) # set OC[3]-HDS-max
    # prob.variables.set_lower_bounds(zip(range(Ulist[3]*numT+QI_c,Ulist[3]*numT+numT+QI_c),
    #                 [5.0]*numT))                                                                     # set QI-Ulist[3]-ETH-min
    # prob.variables.set_lower_bounds(zip(range(OClist[3]*numT+OC_c,OClist[3]*numT+numT+OC_c),
    #                 [0.0]*numT))                                                                     # set OC[3]-HDS-min
    # prob.variables.set_upper_bounds(zip(range(Ulist[3]*numM*numM*numT+xQI_c,Ulist[4]*numM*numM*numT+xQI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[3]*numT+QI_c)]*numM*numM*numT)) # set xQI-Ulist[3]-ETH-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[3]*numM*numM*numT+xQI1_c,Ulist[4]*numM*numM*numT+xQI1_c),
    #                 [prob.variables.get_upper_bounds(Ulist[3]*numT+QI_c)]*numM*numM*numT)) # set xQI1-Ulist[3]-ETH-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[3]*numM*numT+xyQI_c,Ulist[4]*numM*numT+xyQI_c),
    #                 [prob.variables.get_upper_bounds(Ulist[3]*numT+QI_c)]*numM*numT)) # set xQI-Ulist[3]-ETH-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[3]*numM*numT+xyQI1_c,Ulist[4]*numM*numT+xyQI1_c),
    #                 [prob.variables.get_upper_bounds(Ulist[3]*numT+QI_c)]*numM*numT)) # set xQI1-Ulist[3]-ETH-max
    # print "QI-ETH-MAX : ", prob.variables.get_upper_bounds(Ulist[3] * numT + QI_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[4] * numT + QI_c) * 97.0 * 0.01
    # print "QI-ETH-MIN : ", prob.variables.get_lower_bounds(Ulist[3] * numT + QI_c), " = ", 5.0
    # print "xQI-ETH-MAX : ", prob.variables.get_upper_bounds(Ulist[3] * numM * numM * numT + xQI_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[3] * numT + QI_c)
    # print "xQI1-ETH-MAX : ", prob.variables.get_upper_bounds(Ulist[3] * numM * numM * numT + xQI1_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[3] * numT + QI_c)
    # print "xyQI-ETH-MAX : ", prob.variables.get_upper_bounds(Ulist[3] * numM * numT + xyQI_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[3] * numT + QI_c)
    # print "xyQI1-ETH-MAX : ", prob.variables.get_upper_bounds(Ulist[3] * numM * numT + xyQI1_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[3] * numT + QI_c)
    # print "OC-HDS-MAX : ", prob.variables.get_upper_bounds(OClist[3] * numT + OC_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[4] * numT + QI_c) * 97.0 * 0.01, " - ", 5.0
    # # =========================================== Set QO Conponent Oil Bound ===============================
    # maxyield1 = []
    # maxyield2 = []
    # for M in [Mlist[0]]:
    #     maxyield1.append(Yield[Ulist[7] * numM * numS + M * numS + Slist[0]])
    #     maxyield2.append(Yield[Ulist[7] * numM * numS + M * numS + Slist[1]])
    # prob.variables.set_upper_bounds(zip(range(Ulist[7]*numS*numT+Slist[0]*numT+QO_c,
    #                                           Ulist[7]*numS*numT+Slist[0]*numT+numT+QO_c),
    #                 [prob.variables.get_upper_bounds(Ulist[7]*numT+QI_c)*max(maxyield1)*0.01]*numT)) # set QO-U[7]-S1-C5-max
    # prob.variables.set_upper_bounds(zip(range(Ulist[7]*numS*numT+Slist[1]*numT+QO_c,
    #                                           Ulist[7]*numS*numT+Slist[1]*numT+numT+QO_c),
    #                 [prob.variables.get_upper_bounds(Ulist[7]*numT+QI_c)*max(maxyield2)*0.01]*numT)) # set QO-U[7]-S2-Reformate-max
    # prob.variables.set_lower_bounds(zip(range(Ulist[7]*numS*numT+Slist[0]*numT+QO_c,
    #                                           Ulist[7]*numS*numT+Slist[0]*numT+numT+QO_c),
    #                 [prob.variables.get_lower_bounds(Ulist[7]*numT+QI_c)*min(maxyield1)*0.01]*numT)) # set QO-U[7]-S1-C5-min
    # prob.variables.set_lower_bounds(zip(range(Ulist[7]*numS*numT+Slist[1]*numT+QO_c,
    #                                           Ulist[7]*numS*numT+Slist[1]*numT+numT+QO_c),
    #                 [prob.variables.get_lower_bounds(Ulist[7]*numT+QI_c)*min(maxyield2)*0.01]*numT)) # set QO-U[7]-S2-Reformate-min
    # print "QO-U[7]-S1-C5-MAX : ", prob.variables.get_upper_bounds(Ulist[7] *numS* numT+Slist[0]*numT + QO_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[7] * numT + QI_c) * 10.0 * 0.01
    # print "QO-U[7]-S1-C5-MIN : ", prob.variables.get_lower_bounds(Ulist[7] *numS* numT+Slist[0]*numT + QO_c), " = ", \
    #     prob.variables.get_lower_bounds(Ulist[7] * numT + QI_c) * 10.0 * 0.01
    # print "QO-U[7]-S2-Reformate-MAX : ", prob.variables.get_upper_bounds(Ulist[7] *numS* numT+Slist[1]*numT + QO_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[7] * numT + QI_c) * 90.0 * 0.01
    # print "QO-U[7]-S2-Reformate-MIN : ", prob.variables.get_lower_bounds(Ulist[7] *numS* numT+Slist[1]*numT + QO_c), " = ", \
    #     prob.variables.get_lower_bounds(Ulist[7] * numT + QI_c) * 90.0 * 0.01
    # prob.variables.set_upper_bounds(zip(range(Ulist[8]*numS*numT+Slist[0]*numT+QO_c,
    #                                           Ulist[8]*numS*numT+Slist[0]*numT+numT+QO_c),
    #                 [prob.variables.get_upper_bounds(Ulist[8]*numT+QI_c)*Yield[Ulist[8]*numM*numS+Mlist[0]*numS+Slist[0]]
    #                  * 0.01]*numT))                                                       # set QO-U[8]-S1-MTBE-max
    # prob.variables.set_lower_bounds(zip(range(Ulist[8]*numS*numT+Slist[0]*numT+QO_c,
    #                                           Ulist[8]*numS*numT+Slist[0]*numT+numT+QO_c),
    #                 [prob.variables.get_lower_bounds(Ulist[8]*numT+QI_c)*Yield[Ulist[8]*numM*numS+Mlist[0]*numS+Slist[0]]
    #                  * 0.01]*numT))                                                       # set QO-U[8]-S1-MTBE-min
    # print "QO-U[8]-S1-MTBE-MAX : ", prob.variables.get_upper_bounds(Ulist[8]*numS * numT+Slist[0]*numT + QO_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[8] * numT + QI_c) * MTBE120or110 * 0.01
    # print "QO-U[8]-S1-MTBE-MIN : ", prob.variables.get_lower_bounds(Ulist[8]*numS * numT+Slist[0]*numT + QO_c), " = ", \
    #     prob.variables.get_lower_bounds(Ulist[8] * numT + QI_c) * MTBE120or110 * 0.01
    # maxyield = []
    # for M in Mlist[0:4]:
    #     maxyield.append(Yield[Ulist[3] * numM * numS + M * numS + Slist[0]])    #  form Ulist[3]-ETH-S1
    # prob.variables.set_upper_bounds(zip(range(Ulist[3]*numS*numT+Slist[0]*numT+QO_c,
    #                                           Ulist[3]*numS*numT+Slist[0]*numT+numT+QO_c),
    #                 [prob.variables.get_upper_bounds(Ulist[3]*numT+QI_c)*max(maxyield)*0.01]*numT)) # set QO-U[3]-S1-Etherified-max
    # prob.variables.set_lower_bounds(zip(range(Ulist[3]*numS*numT+Slist[0]*numT+QO_c,
    #                                           Ulist[3]*numS*numT+Slist[0]*numT+numT+QO_c),
    #                 [prob.variables.get_lower_bounds(Ulist[3]*numT+QI_c)*min(maxyield)*0.01]*numT)) # set QO-U[3]-S1-Etherified-min
    # print "QO-U[3]-S1-Etherified-MAX : ", prob.variables.get_upper_bounds(Ulist[3]*numS * numT+Slist[0]*numT + QO_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[3] * numT + QI_c) * 98.1 * 0.01
    # print "QO-U[3]-S1-Etherified-MIN : ", prob.variables.get_lower_bounds(Ulist[3]*numS * numT+Slist[0]*numT + QO_c), " = ", \
    #     prob.variables.get_lower_bounds(Ulist[3] * numT + QI_c) * 90.0 * 0.01
    # maxyield = []
    # for M in Mlist[0:2]:
    #     maxyield.append(Yield[Ulist[6] * numM * numS + M * numS + Slist[1]])    #  form Ulist[6]-HTU2-S2
    # prob.variables.set_upper_bounds(zip(range(Ulist[6]*numS*numT+Slist[1]*numT+QO_c,
    #                                           Ulist[6]*numS*numT+Slist[1]*numT+numT+QO_c),
    #                 [prob.variables.get_upper_bounds(Ulist[6]*numT+QI_c)*max(maxyield)*0.01]*numT)) # set QO-U[6]-diesel2-max
    # prob.variables.set_lower_bounds(zip(range(Ulist[6]*numS*numT+Slist[1]*numT+QO_c,
    #                                           Ulist[6]*numS*numT+Slist[1]*numT+numT+QO_c),
    #                 [prob.variables.get_lower_bounds(Ulist[6]*numT+QI_c)*min(maxyield)*0.01]*numT)) # set QO-U[6]-diesel2-min
    # print "QO-U[6]-S2-diesel2-MAX : ", prob.variables.get_upper_bounds(Ulist[6] * numS * numT+Slist[1]*numT + QO_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[6] * numT + QI_c) * 93.0 * 0.01
    # print "QO-U[6]-S2-diesel2-MIN : ", prob.variables.get_lower_bounds(Ulist[6] * numS * numT+Slist[1]*numT + QO_c), " = ", \
    #     prob.variables.get_lower_bounds(Ulist[6] * numT + QI_c) * 89.0 * 0.01
    # maxyield = []
    # for M in Mlist[0:2]:
    #     maxyield.append(Yield[Ulist[5] * numM * numS + M * numS + Slist[0]])    #  form Ulist[5]-HTU1-S1
    # prob.variables.set_upper_bounds(zip(range(Ulist[5]*numS*numT+Slist[0]*numT+QO_c,
    #                                           Ulist[5]*numS*numT+Slist[0]*numT+numT+QO_c),
    #                 [prob.variables.get_upper_bounds(Ulist[5]*numT+QI_c)*max(maxyield)*0.01]*numT)) # set QO-U[5]-diesel1-max
    # prob.variables.set_lower_bounds(zip(range(Ulist[5]*numS*numT+Slist[0]*numT+QO_c,
    #                                           Ulist[5]*numS*numT+Slist[0]*numT+numT+QO_c),
    #                 [prob.variables.get_lower_bounds(Ulist[5]*numT+QI_c)*min(maxyield)*0.01]*numT)) # set QO-U[5]-diesel1-min
    # print "QO-U[5]-S1-diesel1-MAX : ", prob.variables.get_upper_bounds(Ulist[5] * numS * numT+Slist[0]*numT + QO_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[5] * numT + QI_c) * 99.4 * 0.01
    # print "QO-U[5]-S1-diesel1-MIN : ", prob.variables.get_lower_bounds(Ulist[5] * numS * numT+Slist[0]*numT + QO_c), " = ", \
    #     prob.variables.get_lower_bounds(Ulist[5] * numT + QI_c) * 99.4 * 0.01
    #
    # # =========================================== Set OCINV Tank Bound ===============================
    # prob.variables.set_upper_bounds(zip(range(OClist[0]*numT+OCINV_c,OClist[0]*numT+numT+OCINV_c),  # set OClist[0]-C5-max
    #                 [prob.variables.get_upper_bounds(Ulist[7]*numS*numT+Slist[0]*numT+QO_c)*hours*invC_multi_flow]*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[1]*numT+OCINV_c,OClist[1]*numT+numT+OCINV_c),  # set OClist[1]-Reformate-max
    #                 [prob.variables.get_upper_bounds(Ulist[7]*numS*numT+Slist[1]*numT+QO_c)*hours*invC_multi_flow]*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[2]*numT+OCINV_c,OClist[2]*numT+numT+OCINV_c),  # set OClist[2]-MTBE-max
    #                 [prob.variables.get_upper_bounds(Ulist[8]*numS*numT+Slist[0]*numT+QO_c)*hours*invC_multi_flow]*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[3]*numT+OCINV_c,OClist[3]*numT+numT+OCINV_c),  # set OClist[3]-HDS-max
    #                 [prob.variables.get_upper_bounds(OClist[3]*numT+OC_c)*hours*invC_multi_flow]*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[4]*numT+OCINV_c,OClist[4]*numT+numT+OCINV_c),  # set OClist[4]-Ether-max
    #                 [prob.variables.get_upper_bounds(Ulist[3]*numS*numT+Slist[0]*numT+QO_c)*hours*invC_multi_flow]*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[5]*numT+OCINV_c,OClist[5]*numT+numT+OCINV_c),  # set OClist[5]-diesel1-max
    #                 [prob.variables.get_upper_bounds(Ulist[5]*numS*numT+Slist[0]*numT+QO_c)*hours*invC_multi_flow]*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[6]*numT+OCINV_c,OClist[6]*numT+numT+OCINV_c),  # set OClist[6]-diesel2-max
    #                 [prob.variables.get_upper_bounds(Ulist[6]*numS*numT+Slist[1]*numT+QO_c)*hours*invC_multi_flow]*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[7]*numT+OCINV_c,OClist[7]*numT+numT+OCINV_c),  # set OClist[7]-Light-max
    #                 [prob.variables.get_upper_bounds(OClist[7]*numT+OC_c)*hours*invC_multi_flow]*numT))
    # print "tank[0]-C5-max : ", prob.variables.get_upper_bounds(OClist[0] * numT+ OCINV_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[7] * numS * numT +Slist[0]*numT + QO_c)," * ",hours," * ",invC_multi_flow
    # print "tank[1]-Reformate-max : ", prob.variables.get_upper_bounds(OClist[1] * numT+ OCINV_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[7] * numS * numT +Slist[1]*numT + QO_c)," * ",hours," * ",invC_multi_flow
    # print "tank[2]-MTBE-max : ", prob.variables.get_upper_bounds(OClist[2] * numT+ OCINV_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[8] * numS * numT +Slist[0]*numT + QO_c)," * ",hours," * ",invC_multi_flow
    # print "tank[3]-HDS-max : ", prob.variables.get_upper_bounds(OClist[3] * numT+ OCINV_c), " = ", \
    #     prob.variables.get_upper_bounds(OClist[3] * numT + OC_c)," * ",hours," * ",invC_multi_flow
    # print "tank[4]-Ether-max : ", prob.variables.get_upper_bounds(OClist[4] * numT+ OCINV_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[3] * numS * numT +Slist[0]*numT + QO_c)," * ",hours," * ",invC_multi_flow
    # print "tank[5]-diesel1-max : ", prob.variables.get_upper_bounds(OClist[5] * numT+ OCINV_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[5] * numS * numT +Slist[0]*numT + QO_c)," * ",hours," * ",invC_multi_flow
    # print "tank[6]-diesel2-max : ", prob.variables.get_upper_bounds(OClist[6] * numT+ OCINV_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[6] * numS * numT +Slist[1]*numT + QO_c)," * ",hours," * ",invC_multi_flow
    # print "tank[7]-Light-max : ", prob.variables.get_upper_bounds(OClist[7] * numT+ OCINV_c), " = ", \
    #     prob.variables.get_upper_bounds(OClist[7] * numT + OC_c)," * ",hours," * ",invC_multi_flow
    # # =========================================== Set OCINVint Tank Bound ===============================
    # # This is not need. because OCINVint(T) = OCINV(T-1)
    # # =========================================== Set OCtankout Bound ===============================
    # prob.variables.set_upper_bounds(zip(range(OClist[0]*numT+OCtankout_c,OClist[0]*numT+numT+OCtankout_c),  # set OClist[0]-C5-max
    #                 [prob.variables.get_upper_bounds(Ulist[7]*numS*numT+Slist[0]*numT+QO_c)]*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[1]*numT+OCtankout_c,OClist[1]*numT+numT+OCtankout_c),  # set OClist[1]-Reformate-max
    #                 [prob.variables.get_upper_bounds(Ulist[7]*numS*numT+Slist[1]*numT+QO_c)]*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[2]*numT+OCtankout_c,OClist[2]*numT+numT+OCtankout_c),  # set OClist[2]-MTBE-max
    #                 [prob.variables.get_upper_bounds(Ulist[8]*numS*numT+Slist[0]*numT+QO_c)]*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[3]*numT+OCtankout_c,OClist[3]*numT+numT+OCtankout_c),  # set OClist[3]-HDS-max
    #                 [prob.variables.get_upper_bounds(OClist[3]*numT+OC_c)]*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[4]*numT+OCtankout_c,OClist[4]*numT+numT+OCtankout_c),  # set OClist[4]-Ether-max
    #                 [prob.variables.get_upper_bounds(Ulist[3]*numS*numT+Slist[0]*numT+QO_c)]*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[5]*numT+OCtankout_c,OClist[5]*numT+numT+OCtankout_c),  # set OClist[5]-diesel1-max
    #                 [prob.variables.get_upper_bounds(Ulist[5]*numS*numT+Slist[0]*numT+QO_c)]*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[6]*numT+OCtankout_c,OClist[6]*numT+numT+OCtankout_c),  # set OClist[6]-diesel2-max
    #                 [prob.variables.get_upper_bounds(Ulist[6]*numS*numT+Slist[1]*numT+QO_c)]*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[7]*numT+OCtankout_c,OClist[7]*numT+numT+OCtankout_c),  # set OClist[7]-Light-max
    #                 [prob.variables.get_upper_bounds(OClist[7]*numT+OC_c)]*numT))
    # print "OCtankout[0]-C5-max : ", prob.variables.get_upper_bounds(OClist[0] * numT+ OCtankout_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[7] * numS * numT +Slist[0]*numT + QO_c)
    # print "OCtankout[1]-Reformate-max : ", prob.variables.get_upper_bounds(OClist[1] * numT+ OCtankout_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[7] * numS * numT +Slist[1]*numT + QO_c)
    # print "OCtankout[2]-MTBE-max : ", prob.variables.get_upper_bounds(OClist[2] * numT+ OCtankout_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[8] * numS * numT +Slist[0]*numT + QO_c)
    # print "OCtankout[3]-HDS-max : ", prob.variables.get_upper_bounds(OClist[3] * numT+ OCtankout_c), " = ", \
    #     prob.variables.get_upper_bounds(OClist[3] * numT + OC_c)
    # print "OCtankout[4]-Ether-max : ", prob.variables.get_upper_bounds(OClist[4] * numT+ OCtankout_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[3] * numS * numT +Slist[0]*numT + QO_c)
    # print "OCtankout[5]-diesel1-max : ", prob.variables.get_upper_bounds(OClist[5] * numT+ OCtankout_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[5] * numS * numT +Slist[0]*numT + QO_c)
    # print "OCtankout[6]-diesel2-max : ", prob.variables.get_upper_bounds(OClist[6] * numT+ OCtankout_c), " = ", \
    #     prob.variables.get_upper_bounds(Ulist[6] * numS * numT +Slist[1]*numT + QO_c)
    # print "OCtankout[7]-Light-max : ", prob.variables.get_upper_bounds(OClist[7] * numT+ OCtankout_c), " = ", \
    #     prob.variables.get_upper_bounds(OClist[7] * numT + OC_c)
    # # =========================================== Set Q Bound ===============================
    # prob.variables.set_upper_bounds(zip(range(OClist[0]*numO*numT+Q_c,OClist[1]*numO*numT+Q_c),  # set OClist[0]-C5-max
    #                 [prob.variables.get_upper_bounds(OClist[0]*numT+OCtankout_c)]*numO*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[1]*numO*numT+Q_c,OClist[2]*numO*numT+Q_c),  # set OClist[1]-Reformate-max
    #                 [prob.variables.get_upper_bounds(OClist[1]*numT+OCtankout_c)]*numO*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[2]*numO*numT+Q_c,OClist[3]*numO*numT+Q_c),  # set OClist[2]-MTBE-max
    #                 [prob.variables.get_upper_bounds(OClist[2]*numT+OCtankout_c)]*numO*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[3]*numO*numT+Q_c,OClist[4]*numO*numT+Q_c),  # set OClist[3]-HDS-max
    #                 [prob.variables.get_upper_bounds(OClist[3]*numT+OCtankout_c)]*numO*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[4]*numO*numT+Q_c,OClist[5]*numO*numT+Q_c),  # set OClist[4]-Ether-max
    #                 [prob.variables.get_upper_bounds(OClist[4]*numT+OCtankout_c)]*numO*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[5]*numO*numT+Q_c,OClist[6]*numO*numT+Q_c),  # set OClist[5]-diesel1-max
    #                 [prob.variables.get_upper_bounds(OClist[5]*numT+OCtankout_c)]*numO*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[6]*numO*numT+Q_c,OClist[7]*numO*numT+Q_c),  # set OClist[6]-diesel2-max
    #                 [prob.variables.get_upper_bounds(OClist[6]*numT+OCtankout_c)]*numO*numT))
    # prob.variables.set_upper_bounds(zip(range(OClist[7]*numO*numT+Q_c,Qcount+Q_c),               # set OClist[7]-Light-max
    #                 [prob.variables.get_upper_bounds(OClist[7]*numT+OCtankout_c)]*numO*numT))
    # print "Q[0]-C5-max : ", prob.variables.get_upper_bounds(OClist[0]*numO * numT+ Q_c), " = ", \
    #     prob.variables.get_upper_bounds(OClist[0] * numT  + OCtankout_c)
    # print "Q[1]-Reformate-max : ", prob.variables.get_upper_bounds(OClist[1] * numO * numT + Q_c), " = ", \
    #     prob.variables.get_upper_bounds(OClist[1] * numT + OCtankout_c)
    # print "Q[2]-MTBE-max : ", prob.variables.get_upper_bounds(OClist[2] * numO * numT + Q_c), " = ", \
    #     prob.variables.get_upper_bounds(OClist[2] * numT + OCtankout_c)
    # print "Q[3]-HDS-max : ", prob.variables.get_upper_bounds(OClist[3] * numO * numT + Q_c), " = ", \
    #     prob.variables.get_upper_bounds(OClist[3] * numT + OCtankout_c)
    # print "Q[4]-Ether-max : ", prob.variables.get_upper_bounds(OClist[4] * numO * numT + Q_c), " = ", \
    #     prob.variables.get_upper_bounds(OClist[4] * numT + OCtankout_c)
    # print "Q[5]-diesel1-max : ", prob.variables.get_upper_bounds(OClist[5] * numO * numT + Q_c), " = ", \
    #     prob.variables.get_upper_bounds(OClist[5] * numT + OCtankout_c)
    # print "Q[6]-diesel2-max : ", prob.variables.get_upper_bounds(OClist[6] * numO * numT + Q_c), " = ", \
    #     prob.variables.get_upper_bounds(OClist[6] * numT + OCtankout_c)
    # print "Q[7]-Light-max : ", prob.variables.get_upper_bounds(OClist[7] * numO * numT + Q_c), " = ", \
    #     prob.variables.get_upper_bounds(OClist[7] * numT + OCtankout_c)


    return [y_c,ycount,x_c,xcount,xycount,xy_c,QI_c,QIcount,QO_c,QOcount,Otankout_c,Otankoutcount,Q_c,Qcount,OINV_c,OINVcount,
            xQI_c,xQIcount,xQI1_c,xQI1count,xyQI_c,xyQIcount,xyQI1_c,xyQI1count,OCcount,OC_c,OCINVcount,OCINV_c,
            OCtankoutcount,OCtankout_c]

def refinery(numT, Tlist, numL, Llist, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode):
    #,QI_atm,QI_eth,QI_htu1
    prob = cplex.Cplex()
    # prob.parameters.barrier.qcpconvergetol.set(1e-10)
    prob.parameters.mip.tolerances.mipgap.set(0.0)
    prob.parameters.timelimit.set(50)
    [y_c,ycount,x_c,xcount,xycount,xy_c,QI_c,QIcount,QO_c,QOcount,Otankout_c,Otankoutcount,Q_c,Qcount,OINV_c,OINVcount,
            xQI_c,xQIcount,xQI1_c,xQI1count,xyQI_c,xyQIcount,xyQI1_c,xyQI1count,OCcount,OC_c,OCINVcount,OCINV_c,
            OCtankoutcount,OCtankout_c] = buildmodel(prob,
                                    numT, Tlist, numL, Llist, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode)
    # prob.write("refinery.lp")
    # global nn
    # class TimeLimitCallback(MIPInfoCallback):
    #     def __call__(self):
    #         # if not self.aborted and self.has_incumbent():
    #         nn = 100.0 * self.get_MIP_relative_gap()
    #             # timeused = self.get_time() - self.starttime
    #             # if timeused > self.timelimit and gap < self.acceptablegap:
    #         print "sec., gap =", nn

    # timelim_cb = prob.register_callback(TimeLimitCallback)
    prob.solve()
    sol = prob.solution
    print
    # solution.get_status() returns an integer code
    print "Solution status = ", sol.get_status(), ":",
    # the following line prints the corresponding string
    print sol.status[sol.get_status()]
    # a = 0
    # for L in Llist:
    #    for O in Olist:
    #        a += DV1[L * numO + O]
    print "Solution value  = ", sol.get_objective_value()
    # print sum(sum(DV1)) * bp, "\n"  + sum(sum(DV1[:numL])) * bp
    print "Banery number = ", prob.variables.get_num_binary()
    # the following line prints the corresponding string
    print "Variable number = ", prob.variables.get_num()
    print "Contraint number = ", prob.linear_constraints.get_num(), "\n"
    QI = sol.get_values(QI_c, QI_c + QIcount - 1)
    # print "nn:",nn
    # prob.register_callback(MIPInfoCallback)
    # M: numU*numM*numT
    M = sol.get_values(y_c, y_c + ycount - 1)
    # print "Mode = ",M
    header = Tlist[:]
    M_header = header[:]
    M_header.insert(0, "M")
    M_table_ = [0] * (numT + 1)
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
        for T in Tlist:
            for Mode in Mlist:
                if M[U * numM * numT + Mode * numT + T] >= 0.1:
                    M_table[U][T + 1] = Mode
                    break
                elif Mode == 3:
                    M_table[U][T + 1] = "N/A"
    print tabulate(M_table, M_header, tablefmt="simple", numalign="center", floatfmt=".1f")

    # MT: numU*numM*numM*numT
    MT = sol.get_values(x_c, x_c + xcount - 1)
    MT_header = header[:]
    MT_header.insert(0, "MT")
    MT_table_ = [0] * (numT + 1)
    MT_table = []
    for U in Ulist:
        MT_table.append(MT_table_[:])
    # print "Unit Mode:  "
    # MT_table[0][0] = "ATM"
    # MT_table[1][0] = "VDU"
    # MT_table[2][0] = "FCCU"
    # MT_table[3][0] = "ETH"
    # MT_table[4][0] = "HDS"
    # MT_table[5][0] = "HTU1"
    # MT_table[6][0] = "HTU2"
    # MT_table[7][0] = "RF"
    # MT_table[8][0] = "MTBE"
    # for U in Ulist:
    #     for T in Tlist:
    #         AS = None
    #         for Mode in Mlist:
    #             for Mode_ in Mlist:
    #                 if MT[U * numM * numM * numT + Mode_ * numM * numT + Mode * numT + T] >= 0.1:
    #                     AS = str(Mode_) + "-" + str(Mode)
    #                     break
    #             if AS != None:
    #                 MT_table[U][T + 1] = AS
    #                 break
    #             elif Mode == 3:
    #                 MT_table[U][T + 1] = "N/A"
    # print tabulate(MT_table, MT_header, tablefmt="simple", numalign="center", floatfmt=".1f")
    # M: numU*numM*numT
    M = sol.get_values(xy_c, xy_c + xycount - 1)
    header = Tlist[:]
    M_header = header[:]
    M_header.insert(0, "xy")
    M_table_ = [0] * (numT + 1)
    M_table = []
    for U in Ulist[0:9]:
        M_table.append(M_table_[:])
    # print "Unit Mode:  "
    # M_table[0][0] = "ATM"
    # M_table[1][0] = "VDU"
    # M_table[2][0] = "FCCU"
    # M_table[3][0] = "ETH"
    # M_table[4][0] = "HDS"
    # M_table[5][0] = "HTU1"
    # M_table[6][0] = "HTU2"
    # M_table[7][0] = "RF"
    # M_table[8][0] = "MTBE"
    # for U in Ulist[0:9]:
    #     for T in Tlist:
    #         for Mode in Mlist:
    #             if M[U * numM * numT + Mode * numT + T] >= 0.1:
    #                 M_table[U][T + 1] = Mode
    #                 break
    #             elif Mode == 3:
    #                 M_table[U][T + 1] = "N/A"
    # print tabulate(M_table, M_header, tablefmt="simple", numalign="center", floatfmt=".1f")

    M = sol.get_values(y_c, y_c + ycount - 1)
    header = Tlist[:]
    M_header = header[:]
    M_header.insert(0, "M")
    M_table_ = [0] * (numT + 1)
    M_table = []
    for U in Ulist[0:9]:
        M_table.append(M_table_[:])
    # print "Unit Mode:  "
    # M_table[0][0] = "ATM"
    # M_table[1][0] = "VDU"
    # M_table[2][0] = "FCCU"
    # M_table[3][0] = "ETH"
    # M_table[4][0] = "HDS"
    # M_table[5][0] = "HTU1"
    # M_table[6][0] = "HTU2"
    # M_table[7][0] = "RF"
    # M_table[8][0] = "MTBE"
    # for U in Ulist[0:9]:
    #     for T in Tlist:
    #         b = []
    #         for Mode in Mlist:
    #             b.append(round(M[U * numM * numT + Mode * numT + T],1))
    #         M_table[U][T + 1] = b
    # print tabulate(M_table, M_header, tablefmt="simple", numalign="center", floatfmt=".1f")
    M = sol.get_values(xy_c, xy_c + xycount - 1)
    header = Tlist[:]
    M_header = header[:]
    M_header.insert(0, "xy")
    M_table_ = [0] * (numT + 1)
    M_table = []
    for U in Ulist[0:9]:
        M_table.append(M_table_[:])
    # print "Unit Mode:  "
    # M_table[0][0] = "ATM"
    # M_table[1][0] = "VDU"
    # M_table[2][0] = "FCCU"
    # M_table[3][0] = "ETH"
    # M_table[4][0] = "HDS"
    # M_table[5][0] = "HTU1"
    # M_table[6][0] = "HTU2"
    # M_table[7][0] = "RF"
    # M_table[8][0] = "MTBE"
    # for U in Ulist[0:9]:
    #     for T in Tlist:
    #         b = []
    #         for Mode in Mlist:
    #             b.append(round(M[U * numM * numT + Mode * numT + T],1))
    #         M_table[U][T + 1] = b
    # print tabulate(M_table, M_header, tablefmt="simple", numalign="center", floatfmt=".1f")
    # FUin: numU*numT
    FinM = sol.get_values(QI_c, QI_c + QIcount - 1)
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
        for T in Tlist:
            FUin_table[U][T + 1] = FinM[U * numT + T]
    print tabulate(FUin_table, FUin_header, tablefmt="simple", numalign="center", floatfmt=".6f")
    # QO: numU*numS*numT
    QO = sol.get_values(QO_c, QO_c + QOcount - 1)
    QO_header = header[:]
    QO_header.insert(0, "QO")
    QO_table_ = [0] * (numT + 1)
    QO_table = []
    for U in Ulist[0:9]:
        QO_table.append(QO_table_[:])
    # print "Unit Input Flowrate:  "
    # QO_table[0][0] = "ATM"
    # QO_table[1][0] = "VDU"
    # QO_table[2][0] = "FCCU"
    # QO_table[3][0] = "ETH"
    # QO_table[4][0] = "HDS"
    # QO_table[5][0] = "HTU1"
    # QO_table[6][0] = "HTU2"
    # QO_table[7][0] = "RF"
    # QO_table[8][0] = "MTBE"
    # for U in Ulist[0:9]:
    #     for T in Tlist:
    #         sa =[]
    #         for S in Slist:
    #             sa.append(round(QO[U * numS * numT + S * numT + T],6))
    #         QO_table[U][T + 1] = sa
    # print tabulate(QO_table, QO_header, tablefmt="simple", numalign="center", floatfmt=".6f")
    # Print Fout
    M = sol.get_values(y_c, y_c + ycount - 1)
    MT = sol.get_values(x_c, x_c + xcount - 1)
    OC = sol.get_values(OC_c, OC_c + OCcount - 1)
    Fout_header = header[:]
    Fout_header.insert(0, "Fout")
    Fout_table_ = [0] * (numT + 1)
    Fout_table = []
    for U in range(11):
        Fout_table.append(Fout_table_[:])
    # print "Output flowrate of Units:  "
    # Fout_table[0][0] = "ATM"
    # Fout_table[1][0] = "VDU"
    # Fout_table[2][0] = "FCCU"
    # Fout_table[3][0] = "ETH"
    # Fout_table[4][0] = "HDS"
    # Fout_table[5][0] = "HTU1"
    # Fout_table[6][0] = "HTU2"
    # Fout_table[7][0] = "RF"
    # Fout_table[8][0] = "MTBE"
    # Fout_table[9][0] = "Fen1"
    # Fout_table[10][0] = "Fen2"
    # for U in [Ulist[0], Ulist[1], ]:
    #     for T in Tlist:
    #         S_all = []
    #         for S in Slist:
    #             Y = 0
    #             for Mode in Mlist[:2]:
    #                 for Mode_ in Mlist[:2]:
    #                     if MT[U * numM * numM * numT + Mode_ * numM * numT + Mode * numT + T] >= 0.1:
    #                         Y = tYield[U * numM * numM * numS + Mode_ * numM * numS + Mode * numS + S]
    #                         break
    #                 if Y == 0 and M[U * numM * numT + Mode * numT + T] >= 0.1:
    #                     Y = Yield[U * numM * numS + Mode * numS + S]
    #                     break
    #             S_all.append(round(FUin_table[U][T + 1] * Y * 0.01, 6))
    #         Fout_table[U][T + 1] = S_all
    # for U in [Ulist[2], Ulist[3], Ulist[4]]:
    #     for T in Tlist:
    #         S_all = []
    #         for S in Slist:
    #             Y = 0
    #             for Mode in Mlist:
    #                 for Mode_ in Mlist:
    #                     if MT[U * numM * numM * numT + Mode_ * numM * numT + Mode * numT + T] >= 0.1:
    #                         Y = tYield[U * numM * numM * numS + Mode_ * numM * numS + Mode * numS + S]
    #                         break
    #                 if Y == 0 and M[U * numM * numT + Mode * numT + T] >= 0.1:
    #                     Y = Yield[U * numM * numS + Mode * numS + S]
    #                     break
    #             S_all.append(round(FUin_table[U][T + 1] * Y * 0.01, 6))
    #         Fout_table[U][T + 1] = S_all
    # for U in [Ulist[5], Ulist[6]]:
    #     for T in Tlist:
    #         S_all = []
    #         for S in Slist:
    #             Y = 0
    #             for Mode in Mlist[:2]:
    #                 for Mode_ in Mlist[:2]:
    #                     if MT[U * numM * numM * numT + Mode_ * numM * numT + Mode * numT + T] >= 0.1:
    #                         Y = tYield[U * numM * numM * numS + Mode_ * numM * numS + Mode * numS + S]
    #                         break
    #                 if Y == 0 and M[U * numM * numT + Mode * numT + T] >= 0.1:
    #                     Y = Yield[U * numM * numS + Mode * numS + S]
    #                     break
    #             S_all.append(round(FUin_table[U][T + 1] * Y * 0.01, 6))
    #         Fout_table[U][T + 1] = S_all
    # for U in [Ulist[7], Ulist[8]]:
    #     for T in Tlist:
    #         S_all = []
    #         for S in Slist:
    #             S_all.append(round(FUin_table[U][T + 1] * Yield[U * numM * numS + 0 * numS + S] * 0.01, 6))
    #         Fout_table[U][T + 1] = S_all
    # for U in [9]:
    #     for T in Tlist:
    #         Fout_table[U][T + 1] = [round(OC[7 * numT + T], 6), round(FUin_table[5][T + 1], 3)]
    # for U in [10]:
    #     for T in Tlist:
    #         Fout_table[U][T + 1] = [round(OC[3 * numT + T], 6), round(FUin_table[3][T + 1], 3)]
    # print tabulate(Fout_table, Fout_header, tablefmt="simple", numalign="center", floatfmt=".1f")

    # FOout: numO*numL*numT
    Otankout = sol.get_values(Otankout_c, Otankout_c + Otankoutcount - 1)
    # print "Otankout = ", Otankout
    FOout_header = header[:]
    FOout_header.insert(0, "Otankout")
    FOout_table_ = [0] * (numT + 1)
    FOout_table = []
    for O in Olist:
        for L in range(numL):
            FOout_table.append(FOout_table_[:])
    # print "Flowrate of O to Order: "
    # for O in Olist:
    #     for L in range(numL):
    #         FOout_table[O * numL + L][0] = "O" + str(O) + " L" + str(L)
    #         for T in Tlist:
    #             FOout_table[O * numL + L][T + 1] = Otankout[O * numL * numT + L * numT + T]
    # print tabulate(FOout_table, FOout_header, tablefmt="simple", numalign="center", floatfmt=".3f")
    FOout = sol.get_values(Otankout_c, Otankout_c + Otankoutcount - 1)
    FOout_header = header[:]
    FOout_header.insert(0, "FOout")
    FOout_table_ = [0] * (numT + 1)
    FOout_table = []
    for L in Llist:
        FOout_table.append(FOout_table_[:])
    # print "Flowrate of O to Order: "
    # for L in range(numL):
    #     FOout_table[L][0] = " L" + str(L)
    #     for T in Tlist:
    #         g = []
    #         for O in Olist:
    #             g.append(round(FOout[O * numL * numT + L * numT + T], 1))
    #         FOout_table[L][T + 1] = g
    # print tabulate(FOout_table, FOout_header, tablefmt="simple", numalign="center", floatfmt=".3f")
    FOout_header = header[:]
    FOout_header.insert(0, "order left")
    FOout_table_ = [0] * (numT + 1)
    FOout_table = []
    for L in Llist:
        FOout_table.append(FOout_table_[:])
    # print "Flowrate of O to Order: "
    # FOout_sum = np.zeros((numO, numL))
    # for L in range(numL):
    #     FOout_table[L][0] = " L" + str(L)
    #     for T in Tlist:
    #         g = []
    #         for O in Olist:
    #             g.append(round(DV1[L][O] - FOout_sum[O, L], 1))
    #             FOout_sum[O, L] += FOout[O * numL * numT + L * numT + T]
    #         FOout_table[L][T + 1] = g
    # print tabulate(FOout_table, FOout_header, tablefmt="simple", numalign="center", floatfmt=".3f")

    # VO: numO*numT
    OCtankout = sol.get_values(OCtankout_c, OCtankout_c + OCtankoutcount - 1)
    VO_header = header[:]
    VO_header.insert(0, "OCtankout")
    VO_table_ = [0] * (numT + 1)
    VO_table = []
    for O in Olist:
        VO_table.append(VO_table_[:])
    # print "Output flowrate of OC: "
    # for O in Olist:
    #     VO_table[O][0] = "O" + str(O)
    #     for T in Tlist:
    #         VO_table[O][T + 1] = OCtankout[O * numT + T]
    # print tabulate(VO_table, VO_header, tablefmt="simple", numalign="center", floatfmt=".3f")

    # VOC: numOC*numT
    VOC = sol.get_values(OCINV_c, OCINV_c + OCINVcount - 1)
    # print "VOC = ",VOC
    VOC_header = header[:]
    VOC_header.insert(0, "VOC")
    VOC_table_ = [0] * (numT + 1)
    VOC_table = []
    for OC in OClist:
        VOC_table.append(VOC_table_[:])
    print "Volume of OC: "
    for OC in OClist:
        VOC_table[OC][0] = "OC" + str(OC)
        for T in Tlist:
            VOC_table[OC][T + 1] = VOC[OC * numT + T]
    print tabulate(VOC_table, VOC_header, tablefmt="simple", numalign="center", floatfmt=".6f")
    # print "VOC:", np.swapaxes(np.round(VOC, 2).reshape(numOC, numT), 0, 1).reshape((numOC*numT,)).tolist()

    # VO: numO*numT
    VO = sol.get_values(OINV_c, OINV_c + OINVcount - 1)
    # print "VO = ",VO
    VO_header = header[:]
    VO_header.insert(0, "VO")
    VO_table_ = [0] * (numT + 1)
    VO_table = []
    for O in Olist:
        VO_table.append(VO_table_[:])
    print "Volume of O: "
    for O in Olist:
        VO_table[O][0] = "O" + str(O)
        for T in Tlist:
            VO_table[O][T + 1] = VO[O * numT + T]
    print tabulate(VO_table, VO_header, tablefmt="simple", numalign="center", floatfmt=".3f")
    # print "VO:", np.swapaxes(np.round(VO, 2).reshape(numO, numT), 0, 1).reshape((numO*numT,)).tolist()
    # FOCO: numOC*numO*numT
    FOCO = sol.get_values(Q_c, Q_c + Qcount - 1)
    FOCO_header = header[:]
    FOCO_header.insert(0, "FOCO")
    FOCO_table_ = [0] * (numT + 1)
    FOCO_table = []
    for OC in OClist:
        for O in Olist:
            FOCO_table.append(FOCO_table_[:])
    # print "blending Flowrate of OC to O: "
    # for OC in OClist:
    #     for O in Olist:
    #         FOCO_table[OC * numO + O][0] = "OC" + str(OC) + " O" + str(O)
    #         for T in Tlist:
    #             FOCO_table[OC * numO + O][T + 1] = round(FOCO[OC * numO * numT + O * numT + T], 6)
    # print tabulate(FOCO_table, FOCO_header, tablefmt="simple", numalign="center", floatfmt=".6f")

    M = sol.get_values(xyQI_c, xyQI_c + xyQIcount - 1)
    header = Tlist[:]
    M_header = header[:]
    M_header.insert(0, "xyQI")
    M_table_ = [0] * (numT + 1)
    M_table = []
    for U in Ulist[0:9]:
        M_table.append(M_table_[:])
    # print "Unit Mode:  "
    # M_table[0][0] = "ATM"
    # M_table[1][0] = "VDU"
    # M_table[2][0] = "FCCU"
    # M_table[3][0] = "ETH"
    # M_table[4][0] = "HDS"
    # M_table[5][0] = "HTU1"
    # M_table[6][0] = "HTU2"
    # M_table[7][0] = "RF"
    # M_table[8][0] = "MTBE"
    # for U in Ulist[0:9]:
    #     for T in Tlist:
    #         b = []
    #         for Mode in Mlist:
    #             b.append(round(M[U * numM * numT + Mode * numT + T],6))
    #         M_table[U][T + 1] = b
    # print tabulate(M_table, M_header, tablefmt="simple", numalign="center", floatfmt=".6f")
    M = sol.get_values(xyQI1_c, xyQI1_c + xyQI1count - 1)
    header = Tlist[:]
    M_header = header[:]
    M_header.insert(0, "xyQI1")
    M_table_ = [0] * (numT + 1)
    M_table = []
    for U in Ulist[0:9]:
        M_table.append(M_table_[:])
    # print "Unit Mode:  "
    # M_table[0][0] = "ATM"
    # M_table[1][0] = "VDU"
    # M_table[2][0] = "FCCU"
    # M_table[3][0] = "ETH"
    # M_table[4][0] = "HDS"
    # M_table[5][0] = "HTU1"
    # M_table[6][0] = "HTU2"
    # M_table[7][0] = "RF"
    # M_table[8][0] = "MTBE"
    # for U in Ulist[0:9]:
    #     for T in Tlist:
    #         b = []
    #         for Mode in Mlist:
    #             b.append(round(M[U * numM * numT + Mode * numT + T],6))
    #         M_table[U][T + 1] = b
    # print tabulate(M_table, M_header, tablefmt="simple", numalign="center", floatfmt=".6f")

    M = sol.get_values(xQI_c,xQI_c+xQIcount-1)
    print "sum xQI:",sum(M)
    header = Tlist[:]
    M_header = header[:]
    M_header.insert(0, "xQI")
    M_table_ = [0] * (numT + 1)
    M_table = []
    for U in Ulist[0:9]:
        M_table.append(M_table_[:])
    # print "Unit Mode:  "
    # M_table[0][0] = "ATM"
    # M_table[1][0] = "VDU"
    # M_table[2][0] = "FCCU"
    # M_table[3][0] = "ETH"
    # M_table[4][0] = "HDS"
    # M_table[5][0] = "HTU1"
    # M_table[6][0] = "HTU2"
    # M_table[7][0] = "RF"
    # M_table[8][0] = "MTBE"
    # for U in Ulist[0:9]:
    #     for T in Tlist:
    #         for Mode in Mlist:
    #             for Mode1 in Mlist:
    #                 if M[U * numM * numM * numT + Mode1 * numM * numT + Mode * numT + T] > 0.001:
    #                     M_table[U][T + 1] = [Mode1,Mode,round(M[U * numM * numM * numT + Mode1 * numM * numT + Mode * numT + T],6)]
    # print tabulate(M_table, M_header, tablefmt="simple", numalign="center", floatfmt=".6f")
    M = sol.get_values(xQI1_c,xQI1_c+xQI1count-1)
    # print "sum xQI1:",sum(M)
    header = Tlist[:]
    M_header = header[:]
    M_header.insert(0, "xQI1")
    M_table_ = [0] * (numT + 1)
    M_table = []
    for U in Ulist[0:9]:
        M_table.append(M_table_[:])
    # print "Unit Mode:  "
    # M_table[0][0] = "ATM"
    # M_table[1][0] = "VDU"
    # M_table[2][0] = "FCCU"
    # M_table[3][0] = "ETH"
    # M_table[4][0] = "HDS"
    # M_table[5][0] = "HTU1"
    # M_table[6][0] = "HTU2"
    # M_table[7][0] = "RF"
    # M_table[8][0] = "MTBE"
    # for U in Ulist[0:9]:
    #     for T in Tlist:
    #         for Mode in Mlist:
    #             for Mode1 in Mlist:
    #                 if M[U * numM * numM * numT + Mode1 * numM * numT + Mode * numT + T] > 0.001:
    #                     M_table[U][T + 1] = [Mode1,Mode,round(M[U * numM * numM * numT + Mode1 * numM * numT + Mode * numT + T],6)]
    # print tabulate(M_table, M_header, tablefmt="simple", numalign="center", floatfmt=".6f")
    # PRO:numO*numT
    FOCO = sol.get_values(Q_c, Q_c + Qcount - 1)
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
            F_sum = sum([FOCO[OC * numO * numT + O * numT + T] for OC in OClist[0:5]])
            if F_sum >= 0.00001:
                PRO_table[O * 3 + 0][T + 1] = "[" + str(PROMAX[0 * numO + O]) + " " + str(PROMAX[2 * numO + O]) + "]"
                PRO_table[O * 3 + 1][T + 1] = "[" + str(round(
                    sum([FOCO[OC * numO * numT + O * numT + T] * PRO[0 * numOC + OC] for OC in OClist[0:5]]) / F_sum,
                    2)) + " " + \
                                              str(round(sum(
                                                  [FOCO[OC * numO * numT + O * numT + T] * PRO[2 * numOC + OC] for OC in
                                                   OClist[0:5]]) / F_sum, 4)) + "]"
                PRO_table[O * 3 + 2][T + 1] = "[" + str(PROMIN[0 * numO + O]) + " " + str(PROMIN[2 * numO + O]) + "]"
            # elif T != 0:
            #     PRO_table[O * 3 + 0][T + 1] = "[" + str(PROMAX[0 * numO + O]) + " " + str(PROMAX[2 * numO + O]) + "]"
            #     PRO_table[O * 3 + 1][T + 1] = PRO_table[O * 3 + 1][T]
            #     PRO_table[O * 3 + 2][T + 1] = "[" + str(PROMIN[0 * numO + O]) + " " + str(PROMIN[2 * numO + O]) + "]"
            else:
                PRO_table[O * 3 + 0][T + 1] = "[" + str(PROMAX[0 * numO + O]) + " " + str(PROMAX[2 * numO + O]) + "]"
                PRO_table[O * 3 + 1][T + 1] = "INI"
                PRO_table[O * 3 + 2][T + 1] = "[" + str(PROMIN[0 * numO + O]) + " " + str(PROMIN[2 * numO + O]) + "]"
    for O in Olist[5:8]:
        PRO_table[O * 3 + 0][0] = "max"
        PRO_table[O * 3 + 1][0] = "O" + str(O)
        PRO_table[O * 3 + 2][0] = "min"
        for T in Tlist:
            F_sum = sum([FOCO[OC * numO * numT + O * numT + T] for OC in OClist[5:8]])
            if F_sum >= 0.001:
                PRO_table[O * 3 + 0][T + 1] = "[" + str(PROMAX[1 * numO + O]) + " " + str(
                    PROMAX[2 * numO + O]) + " " + str(PROMAX[3 * numO + O]) + "]"
                PRO_table[O * 3 + 1][T + 1] = "[" + str(round(
                    sum([FOCO[OC * numO * numT + O * numT + T] * PRO[1 * numOC + OC] for OC in OClist[5:8]]) / F_sum,
                    2)) + " " + \
                                              str(round(sum(
                                                  [FOCO[OC * numO * numT + O * numT + T] * PRO[2 * numOC + OC] for OC in
                                                   OClist[5:8]]) / F_sum, 4)) + " " + \
                                              str(round(sum(
                                                  [FOCO[OC * numO * numT + O * numT + T] * PRO[3 * numOC + OC] for OC in
                                                   OClist[5:8]]) / F_sum, 4)) + "]"
                PRO_table[O * 3 + 2][T + 1] = "[" + str(PROMIN[1 * numO + O]) + " " + str(
                    PROMIN[2 * numO + O]) + " " + str(PROMIN[3 * numO + O]) + "]"
            # elif T != 0:
            #     PRO_table[O * 3 + 0][T + 1] = "[" + str(PROMAX[1 * numO + O]) + " " + str(
            #         PROMAX[2 * numO + O]) + " " + str(PROMAX[3 * numO + O]) + "]"
            #     PRO_table[O * 3 + 1][T + 1] = PRO_table[O * 3 + 1][T]
            #     PRO_table[O * 3 + 2][T + 1] = "[" + str(PROMIN[1 * numO + O]) + " " + str(
            #         PROMIN[2 * numO + O]) + " " + str(PROMIN[3 * numO + O]) + "]"
            else:
                PRO_table[O * 3 + 0][T + 1] = "[" + str(PROMAX[1 * numO + O]) + " " + str(
                    PROMAX[2 * numO + O]) + " " + str(PROMAX[3 * numO + O]) + "]"
                PRO_table[O * 3 + 1][T + 1] = "INI"
                PRO_table[O * 3 + 2][T + 1] = "[" + str(PROMIN[1 * numO + O]) + " " + str(
                    PROMIN[2 * numO + O]) + " " + str(PROMIN[3 * numO + O]) + "]"
    # print tabulate(PRO_table, PRO_header, tablefmt="simple", numalign="center", floatfmt=".3f")

    xQI = sol.get_values(xQI_c, xQI_c + xQIcount - 1)
    xyQI = sol.get_values(xyQI_c, xyQI_c + xyQIcount - 1)
    QI = sol.get_values(QI_c, QI_c+QIcount-1)
    ObjVal = 0
    for T in Tlist:
        ObjVal += QI[Ulist[0]*numT+T]*OPC*hours
    print "crude oil cost:",ObjVal
    a = 0
    for U in Ulist[0:2]:
        for M in Mlist[0:2]:
            for M1 in Mlist[0:2]:
                for T in Tlist:
                    if M1 != M:
                        a += xQI[U*numM*numM*numT+M*numM*numT+M1*numT+T]*hours*tOpCost[U*numM*numM+M*numM+M1]
    for U in Ulist[0:2]:
        for M in Mlist[0:2]:
            for T in Tlist:
                a += xyQI[U * numM * numT + M * numT + T]*hours * OpCost[U * numM + M]
    for U in Ulist[2:5]:
        for M in Mlist[0:4]:
            for M1 in Mlist[0:4]:
                for T in Tlist:
                    if M1 != M:
                        a += xQI[U*numM*numM*numT+M*numM*numT+M1*numT+T]*hours*tOpCost[U*numM*numM+M*numM+M1]
    for U in Ulist[2:5]:
        for M in Mlist[0:4]:
            for T in Tlist:
                a += xyQI[U * numM * numT + M * numT + T]*hours * OpCost[U * numM + M]
    for U in Ulist[5:7]:
        for M in Mlist[0:2]:
            for M1 in Mlist[0:2]:
                for T in Tlist:
                    if M1 != M:
                        a += xQI[U*numM*numM*numT+M*numM*numT+M1*numT+T]*hours*tOpCost[U*numM*numM+M*numM+M1]
    for U in Ulist[5:7]:
        for M in Mlist[0:2]:
            for T in Tlist:
                a += xyQI[U * numM * numT + M * numT + T]*hours * OpCost[U * numM + M]
    for U in Ulist[7:9]:
        for T in Tlist:
                a += QI[U*numT+T]*hours*OpCost[U*numM+Mlist[0]]
    ObjVal += a
    print "Unit operation cost:",a
    a = 0
    for O in Olist:
        for T in Tlist:
            if T == 0:
                a += (Otank_ini[O] + VO[O * numT + T]) * 0.5 * apo
            if T != 0:
                a += (VO[O * numT + T - 1] + VO[O * numT + T]) * 0.5 * apo
        # for T in Tlist:
        #     a += VO[O*numT+T]*apo
    ObjVal += a
    print "O inventory cost:",a
    a = 0
    for OC in OClist:
        for T in Tlist[:]:
            if T == 0:
                a += (OCtank_ini[OC] + VOC[OC * numT + T]) * 0.5 * apoc
            if T != 0:
                a += (VOC[OC * numT + T - 1] + VOC[OC * numT + T]) * 0.5 * apoc
        # for T in Tlist:
        #     a += VOC[OC*numT+T]*apoc
    ObjVal += a
    print "OC inventory cost:",a
    a = 0
    for L in Llist:
        for O in Olist:
            a += DV1[L,O]*bp
            for T in Tlist:
                a -= Otankout[O*numL*numT+L*numT+T]*(hours*bp) #-T*10
    ObjVal += a
    print "Order delay cost:",a
    Obj_1 = np.zeros((numL, numO))
    print "Order amount delay (DV1): "
    for L in range(numL):
        for O in Olist:
            for T in Tlist:
                Obj_1[L,O] += Otankout[O * numL * numT + L * numT + T] * hours
            Obj_1[L,O] = round(DV1[L,O] - Obj_1[L,O], 6)
    print Obj_1
    print "original order:"
    print DV1[:numL]
    print "object value : ",ObjVal
    return sol.get_objective_value()    # + sum(sum(DV1[:numL])) * bp

def printYield():
    # yield:numU*numM*numS
    Y_header = Slist[:]
    Y_header.insert(0,"Yield")
    Y_table_ = [0] * (numM + 1)
    Y_table = []
    for U in Ulist[0:9]:
        Y_table.append(Y_table_[:])
    for U in Ulist[0:9]:
        for M in Mlist:
            Y_table[U][0] = "U"+str(U)
            S_all = []
            for S in Slist:
                S_all.append(round(Yield[U*numM*numS+M*numS+S],4))
            Y_table[U][M+1] = S_all
    print tabulate(Y_table, Y_header, tablefmt="simple", numalign="center", floatfmt=".3f")
    # tyield:numU*numM*numS
    tY_header = ['00','01','02','03',10,11,12,13,20,21,22,23,30,31,32,33]
    tY_header.insert(0, "tYield")
    tY_table_ = [0] * (numM*numM + 1)
    tY_table = []
    for U in Ulist[0:9]:
        tY_table.append(tY_table_[:])
    for U in Ulist[0:9]:
        for M in Mlist:
            for M_ in Mlist:
                tY_table[U ][0] = "U" + str(U)
                S_all = []
                for S in Slist:
                    S_all.append(round(tYield[U * numM * numM * numS + M * numM * numS + M_ * numS + S],4))
                tY_table[U][M*numM + M_ + 1] = S_all
    print tabulate(tY_table, tY_header, tablefmt="simple", numalign="center", floatfmt=".3f")

    # Cost:numU*numM
    Cost_header = Mlist[:]
    Cost_header.insert(0,"Cost")
    Cost_table_ = [0] * (numM + 1)
    Cost_table = []
    for U in Ulist[0:9]:
        Cost_table.append(Cost_table_[:])
    for U in Ulist[0:9]:
        Cost_table[U][0] = "U" + str(U)
        for M in Mlist:
            Cost_table[U][M + 1] = OpCost[U * numM + M]
    print tabulate(Cost_table, Cost_header, tablefmt="simple", numalign="center", floatfmt=".3f")
    # tCost:numU*numM*numM
    tCost_header = ['00','01','02','03',10,11,12,13,20,21,22,23,30,31,32,33]
    tCost_header.insert(0,"tCost")
    tCost_table_ = [0] * (numM*numM + 1)
    tCost_table = []
    for U in Ulist[0:9]:
        tCost_table.append(tCost_table_[:])
    for U in Ulist[0:9]:
        tCost_table[U][0] = "U" + str(U)
        for M in Mlist:
            for M_ in Mlist:
                tCost_table[U][M * numM + M_ + 1] = tOpCost[U * numM * numM + M * numM + M_]
    print tabulate(tCost_table, tCost_header, tablefmt="simple", numalign="center", floatfmt=".3f")

def run(CASE):
    printYield()
    for i in range(len(CASE)):
        if CASE[i] == 'ShiL-case1':
            numT = 8
            Tlist = range(numT)
            numL1 = 2
            Llist1 = range(numL1)
            OCtank_ini = [0,0,0,0,0,0,0,0]
            Otank_ini = [0]*numO
            DS_num = [[0,6],[2,8]]
            DS1 = [[1, 1, 1, 1, 1, 1, 0, 0], [0, 0, 1, 1, 1, 1, 1, 1]]
            DV1 = [[100.,400.,200.,100.,550.,1000.,600.,700.],
                   [100.,300.,100.,100.,700.,800.,700.,900.]]
            DV1 = np.array(DV1)
            DS1 = np.array(DS1)
            DS_num = np.array(DS_num)
            Pri = 1
            Mode = 0
            sample = 0
            Mode = [0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -0.0, -0.0, -0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0,
                 -0.0, 0.0, 0.0, -0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, -0.0, -0.0,
                 0.0, 0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, -0.0, -0.0, 1.0, 1.0, 1.0, 1.0,
                 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, -0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, -0.0, -0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                 -0.0, 0.0, 0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

            for u in Ulist[7:9]:
                for M in [Mlist[0]]:
                    for t in Tlist:
                        Mode[u*numM*numT+M*numT+t]=1
            QI_atm = [234.64,222.675,200.,200.,285.653,200.,200.,219.327]
            QI_eth = [5.,5.,5.,5.,5.,5.,5.,5.]
            # QI_htu1 = [38.806, 34.752, 34.752, 34.752, 46.047, 38.97, 30.698, 33.852]
            # QI_htu1 = [45.527,38.692,34.752,34.752,43.845,30.698,30.698,33.664]
            QI_htu1 = [45.527,38.692,34.752,34.752,43.8445,30.698,30.698,33.664]
            refinery(numT, Tlist, numL1, Llist1, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode)#,QI_atm,QI_eth,QI_htu1
        elif CASE[i] == '12s3o':
            NCmax = 15
            numT = 12
            Tlist = range(numT)
            numL1 = 3
            Llist1 = range(numL1)
            DS_num = [[0,12],[2,6],[4,8]]
            DS1 = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0]]
            DV1 = [[400.,200.,300.,100.,250.,500.,400.,600.],
                   [50.,50.,100.,100.,200.,300.,300.,300.],
                   [100.,100.,100.,100.,200.,300.,200.,400.]]
            OCtank_ini = [0,0,0,0,0,0,0,0]
            Otank_ini = [0]*numO
            DV1 = np.array(DV1)
            DS1 = np.array(DS1)
            DS_num = np.array(DS_num)
            Pri = 1
            Mode = 0
            sample = 0
            Mode = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, -0.0, -0.0,
                 -0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, 0.0, 0.0, -0.0, -0.0, -0.0, -0.0,
                 -0.0, 1.0, 1.0, 1.0, -0.0, 0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, 0.0, -0.0, 0.0, 1.0, 1.0,
                 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -0.0, -0.0, 0.0, -0.0, -0.0, 0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, -0.0, -0.0, 0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, -0.0, -0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -0.0, -0.0, 0.0,
                 -0.0, -0.0, 0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, -0.0, 0.0, -0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, -0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, 1.0, 1.0, 1.0,
                 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0,
                 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, -0.0, -0.0, -0.0, -0.0, 0.0, -0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

            for u in Ulist[7:9]:
                for M in [Mlist[0]]:
                    for t in Tlist:
                        Mode[u*numM*numT+M*numT+t]=1
            QI_atm = [200.000,200.000,200.000 , 200.000  ,200.000 , 200.000 , 200.000  ,200.000  ,200.000,  200.000 , 200.000,  200.000]
            QI_eth = [ 6.936  ,  7.045 ,   7.137   , 8.472 ,   9.360 ,  14.237 ,  11.515   ,15.074 ,  15.074 ,  15.074 ,  15.074 ,   5.000]
            # QI_htu1 = [38.806, 34.752, 34.752, 34.752, 46.047, 38.97, 30.698, 33.852]
            # QI_htu1 = [45.527,38.692,34.752,34.752,43.845,30.698,30.698,33.664]
            QI_htu1 = [30.698  , 30.698,   30.698  , 30.698   ,30.698  , 30.698 ,  30.698  , 30.698 ,  30.698  ,  5.000   , 5.000  ,  5.000]

            refinery(numT, Tlist, numL1, Llist1, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode) #,QI_atm,QI_eth,QI_htu1
        elif CASE[i] == '18s3o':
            NCmax = 30
            numT = 18
            Tlist = range(numT)
            numL1 = 3
            Llist1 = range(numL1)
            DS1 = [[1, 1, 1, 1, 1, 1, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 1, 1, 1, 1, 1, 1, 0, 0]]
            DV1 = [[90.,80.,70.,80.,70.,120.,150.,130.],
                  [20.,50.,40.,30.,20.,120.,130.,205.],
                  [40.,50.,45.,52.,60.,120.,130.,130.],
                  [380.,70.,0.,150.,1125.,650.,1500.,2250.]] # numL*numO
            DS_num = [[0,5],[4,14],[12,17]]
            OCtank_ini = [0,0,0,0,0,0,0,0]
            Otank_ini = [0]*numO
            DV1 = np.array(DV1)
            DS1 = np.array(DS1)
            DS_num = np.array(DS_num)
            Pri = 1
            sample = 0
            Mode = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -0.0,
                    -0.0, -0.0, -0.0, -0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -0.0, 0.0, 0.0, -0.0, -0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, 0.0, 0.0, 0.0, -0.0, 0.0, 0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    -0.0, -0.0, -0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, 0.0, -0.0, 0.0, 0.0, 0.0, 0.0, -0.0, -0.0, 1.0,
                    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, 0.0, -0.0, -0.0, -0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                    1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0, 0.0, -0.0, -0.0, -0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0,
                    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                    1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -0.0,
                    -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            for u in Ulist[7:9]:
                for M in [Mlist[0]]:
                    for t in Tlist:
                        Mode[u*numM*numT+M*numT+t]=1
            VOC = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 9.011932009398848, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.5715354292839647, 1.1320696830866557, 1.6999295128679717, 2.3000839593084863, 2.888687200200794,
                   3.59625431204425, 3.553878812312249, 3.949933489094862, 4.158103968443012, 4.378415553531016,
                   6.135470483328418, 8.398931149101832, 3.6253383532680257, 3.8335088326161753, 4.07356927984634,
                   4.436060470327375, 5.5370235736254285, 7.926285370707028, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 8.739951172538424, 20.545627124257358, 0.0, 0.0, 0.0, 0.0, 0.0, 1.7325680923623175, 0.0,
                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.7840786345198554, 8.444078634519855, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, 0.0, 5.582746019410969, 52.28977486085253, 11.91465813436701, 40.23099766910362,
                   43.416293676568706, 46.60158968403379, 71.0417988770403, 101.5702825380136, 132.09876619898688,
                   169.7731818110169, 88.70204452327414, 88.95540918881287, 119.78338063263567, 151.61128743729927,
                   183.43919424196287, 222.2862256152525, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   34.50874675862072, 0.0, 0.0, 0.0, 0.0, 0.0, 0.7072823309053486, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 25.698000000000004]
            VO = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0, 0.0]
            QI_atm = [300.000,300.000,300.000,300.000,300.000,300.000,200.000,200.000,200.000,200.000,200.000,200.000,200.000,200.000,200.000,200.000,200.000,200.000]
            QI_eth = [5.000,5.000,5.000,5.000,5.000,5.000,5.000,5.000,5.000,5.000,5.000,5.000,5.000,5.000,5.000,5.000,5.000,5.000]
            QI_htu1 = [46.0470000,46.0470000,46.0470000,46.0470000,46.0470000,46.0470000,34.7520000,34.7520000,34.7520000,38.8060000,38.8060000,38.8060000,34.7520000,34.7520000,34.7520000,30.6980000,30.6980000, 5.0000000]
            refinery(numT, Tlist, numL1, Llist1, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode,QI_atm,QI_eth,QI_htu1) #

        elif CASE[i] == 'VS-case1-10slots-Atuo':
            print " ==================== VS-case1-10slots-40-1"
            numT = 8
            Tlist = range(numT)
            OCtank_ini = [0] * 8
            Otank_ini = [0] * 8
            DV1 = [[100.,400.,200.,100.,550.,1000.,600.,700.],
                     [200.,300.,100.,100.,700.,800.,700.,900.]]
            DV1 = np.array(DV1)
            DS_num = [[1.,6.],[3.,8.]]
            DS_num = np.array(DS_num)
            numL1 = 2
            Llist1 = range(numL1)
            DS1 = np.zeros((numL1, numT))
            for L1 in Llist1:
                DS1[L1, DS_num[L1, 0].astype(int):DS_num[L1, 1].astype(int) + 1] = 1
            Pri = 0
            Mode = 0
            sample = 0
            refinery(numT, Tlist, numL1, Llist1, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode)
        elif CASE[i] == 'VS-case1-10slots-40':
            print " ==================== VS-case1-10slots-40-1"
            numT = 40
            Tlist = range(numT)
            OCtank_ini = [0] * 8
            Otank_ini = [0] * 8
            DV1 = [[232, 159, 145, 158, 120, 266, 376, 280],
                   [133, 132, 118, 124, 33, 351, 269, 235],
                   [142, 150, 120, 180, 59, 261, 258, 283],
                   [36, 40, 58, 22, 31, 153, 80, 90],
                   [17, 38, 21, 35, 34, 64, 161, 138],
                   [33, 56, 26, 22, 51, 74, 67, 148],
                   [47, 61, 48, 110, 52, 82, 47, 168],
                   [33, 23, 45, 157, 58, 177, 187, 63],
                   [28, 6, 4, 59, 36, 64, 19, 143],
                   [55, 42, 16, 35, 43, 179, 28, 153],
                   [11, 41, 2, 117, 23, 48, 143, 150],
                   [23, 52, 58, 26, 39, 88, 159, 57],
                   [8, 53, 121, 124, 22, 46, 170, 43],
                   [50, 20, 50, 31, 33, 118, 55, 77],
                   [41, 41, 24, 17, 3, 48, 143, 50],
                   [23, 52, 58, 26, 39, 88, 47, 57],
                   [28, 53, 21, 24, 22, 146, 40, 66],
                   [50, 50, 40, 31, 33, 80, 55, 77]]
            DV1 = np.array(DV1)
            DS_num = [[0, 24],
                      [14, 27],
                      [16, 29],
                      [24, 39],
                      [10, 38],
                      [8, 25],
                      [1, 37],
                      [16, 39],
                      [22, 28],
                      [1, 23],
                      [24, 38],
                      [1, 38],
                      [2, 45],
                      [7, 49],
                      [14, 38],
                      [14, 24],
                      [2, 25],
                      [13, 49]]
            DS_num = np.array(DS_num)
            numL1 = 3
            Llist1 = range(numL1)
            DS1 = np.zeros((numL1, numT))
            for L1 in Llist1:
                DS1[L1, DS_num[L1, 0].astype(int):DS_num[L1, 1].astype(int) + 1] = 1
            Pri = 0
            Mode = 0
            sample = 0
            refinery(numT, Tlist, numL1, Llist1, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode)
        elif CASE[i] == 'VS-case1-10slots-40-2-600s':
                name = "-40-2"
                VF = 1                                   # with or without Valid Functions
                numT = 40
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
                Pri = 0
                n_num = 10
                print "############################# sample: ################"
                # OCtank_ini_1 = np.random.randint(0, 20, (numOC_g))
                # OCtank_ini_2 = np.random.randint(0, 40, (numOC_d))
                # OCtank_ini = np.hstack((OCtank_ini_1, OCtank_ini_2))
                # Otank_ini_1 = np.random.randint(0, 10, (numO_g))
                # Otank_ini_2 = np.random.randint(0, 30, (numO_d))
                # Otank_ini = np.hstack((Otank_ini_1, Otank_ini_2))
                # numL1 = np.random.randint(1, 15)  # for 1-6
                # Llist1 = range(numL1)
                # DV1_1 = np.random.randint(0, 61, (numL1, numO_g))
                # DV1_2 = np.random.randint(5, 91, (numL1, numO_d))
                # DV1 = np.hstack((DV1_1, DV1_2))
                # DS_num = np.zeros((numL1, 2))
                # for L1 in Llist1:
                #     if L1 == 0:
                #         DS_num[L1, 0] = 0
                #     else:
                #         DS_num[L1, 0] = np.random.randint(0, numT - 3)  # 3 means the shortest length of order duration.
                #     if L1 == Llist1[-1]:
                #         DS_num[L1, 1] = numT - 1
                #     else:
                #         DS_num[L1, 1] = np.random.randint(min(numT - 1, DS_num[L1, 0] + 3), numT)
                # DV1 = [[11,7,26,4,1,35,62,43],
                #         [49,25,36,53,2,41,80,37],
                #         [45,34,36,41,7,18,80,51],
                #         [56,2,1,58,23,12,90,10],
                #         [7,2,12,48,8,26,27,55],
                #         [18,19,44,59,44,21,63,11],
                #         [10,5,1,46,48,44,41,78],
                #         [48,55,26,42,23,53,62,47],
                #         [47,59,17,36,16,17,17,25],
                #         [39,59,38,44,0,54,78,19],
                #         [58,21,8,50,25,86,77,37],
                #         [55,54,14,20,48,60,82,67]]
                # DS_num =[[0,16],
                #             [9,21],
                #             [9,19],
                #             [23,28],
                #             [13,28],
                #             [17,26],
                #             [19,29],
                #             [7,11],
                #             [13,25],
                #             [24,29],
                #             [4,17],
                #             [4,29]]
                OCtank_ini = [17,16,0,15,6,17,12,34]
                Otank_ini = [5,0,1,0,6,5,15,21]
                DV1 = [[34, 40, 34, 34, 41, 230, 234, 183],
                       [39, 55, 36, 33, 52, 252, 125, 212],
                       [25, 34, 46, 51, 67, 168, 120, 181],
                       [36, 30, 31, 38, 53, 252, 209, 190],
                       [47, 50, 62, 48, 58, 272, 227, 165],
                       [38, 49, 54, 49, 56, 200, 203, 241],
                       [30, 45, 57, 36, 68, 154, 141, 122],
                       [42, 45, 26, 49, 53, 101, 87, 107],
                       [29, 32, 56, 72, 63, 221, 207, 97]]
                DS_num = [[0, 29],
                          [11, 32],
                          [25, 39],
                          [13, 38],
                          [9, 18],
                          [15, 36],
                          [18, 39],
                          [7, 31],
                          [11, 36]]
                DS_num = np.array(DS_num)
                numL1 = 9
                DV1 = np.array(DV1[:numL1])#-np.array(DV1_1[:numL1])-np.array(DV1_2[:numL1])
                Llist1 = range(numL1)
                DS1 = np.zeros((numL1, numT))
                for L1 in Llist1:
                    DS1[L1, DS_num[L1, 0].astype(int):DS_num[L1, 1].astype(int) + 1] = 1
                Pri = 1
                Mode = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                        1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                        1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0,
                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0,
                        1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                        1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0,
                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0,
                        0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0,
                        1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                        1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0,
                        1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0,
                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0,
                        0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0,
                        1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0,
                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                        1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

                sample = 0
                refinery(numT, Tlist, numL1, Llist1, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini, Mode)
        elif CASE[i] == 'VS-case1-10slots-60-1':
            print " ==================== VS-case1-10slots-60-1"
            numT = 60
            Tlist = range(numT)
            OCtank_ini = [0] * 8
            Otank_ini = [0] * 8
            DV1 = [[12, 59, 45, 58, 120, 66, 176, 10],
                   [33, 12, 118, 24, 13, 51, 169, 35],
                   [42, 50, 120, 20, 59, 61, 58, 183],
                   [36, 40, 58, 22, 31, 153, 80, 90],
                   [17, 38, 21, 35, 34, 64, 161, 138],
                   [33, 56, 26, 22, 51, 74, 67, 148],
                   [47, 61, 48, 110, 52, 82, 47, 168],
                   [33, 23, 45, 157, 58, 177, 187, 63],
                   [28, 6, 4, 59, 36, 64, 19, 143],
                   [55, 42, 16, 35, 43, 179, 28, 153],
                   [11, 41, 2, 117, 23, 48, 143, 150],
                   [23, 52, 58, 26, 39, 88, 159, 57],
                   [8, 53, 121, 124, 22, 46, 170, 43],
                   [50, 20, 50, 31, 33, 118, 55, 77],
                   [41, 41, 24, 17, 3, 48, 143, 50],
                   [23, 52, 58, 26, 39, 88, 47, 57],
                   [28, 53, 21, 24, 22, 146, 40, 66],
                   [50, 50, 40, 31, 33, 80, 55, 77]]
            DV1 = np.array(DV1)
            DS_num = [[0, 24],
                      [14, 47],
                      [16, 45],
                      [34, 59],
                      [10, 38],
                      [8, 25],
                      [1, 37],
                      [16, 39],
                      [22, 28],
                      [1, 23],
                      [24, 38],
                      [1, 38],
                      [2, 45],
                      [7, 49],
                      [14, 38],
                      [14, 24],
                      [2, 25],
                      [13, 49]]
            DS_num = np.array(DS_num)
            numL1 = 4
            Llist1 = range(numL1)
            DS1 = np.zeros((numL1, numT))
            for L1 in Llist1:
                DS1[L1, DS_num[L1, 0].astype(int):DS_num[L1, 1].astype(int) + 1] = 1
            Pri = 0
            Mode = 0
            sample = 0
            refinery(numT, Tlist, numL1, Llist1, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode)

        elif CASE[i] == 'VS-case1-10slots-60-2':
            print " ==================== VS-case1-10slots-60-2"
            numT = 60
            Tlist = range(numT)
            OCtank_ini = [0] * 8
            Otank_ini = [0] * 8
            DV1 = [[12, 59, 45, 58, 120, 66, 176, 10],
                   [33, 12, 118, 24, 13, 51, 169, 35],
                   [42, 50, 120, 20, 59, 61, 58, 183],
                   [36, 40, 58, 22, 31, 153, 80, 90],
                   [17, 38, 21, 35, 34, 64, 161, 138],
                   [33, 56, 26, 22, 51, 74, 67, 148],
                   [47, 61, 48, 110, 52, 82, 47, 168],
                   [33, 23, 45, 157, 58, 177, 187, 63],
                   [28, 6, 4, 59, 36, 64, 19, 143],
                   [55, 42, 16, 35, 43, 179, 28, 153],
                   [11, 41, 2, 117, 23, 48, 143, 150],
                   [23, 52, 58, 26, 39, 88, 159, 57],
                   [8, 53, 121, 124, 22, 46, 170, 43],
                   [50, 20, 50, 31, 33, 118, 55, 77],
                   [41, 41, 24, 17, 3, 48, 143, 50],
                   [23, 52, 58, 26, 39, 88, 47, 57],
                   [28, 53, 21, 24, 22, 146, 40, 66],
                   [50, 50, 40, 31, 33, 80, 55, 77]]
            DV1 = np.array(DV1)
            DS_num = [[0, 24],
                      [14, 47],
                      [16, 35],
                      [24, 26],
                      [30, 59],
                      [8, 25],
                      [1, 37],
                      [16, 39],
                      [22, 28],
                      [1, 23],
                      [24, 38],
                      [1, 38],
                      [2, 45],
                      [7, 49],
                      [14, 38],
                      [14, 24],
                      [2, 25],
                      [13, 49]]
            DS_num = np.array(DS_num)
            numL1 = 5
            Llist1 = range(numL1)
            DS1 = np.zeros((numL1, numT))
            for L1 in Llist1:
                DS1[L1, DS_num[L1, 0].astype(int):DS_num[L1, 1].astype(int) + 1] = 1
            Pri = 0
            Mode = 0
            sample = 0
            refinery(numT, Tlist, numL1, Llist1, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode)

        elif CASE[i] == 'VS-case1-10slots-100-1':
            print " ==================== VS-case1-10slots-100-1"
            numT = 100
            Tlist = range(numT)
            OCtank_ini = [0] * 8
            Otank_ini = [0] * 8
            DV1 = [[12, 59, 45, 58, 120, 66, 176, 10],
                   [33, 12, 118, 24, 13, 51, 169, 35],
                   [42, 50, 120, 20, 59, 61, 58, 183],
                   [36, 40, 58, 22, 31, 153, 80, 90],
                   [17, 38, 21, 35, 34, 64, 161, 138],
                   [33, 56, 26, 22, 51, 74, 67, 148],
                   [47, 61, 48, 110, 52, 82, 47, 168],
                   [33, 23, 45, 157, 58, 177, 187, 63],
                   [28, 6, 4, 59, 36, 64, 19, 143],
                   [55, 42, 16, 35, 43, 179, 28, 153],
                   [11, 41, 2, 117, 23, 48, 143, 150],
                   [23, 52, 58, 26, 39, 88, 159, 57],
                   [8, 53, 121, 124, 22, 46, 170, 43],
                   [50, 20, 50, 31, 33, 118, 55, 77],
                   [41, 41, 24, 17, 3, 48, 143, 50],
                   [23, 52, 58, 26, 39, 88, 47, 57],
                   [28, 53, 21, 24, 22, 146, 40, 66],
                   [50, 50, 40, 31, 33, 80, 55, 77]]
            DV1 = np.array(DV1)
            DS_num = [[0, 54],
                      [14, 47],
                      [16, 55],
                      [54, 86],
                      [10, 78],
                      [8, 55],
                      [1, 37],
                      [56, 99],
                      [22, 28],
                      [1, 23],
                      [24, 38],
                      [1, 38],
                      [2, 45],
                      [7, 49],
                      [14, 38],
                      [14, 24],
                      [2, 25],
                      [13, 49]]
            DS_num = np.array(DS_num)
            numL1 = 8
            Llist1 = range(numL1)
            DS1 = np.zeros((numL1, numT))
            for L1 in Llist1:
                DS1[L1, DS_num[L1, 0].astype(int):DS_num[L1, 1].astype(int) + 1] = 1
            Pri = 0
            Mode = 0
            sample = 0
            refinery(numT, Tlist, numL1, Llist1, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode)


        elif CASE[i] == 'VS-case1-10slots-VF1':
            VF = 1                                   # with or without Valid Functions
            numT = 50
            TC = "time"                             # Termination_condition: gap or time
            if TC == "gap":
                gap = 0.01
                time = 0
                case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
            elif TC == "time":
                gap = 0.0
                time = 600
                case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
            Tlist = range(numT)
            numL = 8  # order quantity
            numL_g = 5
            numL_d = 3
            L_glist = range(numL_g)
            L_dlist = range(numL_d)
            Tarr = [1, 8, 14]
            Vessel_V = [5000.0,5000.0,5000.0]
            Initial_S = [6880.0,6200.0,6000.0]
            Initial_B = [8320.0,7200.0,2000.0]
            # DS = [[1,1,1,0,1,1,0,0,0,0],[1,1,1,0,1,1,0,0,0,0],[1,1,1,0,1,1,0,0,0,0],[0,1,1,1,1,1,0,0,0,0],
            #       [0,1,1,1,1,1,1,1,1,1],[1,1,1,0,1,1,1,1,1,1],[1,1,1,0,1,1,1,1,1,1],[0,1,1,1,1,1,1,1,1,1]]
            DS_num = [[0,10],[0,10],[0,10],[10,20],[10,20],[0,10],[0,10],[10,20]]
            DS = [[1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1]]
            DP_num = [0,3,4,2,1,             6,7,8]  # no unloading oil. so the order needed is what tank.
            # DV = [400,500,300,300,300,    1200,1000,1400]
            DV = [240,300,180,180,180,    720,600,840]
            numL1 = 3
            Llist1 = range(numL1)
            DS1 = [[1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                   [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1]]
            DS_num = [[0,15],[0,19],[10,29]]
            # DV1 = [[400,0,0,500,0,    1200,0,0],[0,0,0,0,300,    0,1000,0],[0,300,300,0,0,    0,0,1400]]
            # DV1 = [[400,500,0,0,0,    1200,0,0],[0,0,300,0,0,    0,1000,0],[0,0,0,300,300,    0,0,1400]]
            DV1 = [[400,300,0,0,0,    720,0,0],[0,0,180,0,0,    0,600,0],[0,0,0,180,180,    0,0,840]]
            DP = [[1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],[0,0,0,0,1,0,0,0],[0,0,1,0,0,0,0,0],
                  [0,1,0,0,0,0,0,0],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1]]
            Pri = 0
            num_sample = 1
            n_num = 10
            numL1 = numT
            book = xlwt.Workbook(encoding='utf-8', style_compression=0)
            for sample in range(num_sample):
                print "############################# sample:",sample,"################"
                # OCtank_ini_1 = np.random.randint(0,20,(numOC_g))
                # OCtank_ini_2 = np.random.randint(0,40,(numOC_d))
                # OCtank_ini = np.hstack((OCtank_ini_1,OCtank_ini_2))
                # Otank_ini_1 = np.random.randint(0,10,(numO_g))
                # Otank_ini_2 = np.random.randint(0,30,(numO_d))
                # Otank_ini = np.hstack((Otank_ini_1,Otank_ini_2))
                # Llist1 = range(numL1)
                # DS_num = np.zeros((numL1,2))
                # if sample < 50:
                #     DV1_1 = np.random.randint(0,12,(numL1,numO_g))
                #     DV1_2 = np.random.randint(0,22,(numL1,numO_d))
                #     DS_num[:,1] = numT-1
                #     DS_num[:,0] = Tlist
                # elif 50 <= sample < 100:
                #     DV1_1 = np.random.randint(3,17,(numL1,numO_g))
                #     DV1_2 = np.random.randint(4,32,(numL1,numO_d))
                #     DS_num[:,1] = numT-1
                #     DS_num[:,0] = Tlist
                # elif 100 <= sample < 150:
                #     DV1_1 = np.random.randint(5,19,(numL1,numO_g))
                #     DV1_2 = np.random.randint(8,29,(numL1,numO_d))
                #     DS_num[:,1] = numT-1
                #     DS_num[:,0] = Tlist
                # elif 150 <= sample < 200:
                #     DV1_1 = np.random.randint(9,24,(numL1,numO_g))
                #     DV1_2 = np.random.randint(10,37,(numL1,numO_d))
                #     DS_num[:,1] = numT-1
                #     DS_num[:,0] = Tlist
                # elif 200 <= sample < 250:
                #     DV1_1 = np.random.randint(15,35,(numL1,numO_g))
                #     DV1_2 = np.random.randint(20,50,(numL1,numO_d))
                #     DS_num[:,1] = numT-1
                #     DS_num[:,0] = Tlist
                # elif 250 <= sample < 300:
                # # if sample < 300:
                #     DV1_1 = np.random.randint(0,12,(numL1,numO_g))
                #     DV1_2 = np.random.randint(0,22,(numL1,numO_d))
                #     DS_num[:,1] = Tlist
                #     DS_num[:,0] = 0
                # elif 300 <= sample < 350:
                #     DV1_1 = np.random.randint(3,17,(numL1,numO_g))
                #     DV1_2 = np.random.randint(4,32,(numL1,numO_d))
                #     DS_num[:,1] = Tlist
                #     DS_num[:,0] = 0
                # elif 350 <= sample < 400:
                #     DV1_1 = np.random.randint(5,19,(numL1,numO_g))
                #     DV1_2 = np.random.randint(8,29,(numL1,numO_d))
                #     DS_num[:,1] = Tlist
                #     DS_num[:,0] = 0
                # elif 400 <= sample < 450:
                #     DV1_1 = np.random.randint(9,24,(numL1,numO_g))
                #     DV1_2 = np.random.randint(10,37,(numL1,numO_d))
                #     DS_num[:,1] = Tlist
                #     DS_num[:,0] = 0
                # elif 450 <= sample < 500:
                #     DV1_1 = np.random.randint(15,35,(numL1,numO_g))
                #     DV1_2 = np.random.randint(20,50,(numL1,numO_d))
                #     DS_num[:,1] = Tlist
                #     DS_num[:,0] = 0
                # else:
                #     numL1 = np.random.randint(1, 9)  # for 1-6
                #     Llist1 = range(numL1)
                #     DV1_1 = np.random.randint(0,41,(numL1,numO_g))
                #     DV1_2 = np.random.randint(5,71,(numL1,numO_d))
                #     DS_num = np.zeros((numL1,2))
                #     for L1 in Llist1:
                #         if L1 == 0:
                #             DS_num[L1,0] = 0
                #         else:
                #             DS_num[L1,0] = np.random.randint(0,numT-3) # 3 means the shortest length of order duration.
                #         if L1 == Llist1[-1]:
                #             DS_num[L1,1] = numT-1
                #         else:
                #             DS_num[L1,1] = np.random.randint(min(numT-1,DS_num[L1,0]+3),numT)
                # DV1 = np.hstack((DV1_1,DV1_2))
                # DS1 = np.zeros((numL1,numT))
                # for L1 in Llist1:
                #     DS1[L1,DS_num[L1,0].astype(int):DS_num[L1,1].astype(int)+1] = 1
                # DV1_1 = np.random.randint(0, 61, (numL1, numO_g))
                # DV1_2 = np.random.randint(5, 91, (numL1, numO_d))
                # DV1 = np.hstack((DV1_1, DV1_2))
                # for L1 in Llist1:
                #     if L1 == 0:
                #         DS_num[L1, 0] = 0
                #     else:
                #         DS_num[L1, 0] = np.random.randint(0, numT - 3)  # 3 means the shortest length of order duration.
                #     if L1 == Llist1[-1]:
                #         DS_num[L1, 1] = numT - 1
                #     else:
                #         DS_num[L1, 1] = np.random.randint(min(numT - 1, DS_num[L1, 0] + 3), numT)
                # ==============================
                # OCtank_ini = np.array([16,11,11,19,13,22,20,30])
                # Otank_ini = np.array([1,6,1,8,1,18,7,16])
                # numL1 = 14
                # Llist1 = range(numL1)
                # DV1 = [[2,59,5,8,20,66,76,10],
                #         [33,2,8,24,13,51,69,35],
                #         [42,10,0,20,59,61,58,83],
                #         [36,40,58,2,11,53,80,90],
                #         [17,8,21,35,34,64,61,38],
                #         [13,56,26,22,51,74,7,28],
                #         [17,11,48,10,52,82,47,68],
                #         [33,23,45,57,58,77,87,63],
                #         [28,6,4,59,36,64,19,43],
                #         [55,42,16,35,3,79,28,53],
                #         [11,41,2,17,3,48,43,50],
                #         [23,52,58,26,39,88,9,17],
                #         [8,53,21,24,22,46,10,13],
                #         [50,0,10,31,33,8,55,77]]
                # DV1 = np.array(DV1)
                # DS_num = [[0,24],
                #             [24,27],
                #             [26,29],
                #             [14,26],
                #             [10,18],
                #             [8,25],
                #             [1,27],
                #             [16,19],
                #             [22,28],
                #             [1,13],
                #             [24,28],
                #             [1,18],
                #             [2,25],
                #             [13,29]]
                OCtank_ini = [0]*8
                Otank_ini = [0]*8
                DV1 = [[12,59,45,58,120,66,176,10],
                        [33,12,118,24,13,51,169,35],
                                        [42,50,120,20,59,61,58,183],
                                        [36,40,58,22,31,153,80,90],
                                        [17,38,21,35,34,64,161,138],
                                        [33,56,26,22,51,74,67,148],
                                        [47,61,48,110,52,82,47,168],
                                        [33,23,45,157,58,177,187,63],
                                        [28,6,4,59,36,64,19,143],
                                        [55,42,16,35,43,179,28,153],
                                        [11,41,2,117,23,48,143,150],
                                        [23,52,58,26,39,88,159,57],
                                        [8,53,121,124,22,46,170,43],
                                        [50,20,50,31,33,118,55,77],
                                        [41,41,24,17,3,48,143,50],
                                        [23,52,58,26,39,88,47,57],
                                        [28,53,21,24,22,146,40,66],
                                        [50,50,40,31,33,80,55,77]]
                DV1 = np.array(DV1)
                DS_num = [[0,24],
                                            [24,47],
                                            [26,49],
                                            [14,26],
                                            [10,38],
                                            [8,25],
                                            [1,37],
                                            [16,39],
                                            [22,28],
                                            [1,23],
                                            [24,38],
                                            [1,38],
                                            [2,45],
                                            [7,49],
                                            [14,38],
                                            [14,24],
                                            [2,25],
                                            [13,49]]
                # DS_num = np.array(DS_num)
                numL1 = 18
                Llist1 = range(numL1)
                # OCtank_ini = np.array([17,16,0,15,6,17,12,34])
                # Otank_ini = np.array([5,0,1,0,6,5,15,21])
                # numL1 = 6
                # Llist1 = range(numL1)
                # DV1 = [[47,60,26,36,6,48,8,18],
                #         [52,12,11,6,44,87,16,75],
                #         [28,22,2,46,18,30,62,7],
                #         [18,32,24,9,11,33,88,20],
                #         [20,47,33,40,37,69,12,72],
                #         [54,7,35,40,47,53,8,27]]
                # DV1 = np.array(DV1)
                # DS_num = [[0,10],
                #             [18,21],
                #             [18,26],
                #             [12,17],
                #             [26,29],
                #             [26,29]]
                DS_num = np.array(DS_num)
                # =====================================================
                DS1 = np.zeros((numL1, numT))
                for L1 in Llist1:
                    DS1[L1, DS_num[L1, 0].astype(int):DS_num[L1, 1].astype(int) + 1] = 1
                # mode = np.zeros((numU,numM,numT))
                # for i in range(numT):
                #     for u in Ulist:
                #         if u in [0,1,5,6]:
                #             m = np.random.randint(0,2)
                #         elif u in [2]:
                #             m = np.random.randint(0,4)
                #         else:
                #             m = 0
                #         mode[u,m,i] =1
                # mode[3, :,:] = mode[2,:,:]
                # mode[4, :,:] = mode[2,:,:]
                # mode = mode.reshape((numT*numU*numM,)).tolist()
                Obj_value, FOout, OC_inventory, O_inventory, Mode_act,FinM, Qout = PRO_opt(numT,Tlist,numL1,Llist1,DS1,DV1,Pri,DS_num,sample,OCtank_ini,Otank_ini)#,mode
                # print "Objective:",Obj_value

                Prod_flow = np.zeros((numT,numO,numL1,n_num))
                Prod_sum = np.zeros((numT,numO))
                FOout_sum = np.zeros((numL1,numO))
                Oout_sum = np.zeros((numT,numO))
                for O in Olist:
                    for L in Llist1:
                        for T in Tlist:
                            if T >= 1:
                                FOout_sum[L,O] += FOout[O * numL1 * numT + L * numT + T-1]
                            if T <= DS_num[L][1]:
                                Prod_flow[T,O,L,0] = (DV1[L][O] - FOout_sum[L,O] * hours) / (DS_num[L][1] - T + 1)
                            for n in range(1,n_num):
                                if T+n <= DS_num[L][0]:
                                    Prod_flow[T,O,L,n] = (DV1[L][O] - FOout_sum[L,O] * hours) / (DS_num[L][1] - T + 1-n)
                                elif DS_num[L][0] < T+n <= DS_num[L][1]:
                                    Prod_flow[T,O,L,n] = Prod_flow[T,O,L,n-1]
                                elif DS_num[L][1] < T+n:
                                    Prod_flow[T,O,L,n] = 0

                sheet = book.add_sheet('case'+str(sample), cell_overwrite_ok=True)
                sheet.write(0, 0, "Slot")
                for O in Olist:
                    sheet.write(0, O*(n_num)+1, "Pro_f"+str(O))
                    for n in range(1,n_num):
                        sheet.write(0, O*(n_num)+n+1, "T"+str(n))
                for OC in OClist:
                    sheet.write(0, OC+numO*(n_num)+1, "OC"+str(OC))
                for O in Olist:
                    sheet.write(0, O+numOC+numO*(n_num)+1, "O"+str(O))
                sheet.write(0, numO+numOC+numO*(n_num)+1, "CRO_in")
                sheet.write(0, numO+numOC+numO*(n_num)+4, "JIV93")
                sheet.write(0, numO+numOC+numO*(n_num)+6, "JIV97")
                sheet.write(0, numO+numOC+numO*(n_num)+8, "G3I90")
                sheet.write(0, numO+numOC+numO*(n_num)+10, "G3I93")
                sheet.write(0, numO+numOC+numO*(n_num)+12, "G3I97")
                sheet.write(0, numO+numOC+numO*(n_num)+14, "G3I0")
                sheet.write(0, numO+numOC+numO*(n_num)+16, "G3I10")
                sheet.write(0, numO+numOC+numO*(n_num)+18, "GIV0")
                sheet.write(0, numO+numOC+numO*(n_num)+20, "OC0")
                sheet.write(0, numO+numOC+numO*(n_num)+22, "OC1")
                sheet.write(0, numO+numOC+numO*(n_num)+24, "OC2")
                sheet.write(0, numO+numOC+numO*(n_num)+26, "OC3")
                sheet.write(0, numO+numOC+numO*(n_num)+28, "OC4")
                sheet.write(0, numO+numOC+numO*(n_num)+30, "OC5")
                sheet.write(0, numO+numOC+numO*(n_num)+32, "OC6")
                sheet.write(0, numO+numOC+numO*(n_num)+34, "OC7")
                sheet.write(0, numO+numOC+numO*(n_num)+36, "CRO_in")
                sheet.write(0, numO+numOC+numO*(n_num)+37, "JIV93")
                sheet.write(0, numO+numOC+numO*(n_num)+38, "JIV97")
                sheet.write(0, numO+numOC+numO*(n_num)+39, "G3I90")
                sheet.write(0, numO+numOC+numO*(n_num)+40, "G3I93")
                sheet.write(0, numO+numOC+numO*(n_num)+41, "G3I97")
                sheet.write(0, numO+numOC+numO*(n_num)+42, "G3I0")
                sheet.write(0, numO+numOC+numO*(n_num)+43, "G3I10")
                sheet.write(0, numO+numOC+numO*(n_num)+44, "GIV0")
                sheet.write(0, numO+numOC+numO*(n_num)+45, "OC0")
                sheet.write(0, numO+numOC+numO*(n_num)+46, "OC1")
                sheet.write(0, numO+numOC+numO*(n_num)+47, "OC2")
                sheet.write(0, numO+numOC+numO*(n_num)+48, "OC3")
                sheet.write(0, numO+numOC+numO*(n_num)+49, "OC4")
                sheet.write(0, numO+numOC+numO*(n_num)+50, "OC5")
                sheet.write(0, numO+numOC+numO*(n_num)+51, "OC6")
                sheet.write(0, numO+numOC+numO*(n_num)+52, "OC7")

                for T in Tlist:
                    sheet.write(T+1, 0, str(T))
                    for O in Olist:
                        for n in range(0,n_num):
                            Prod_f_sum = 0
                            for L in Llist1:
                                Prod_f_sum += Prod_flow[T,O,L,n]
                            sheet.write(T+1, 1+(O*(n_num)+n), round(Prod_f_sum, 6))
                for T in [Tlist[0]]:
                    for OC in OClist:
                        sheet.write(T + 1, OC + numO*(n_num) + 1, round(OCtank_ini[OC], 6))
                    for O in Olist:
                        sheet.write(T + 1, O + numOC + numO*(n_num) + 1, round(Otank_ini[O], 6))
                for T in Tlist[1:]:
                    for OC in OClist:
                        sheet.write(T+1, OC+numO*(n_num)+1, round(OC_inventory[OC * numT + T-1], 6))
                    for O in Olist:
                        sheet.write(T+1, O+numOC+numO*(n_num)+1, round(O_inventory[O * numT + T-1], 6))
                for T in Tlist:
                    if (FinM[0 * numM * numT + 0 * numT + T]+FinM[0 * numM * numT + 1 * numT + T])*hours <= 200:
                        sheet.write(T+1, numO+numOC+numO*(n_num)+1, 1)
                        sheet.write(T+1, numO+numOC+numO*(n_num)+2, 0)
                        sheet.write(T+1, numO+numOC+numO*(n_num)+3, 0)
                    elif 200 < (FinM[0 * numM * numT + 0 * numT + T]+FinM[0 * numM * numT + 1 * numT + T])*hours < 300:
                        sheet.write(T+1, numO+numOC+numO*(n_num)+1, 0)
                        sheet.write(T+1, numO+numOC+numO*(n_num)+2, 1)
                        sheet.write(T+1, numO+numOC+numO*(n_num)+3, 0)
                    elif 300 <= (FinM[0 * numM * numT + 0 * numT + T]+FinM[0 * numM * numT + 1 * numT + T])*hours:
                        sheet.write(T+1, numO+numOC+numO*(n_num)+1, 0)
                        sheet.write(T+1, numO+numOC+numO*(n_num)+2, 0)
                        sheet.write(T+1, numO+numOC+numO*(n_num)+3, 1)
                for T in Tlist[1:]:
                    for O in Olist:
                        if sum([FOout[O * numL1 * numT + L * numT + T] for L in Llist1])+O_inventory[O * numT + T]-O_inventory[O * numT + T-1] > 0:
                            sheet.write(T+1, numO+numOC+numO*(n_num)+4+2*O, 0)
                            sheet.write(T+1, numO+numOC+numO*(n_num)+4+2*O+1, 1)
                        else:
                            sheet.write(T+1, numO+numOC+numO*(n_num)+4+2*O, 1)
                            sheet.write(T+1, numO+numOC+numO*(n_num)+4+2*O+1, 0)
                for T in [Tlist[0]]:
                    for O in Olist:
                        if sum([FOout[O * numL1 * numT + L * numT + T] for L in Llist1])+O_inventory[O * numT + T]-Otank_ini[O] > 0:
                            sheet.write(T+1, numO+numOC+numO*(n_num)+4+2*O, 0)
                            sheet.write(T+1, numO+numOC+numO*(n_num)+4+2*O+1, 1)
                        else:
                            sheet.write(T+1, numO+numOC+numO*(n_num)+4+2*O, 1)
                            sheet.write(T+1, numO+numOC+numO*(n_num)+4+2*O+1, 0)
                for T in Tlist:
                    for OC in OClist:
                        if Qout[OC * numT + T] > 0:
                            sheet.write(T+1, numO+numOC+numO*(n_num)+4+2*numO+OC*2, 0)
                            sheet.write(T+1, numO+numOC+numO*(n_num)+4+2*numO+OC*2+1, 1)
                        else:
                            sheet.write(T+1, numO+numOC+numO*(n_num)+4+2*numO+OC*2, 1)
                            sheet.write(T+1, numO+numOC+numO*(n_num)+4+2*numO+OC*2+1, 0)
                for T in Tlist:
                    sheet.write(T+1, numO+numOC+numO*(n_num)+4+2*numO+2*numOC, round((FinM[0 * numM * numT + 0 * numT + T]+
                                                               FinM[0 * numM * numT + 1 * numT + T])*hours, 6))
                for T in [Tlist[0]]:
                    for O in Olist:
                        sheet.write(T+1, numO+numOC+numO*(n_num)+5+2*numO+2*numOC+O,
                                    round(sum([FOout[O * numL1 * numT + L * numT + T] for L in Llist1])+O_inventory[O * numT + T]-Otank_ini[O], 6))
                for T in Tlist[1:]:
                    for O in Olist:
                        sheet.write(T+1, numO+numOC+numO*(n_num)+5+2*numO+2*numOC+O,
                                    round(sum([FOout[O * numL1 * numT + L * numT + T] for L in Llist1])+O_inventory[O * numT + T]-O_inventory[O * numT + T-1], 6))
                for T in Tlist:
                    for OC in OClist:
                        sheet.write(T+1, numO+numOC+numO*(n_num)+5+2*numO+numO+2*numOC+OC, round(Qout[OC * numT + T], 6))

                for L in Llist1:
                    sheet.write(L+numT+1+2, 0, "L"+str(L))
                    for O in Olist:
                        sheet.write(L+numT + 1 + 2, O+1, DV1[L,O])
                for L in Llist1:
                    sheet.write(L+numL1+2+numT+1+2, 0, "L"+str(L))
                    sheet.write(L+numL1+2+numT+1+2, 1, DS_num[L,0])
                    sheet.write(L+numL1+2+numT+1+2, 2, DS_num[L,1])

                sheet.write(numL1+2+numL1+2+numL1+2+numT+1+2, 0, "Slot")
                for T in Tlist:
                    sheet.write(2+numL1+2+numL1+2+numT+1+2, T+1, "slot"+str(T))
                for L in Llist1:
                    sheet.write(L+1+2+numL1+2+numL1+2+numT+1+2, 0, "L"+str(L))
                    for T in Tlist:
                        sheet.write(L+1+2+numL1+2+numL1+2+numT+1+2, T+1, DS1[L,T])
            book.save('PRO_NN_n-num_case_9allslot1'+'.xls')

        elif CASE[i] == 'VS-case1-4slots-VF1':
            VF = 1                                   # with or without Valid Functions
            numT = 30
            TC = "time"                             # Termination_condition: gap or time
            if TC == "gap":
                gap = 0.01
                time = 0
                case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
            elif TC == "time":
                gap = 0.0
                time = 600
                case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
            Tlist = range(numT)
            numL = 8  # order quantity
            numL_g = 5
            numL_d = 3
            L_glist = range(numL_g)
            L_dlist = range(numL_d)
            Tarr = [1, 8, 14]
            Vessel_V = [10000.0,10000.0,10000.0]
            Initial_S = [6880.0,6200.0,6000.0]
            Initial_B = [8320.0,7200.0,6000.0]
            # DS = [[1,1,1,0,1,1,0,0,0,0],[1,1,1,0,1,1,0,0,0,0],[1,1,1,0,1,1,0,0,0,0],[0,1,1,1,1,1,0,0,0,0],
            #       [0,1,1,1,1,1,1,1,1,1],[1,1,1,0,1,1,1,1,1,1],[1,1,1,0,1,1,1,1,1,1],[0,1,1,1,1,1,1,1,1,1]]
            DS_num = [[0,10],[0,10],[0,10],[10,20],[10,20],[0,10],[0,10],[10,20]]
            DS = [[1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1]]
            DP_num = [0,3,4,2,1,             6,7,8]  # no unloading oil. so the order needed is what tank.
            # DV = [400,500,300,300,300,    1200,1000,1400]
            DV = [240,300,180,180,180,    720,600,840]
            numL1 = 3
            Llist1 = range(numL1)
            DS1 = [[1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                   [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1]]
            DS_num = [[0,15],[0,19],[10,29]]
            # DV1 = [[400,0,0,500,0,    1200,0,0],[0,0,0,0,300,    0,1000,0],[0,300,300,0,0,    0,0,1400]]
            # DV1 = [[400,500,0,0,0,    1200,0,0],[0,0,300,0,0,    0,1000,0],[0,0,0,300,300,    0,0,1400]]
            DV1 = [[400,300,0,0,0,    720,0,0],[0,0,180,0,0,    0,600,0],[0,0,0,180,180,    0,0,840]]
            DP = [[1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],[0,0,0,0,1,0,0,0],[0,0,1,0,0,0,0,0],
                  [0,1,0,0,0,0,0,0],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1]]
            Pri = 0
            num_sample = 1000
            n_num = 10
            book = xlwt.Workbook(encoding='utf-8', style_compression=0)
            for sample in range(num_sample):
                print "############################# sample:",sample,"################"
                OCtank_ini_1 = np.random.randint(0,101,(numO))
                OCtank_ini_2 = np.random.randint(0,201,(numO))
                OCtank_ini = np.hstack((OCtank_ini_1,OCtank_ini_2))
                Otank_ini_1 = np.random.randint(0,151,(numO))
                Otank_ini_2 = np.random.randint(0,301,(numO))
                Otank_ini = np.hstack((Otank_ini_1,Otank_ini_2))
                numL1 = np.random.randint(1, 7)  # for 1-6
                Llist1 = range(numL1)
                DV1_1 = np.random.randint(0,301,(numL1,numO_g))
                DV1_2 = np.random.randint(50,501,(numL1,numO_d))
                DV1 = np.hstack((DV1_1,DV1_2))
                DS_num = np.zeros((numL1,2))
                DS1 = np.zeros((numL1,numT))
                for L1 in Llist1:
                    if L1 == 0:
                        DS_num[L1,0] = 0
                    else:
                        DS_num[L1,0] = np.random.randint(0,30-3) # 3 means the shortest length of order duration.
                    if L1 == Llist1[-1]:
                        DS_num[L1,1] = 29
                    else:
                        DS_num[L1,1] = np.random.randint(min(29,DS_num[L1,0]+3),30)
                    DS1[L1,DS_num[L1,0].astype(int):DS_num[L1,1].astype(int)+1] = 1

                Obj_value, FOout, OC_inventory, O_inventory, Mode_act,FinM = PRO_opt(numT,Tlist,numL1,Llist1,DS1,DV1,Pri,DS_num,sample,OCtank_ini,Otank_ini)
                Prod_flow = np.zeros((numT,numO,numL1))
                Prod_sum = np.zeros((numT,numO))
                FOout_sum = np.zeros((numL1,numO))
                Oout_sum = np.zeros((numT,numO))
                for O in Olist:
                    for L in Llist1:
                        for T in Tlist:
                            if T >= 1:
                                FOout_sum[L,O] += FOout[O * numL1 * numT + L * numT + T-1]
                            if T <= DS_num[L][1]:
                                Prod_flow[T,O,L] = (DV1[L][O] - FOout_sum[L,O] * hours) / (DS_num[L][1] - T + 1)

                sheet = book.add_sheet('case'+str(sample), cell_overwrite_ok=True)
                sheet.write(0, 0, "Slot")
                for O in Olist:
                    sheet.write(0, O*(n_num+2)+1, "Pro_f"+str(O))
                    for n in range(1,n_num+1):
                        sheet.write(0, O*(n_num+2)+n+1, "T"+str(n))
                    sheet.write(0, O*(n_num+2)+n_num+1+1, "TF")
                for OC in OClist:
                    sheet.write(0, OC+numO*(n_num+2)+1, "OC"+str(OC))
                for O in Olist:
                    sheet.write(0, O+numOC+numO*(n_num+2)+1, "O"+str(O))
                sheet.write(0, numO+numOC+numO*(n_num+2)+1, "CRO_in")
                sheet.write(0, 1+numO+numOC+numO*(n_num+2)+1, "JIV93")
                sheet.write(0, 2+numO+numOC+numO*(n_num+2)+1, "JIV97")
                sheet.write(0, 3+numO+numOC+numO*(n_num+2)+1, "G3I90")
                sheet.write(0, 4+numO+numOC+numO*(n_num+2)+1, "G3I93")
                sheet.write(0, 5+numO+numOC+numO*(n_num+2)+1, "G3I97")
                sheet.write(0, 6+numO+numOC+numO*(n_num+2)+1, "G3I0")
                sheet.write(0, 7+numO+numOC+numO*(n_num+2)+1, "G3I10")
                sheet.write(0, 8+numO+numOC+numO*(n_num+2)+1, "GIV0")

                for T in Tlist:
                    sheet.write(T+1, 0, str(T))
                    for O in Olist:
                        for n in range(0,n_num+1):
                            Prod_f_sum = 0
                            for L in Llist1:
                                if T+n >= DS_num[L][0] and T+n <= DS_num[L][1]:
                                    Prod_f_sum += Prod_flow[T,O,L]
                            sheet.write(T+1, 1+(O*(n_num+2)+n), round(Prod_f_sum, 6))
                        Prod_sum = 0
                        for L in Llist1:
                            if T+n_num+1 <= DS_num[L][1]:
                                Prod_sum += Prod_flow[T,O,L]
                        sheet.write(T+1, 1+(O*(n_num+2)+n_num+1), round(Prod_sum,6))
                for T in [Tlist[0]]:
                    for OC in OClist:
                        sheet.write(T + 1, OC + numO*(n_num+2) + 1, round(OCtank_ini[OC], 6))
                    for O in Olist:
                        sheet.write(T + 1, O + numOC + numO*(n_num+2) + 1, round(Otank_ini[O], 6))
                for T in Tlist[1:]:
                    for OC in OClist:
                        sheet.write(T+1, OC+numO*(n_num+2)+1, round(OC_inventory[OC * numT + T-1], 6))
                    for O in Olist:
                        sheet.write(T+1, O+numOC+numO*(n_num+2)+1, round(O_inventory[O * numT + T-1], 6))
                for T in Tlist:
                    sheet.write(T+1, numO+numOC+numO*(n_num+2)+1, round((FinM[0 * numM * numT + 0 * numT + T]+
                                                               FinM[0 * numM * numT + 1 * numT + T])*hours, 6))
                for T in Tlist:
                    for O in Olist:
                        sheet.write(T+1, O+numO+numOC+numO*(n_num+2)+2,
                                    round(sum([FOout[O * numL1 * numT + L * numT + T] for L in Llist1])+O_inventory[O * numT + T], 6))

                for L in Llist1:
                    sheet.write(L+numT+1+2, 0, "L"+str(L))
                    for O in Olist:
                        sheet.write(L+numT + 1 + 2, O+1, DV1[L,O])
                for L in Llist1:
                    sheet.write(L+numL1+2+numT+1+2, 0, "L"+str(L))
                    sheet.write(L+numL1+2+numT+1+2, 1, DS_num[L,0])
                    sheet.write(L+numL1+2+numT+1+2, 2, DS_num[L,1])

                sheet.write(numL1+2+numL1+2+numL1+2+numT+1+2, 0, "Slot")
                for T in Tlist:
                    sheet.write(2+numL1+2+numL1+2+numT+1+2, T+1, "slot"+str(T))
                for L in Llist1:
                    sheet.write(L+1+2+numL1+2+numL1+2+numT+1+2, 0, "L"+str(L))
                    for T in Tlist:
                        sheet.write(L+1+2+numL1+2+numL1+2+numT+1+2, T+1, DS1[L,T])
            book.save('PRO_NN_n-num_4'+'.xls')

        elif CASE[i] == 'VS-case1-4slots-VF1-time35000':
            VF = 1                                   # with or without Valid Functions
            numT = 40
            TC = "time"                             # Termination_condition: gap or time
            if TC == "gap":
                gap = 0.0
                time = 0
                case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
            elif TC == "time":
                gap = 0.0
                time = 200
                case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
            Tlist = range(numT)
            numL = 8  # order quantity
            numL_g = 5
            numL_d = 3
            L_glist = range(numL_g)
            L_dlist = range(numL_d)
            Tarr = [1, 10, 20]
            Vessel_V = [8000.0,9000.0,8500.0]
            Initial_S = [1000.0,1000.0,1000.0]
            Initial_B = [6320.0,8200.0,8000.0]
            # DS = [[1,1,1,0,1,1,0,0,0,0],[1,1,1,0,1,1,0,0,0,0],[1,1,1,0,1,1,0,0,0,0],[0,1,1,1,1,1,0,0,0,0],
            #       [0,1,1,1,1,1,1,1,1,1],[1,1,1,0,1,1,1,1,1,1],[1,1,1,0,1,1,1,1,1,1],[0,1,1,1,1,1,1,1,1,1]]
            DS_num = [[0,2],[0,2],[0,2],[1,3],[1,3],[0,2],[0,2],[1,3]]
            DS = [[1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1]]
            DP_num = [0,3,4,2,1,             6,7,8]  # no unloading oil. so the order needed is what tank.
            DV = [400,500,300,300,300,    1200,1000,1400]
            numL1 = 2
            Llist1 = range(numL1)
            DS1 = [[1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1]]
            DV1 = [[400,0,0,300,300,1200,1000,0],[0,500,300,0,0,0,0,1400]]
            DP = [[1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],[0,0,0,0,1,0,0,0],[0,0,1,0,0,0,0,0],
                  [0,1,0,0,0,0,0,0],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1]]
            SA(VF,numT,TC,gap,time,case,Tlist,numL,numL_g,numL_d,L_glist,L_dlist,Tarr,Vessel_V,Initial_S,Initial_B,DS,DS_num,DP_num,DV,DP)

        elif CASE[i] == "VS-case1-4slots-VF1-gap24":
            VF = 1                                   # with or without Valid Functions
            numT = 40
            TC = "gap"                             # Termination_condition: gap or time
            if TC == "gap":
                gap = 0.0
                time = 0
                case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
            elif TC == "time":
                gap = 0.0
                time = 20000
                case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
            Tlist = range(numT)
            numL = 8  # order quantity
            numL_g = 5
            numL_d = 3
            L_glist = range(numL_g)
            L_dlist = range(numL_d)
            Tarr = [10, 20, 30]
            Vessel_V = [10000.0,10000.0,10000.0]
            Initial_S = [6880.0,6200.0,6000.0]
            Initial_B = [8320.0,7200.0,6000.0]
            # DS = [[1,1,1,0,1,1,0,0,0,0],[1,1,1,0,1,1,0,0,0,0],[1,1,1,0,1,1,0,0,0,0],[0,1,1,1,1,1,0,0,0,0],
            #       [0,1,1,1,1,1,1,1,1,1],[1,1,1,0,1,1,1,1,1,1],[1,1,1,0,1,1,1,1,1,1],[0,1,1,1,1,1,1,1,1,1]]
            DS_num = [[0,2],[0,2],[0,2],[1,3],[1,3],[0,2],[0,2],[1,3]]
            DS = [[1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1]]
            DP_num = [0,3,4,2,1,             6,7,8]  # no unloading oil. so the order needed is what tank.
            DV = [400,500,300,300,300,    1200,1000,1400]
            DP = [[1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],[0,0,0,0,1,0,0,0],[0,0,1,0,0,0,0,0],
                  [0,1,0,0,0,0,0,0],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1]]
            SA(VF,numT,TC,gap,time,case,Tlist,numL,numL_g,numL_d,L_glist,L_dlist,Tarr,Vessel_V,Initial_S,Initial_B,DS,DS_num,DP_num,DV,DP)
            numL = 14  # order quantity
            numL_g = 8
            numL_d = 6
            L_glist = range(numL_g)
            L_dlist = range(numL_d)
            Tarr = [1, 2, 4]
            Vessel_V = [10000.0,8000.0,7000.0]
            Initial_S = [6880.0,6200.0,7000.0]
            Initial_B = [5320.0,8200.0,6320.0]
            DS = [[1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0],
                  [1,1,1,1,0,1,1,1,1,1],[0,0,1,1,1,1,1,1,1,1],[0,0,1,1,1,1,1,1,1,1],[0,0,1,1,1,1,1,1,1,1],
                  [1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0],
                  [0,0,1,1,1,1,1,1,1,1],[0,0,1,1,1,1,1,1,1,1],[0,0,1,1,1,1,1,1,1,1]]
            DS_num = [[0,3],[0,3],[0,3],[0,3],[0,3],[2,5],[2,5],[2,5],      [0,3],[0,3],[0,3],[2,5], [2,5],[2,5]]
            DP_num = [0,3,4,2,1,2,1,3,           6,7,8,6,7,8]  # no unloading oil. so the order needed is what tank.
            DV = [350,400,300,300,300,400,300,200,    900,500,1000,1100,500,1000]
            DP = [[1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],[0,0,0,0,1,0,0,0],[0,0,1,0,0,0,0,0],
                  [0,1,0,0,0,0,0,0],[0,0,1,0,0,0,0,0],[0,1,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1]]

        elif CASE[i] == 'VS-case1-6slots-VF1':
            VF = 1                                   # with or without Valid Functions
            numT = 60
            TC = "time"                             # Termination_condition: gap or time
            if TC == "gap":
                gap = 0.0
                time = 0
                case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
            elif TC == "time":
                gap = 0.0
                time = 40000
                case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
            Tlist = range(numT)
            numL = 14  # order quantity
            numL_g = 8
            numL_d = 6
            L_glist = range(numL_g)
            L_dlist = range(numL_d)
            Tarr = [10, 20, 40]
            Vessel_V = [10000.0,8000.0,7000.0]
            Initial_S = [6880.0,6200.0,7000.0]
            Initial_B = [5320.0,8200.0,6320.0]
            DS = [[1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1]]
            DS_num = [[0,3],[0,3],[0,3],[0,3],[0,3],[2,5],[2,5],[2,5],      [0,3],[0,3],[0,3],[2,5], [2,5],[2,5]]
            DP_num = [0,3,4,2,1,2,1,3,           6,7,8,6,7,8]  # no unloading oil. so the order needed is what tank.
            DV = [350,400,300,300,300,400,300,200,    900,500,1000,1100,500,1000]
            DP = [[1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],[0,0,0,0,1,0,0,0],[0,0,1,0,0,0,0,0],
                  [0,1,0,0,0,0,0,0],[0,0,1,0,0,0,0,0],[0,1,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1]]
            SA(VF,numT,TC,gap,time,case,Tlist,numL,numL_g,numL_d,L_glist,L_dlist,Tarr,Vessel_V,Initial_S,Initial_B,DS,DS_num,DP_num,DV,DP)

        elif CASE[i] == 'VS-case1-5slots-VF1':
            VF = 1                                   # with or without Valid Functions
            numT = 50
            TC = "time"                             # Termination_condition: gap or time
            if TC == "gap":
                gap = 0.20
                time = 0
                case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
            elif TC == "time":
                gap = 0.0
                time = 3600
                case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
            Tlist = range(numT)
            numL = 10  # order quantity
            numL_g = 6
            numL_d = 4
            L_glist = range(numL_g)
            L_dlist = range(numL_d)
            Tarr = [10, 20, 30]
            Vessel_V = [5000.0,5000.0,5000.0]
            Initial_S = [7880.0,7200.0,6000.0]
            Initial_B = [6320.0,6200.0,5320.0]
            DS = [[1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1]]
            DS_num = [[0,3],[0,3],[0,3],[0,3],[0,3],[2,4],      [0,3],[0,3],[0,3],[2,5], [2,5],[2,5]]
            DP_num = [0,3,4,2,1,2,           6,7,8,6,7,8]  # no unloading oil. so the order needed is what tank.
            DV = [350,400,300,300,300,400,    1000,500,1000,500,500,1000]
            numL1 = 2
            Llist1 = range(numL1)
            DS1 = [[1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1]]
            DV1 = [[350,400,0,300,300,0,    1000,500,0,0,0,0],[0,0,300,0,0,400,    0,0,1000,500,500,1000]]
            DP = [[1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],[0,0,0,0,1,0,0,0],[0,0,1,0,0,0,0,0],
                  [0,1,0,0,0,0,0,0],[0,0,1,0,0,0,0,0],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1]]
            SA(VF,numT,TC,gap,time,case,Tlist,numL,numL_g,numL_d,L_glist,L_dlist,Tarr,Vessel_V,Initial_S,Initial_B,DS,DS_num,DP_num,DV,DP)

            # numL = 10  # order quantity
            # numL_g = 6
            # numL_d = 4
            # L_glist = range(numL_g)
            # L_dlist = range(numL_d)
            # Tarr = [1, 2, 3]
            # Vessel_V = [5000.0,5000.0,5000.0]
            # Initial_S = [7880.0,7200.0,6000.0]
            # Initial_B = [6320.0,6200.0,5320.0]
            # DS = [[1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0],
            #       [1,1,1,1,0,0,0,0,0,0],[0,0,1,1,1,1,1,1,1,1],
            #       [1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0],
            #       [0,0,1,1,1,1,1,1,1,1],[0,0,1,1,1,1,1,1,1,1],[0,0,1,1,1,1,1,1,1,1]]
            # DS_num = [[0,3],[0,3],[0,3],[0,3],[0,3],[2,5],     [0,3],[0,3],[0,3],[2,5], [2,5],[2,5]]
            # DP_num = [0,3,4,2,1,2,           6,7,8,6,7,8]  # no unloading oil. so the order needed is what tank.
            # DV = [350,400,300,300,300,400,    1000,500,1000,500,500,1000]
            # DP = [[1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],[0,0,0,0,1,0,0,0],[0,0,1,0,0,0,0,0],
            #       [0,1,0,0,0,0,0,0],[0,0,1,0,0,0,0,0],
            #       [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1],
            #       [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1]]        elif CASE[i] == 'VS-case1-5slots-VF1':

        elif CASE[i] == 'VS-case1-5slots-VF1-':
            VF = 1                                   # with or without Valid Functions
            numT = 50
            TC = "time"                             # Termination_condition: gap or time
            if TC == "gap":
                gap = 0.01
                time = 0
                case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
            elif TC == "time":
                gap = 0.0
                time = 600
                case = 'VS-case1-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
            Tlist = range(numT)
            numL = 10  # order quantity
            numL_g = 6
            numL_d = 4
            L_glist = range(numL_g)
            L_dlist = range(numL_d)
            Tarr = [10, 20, 30]
            Vessel_V = [5000.0,5000.0,5000.0]
            Initial_S = [7880.0,7200.0,6000.0]
            Initial_B = [6320.0,6200.0,5320.0]
            DS = [[1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1]]
            DS_num = [[0,3],[0,3],[0,3],[0,3],[0,3],[2,4],      [0,3],[0,3],[0,3],[2,5], [2,5],[2,5]]
            DP_num = [0,3,4,2,1,2,           6,7,8,6,7,8]  # no unloading oil. so the order needed is what tank.
            DV = [350,400,300,300,300,400,    1000,500,1000,500,500,1000]
            numL1 = 2
            Llist1 = range(numL1)
            DS1 = [[1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1]]
            DV1 = [[350,400,0,300,300,0,    1000,500,0,0,0,0],[0,0,300,0,0,400,    0,0,1000,500,500,1000]]
            DP = [[1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],[0,0,0,0,1,0,0,0],[0,0,1,0,0,0,0,0],
                  [0,1,0,0,0,0,0,0],[0,0,1,0,0,0,0,0],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1]]
            SA(VF,numT,TC,gap,time,case,Tlist,numL,numL_g,numL_d,L_glist,L_dlist,Tarr,Vessel_V,Initial_S,Initial_B,DS,DS_num,DP_num,DV,DP)

            # numL = 10  # order quantity
            # numL_g = 6
            # numL_d = 4
            # L_glist = range(numL_g)
            # L_dlist = range(numL_d)
            # Tarr = [1, 2, 3]
            # Vessel_V = [5000.0,5000.0,5000.0]
            # Initial_S = [7880.0,7200.0,6000.0]
            # Initial_B = [6320.0,6200.0,5320.0]
            # DS = [[1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0],
            #       [1,1,1,1,0,0,0,0,0,0],[0,0,1,1,1,1,1,1,1,1],
            #       [1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0],
            #       [0,0,1,1,1,1,1,1,1,1],[0,0,1,1,1,1,1,1,1,1],[0,0,1,1,1,1,1,1,1,1]]
            # DS_num = [[0,3],[0,3],[0,3],[0,3],[0,3],[2,5],     [0,3],[0,3],[0,3],[2,5], [2,5],[2,5]]
            # DP_num = [0,3,4,2,1,2,           6,7,8,6,7,8]  # no unloading oil. so the order needed is what tank.
            # DV = [350,400,300,300,300,400,    1000,500,1000,500,500,1000]
            # DP = [[1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],[0,0,0,0,1,0,0,0],[0,0,1,0,0,0,0,0],
            #       [0,1,0,0,0,0,0,0],[0,0,1,0,0,0,0,0],
            #       [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1],
            #       [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1]]        elif CASE[i] == 'VS-case1-5slots-VF1':

        elif CASE[i] == 'VS-case2-8slots-VF1':
            VF = 1                                   # with or without Valid Functions
            numT = 80
            TC = "time"                             # Termination_condition: gap or time
            if TC == "gap":
                gap = 0.0
                time = 0
                case = 'VS-case2-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
            elif TC == "time":
                gap = 0.0
                time = 40000
                case = 'VS-case2-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
            Tlist = range(numT)
            numL = 14  # order quantity
            numL_g = 8
            numL_d = 6
            L_glist = range(numL_g)
            L_dlist = range(numL_d)
            Tarr = [10, 40, 70]
            Vessel_V = [10000.0,10000.0,10000.0]
            Initial_S = [2880.0,7200.0,10000.0]
            Initial_B = [4320.0,7200.0,4320.0]
            DS = [[1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1]]
            DS_num = [[0,5],[0,5],[0,5],[0,5],[2,7],[2,7],[2,7],[2,7],   [0,5],[0,5],[0,5],[2,7],[2,7],[2,7]]
            DP_num = [0,3,4,2,1,2,1,3,             6,7,8,6,7,8,6,8]  # no unloading oil. so the order needed is what tank.
            DV = [400,500,300,300,300,300,350,300,    1500,1000,1600,2000,1000,1600]
            DP = [[1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],[0,0,0,0,1,0,0,0],[0,0,1,0,0,0,0,0],
                  [0,1,0,0,0,0,0,0],[0,0,1,0,0,0,0,0],[0,1,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,1],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1]]
            refinery(VF,numT,TC,gap,time,case,Tlist,numL,numL_g,numL_d,L_glist,L_dlist,Tarr,Vessel_V,Initial_S,Initial_B,DS,DS_num,DP_num,DV,DP)

        elif CASE[i] == 'VS-case2-8slots-VF1-revise':
            VF = 1                                   # with or without Valid Functions
            numT = 80
            TC = "time"                             # Termination_condition: gap or time
            if TC == "gap":
                gap = 0.0
                time = 0
                case = 'VS-case2-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(gap)+'%'
            elif TC == "time":
                gap = 0.0
                time = 40000
                case = 'VS-case2-VF'+str(VF)+'-'+str(numT)+'slots'+TC+'-'+str(time)+'s'
            Tlist = range(numT)
            numL = 14  # order quantity
            numL_g = 8
            numL_d = 6
            L_glist = range(numL_g)
            L_dlist = range(numL_d)
            Tarr = [10, 40, 70]
            Vessel_V = [10000.0,10000.0,10000.0]
            Initial_S = [2880.0,7200.0,10000.0]
            Initial_B = [4320.0,7200.0,4320.0]
            # DS = [[1,1,1,1,1,1,1,1,0,0],[1,1,1,1,1,1,1,1,0,0],[1,1,1,1,1,1,1,1,0,0],[1,1,1,1,1,1,1,1,0,0],[1,1,1,1,1,1,1,1,0,0],
            #       [0,0,0,1,1,1,1,1,1,1],[1,1,1,1,0,0,0,0,1,1],[1,1,1,1,0,0,0,0,1,1], # 20181022: found a wrong: the first [1,1,1,1,1,1,0,0,0,0] be [0,0,1,1,1,1,1,1,1,1]
            #       [1,1,1,1,1,1,1,0,0,0],[1,1,1,1,1,1,1,0,0,0],[1,1,1,1,1,1,1,0,0,0],
            #       [0,0,0,1,1,1,1,1,1,1],[1,1,1,1,0,0,0,0,1,1],[1,1,1,1,0,0,0,0,1,1]]
            # DS_num = [[0,5],[0,5],[0,5],[0,5],[0,5],[2,7],[2,7],[2,7],     [0,5],[0,5],[0,5],[3,7],[3,7],[3,7]]
            # DP_num = [0,3,4,2,1, 2, 1,3,             6,7,8,6,7,8]  # no unloading oil. so the order needed is what tank.
            # DV = [400,500,300,300,300,  300,  350,300,   1600,1000,2000,  1000,1000,1600]
            # DP = [[1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],[0,0,0,0,1,0,0,0],[0,0,1,0,0,0,0,0],[0,1,0,0,0,0,0,0],
            #       [0,0,1,0,0,0,0,0],[0,1,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],
            #       [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1],
            #       [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1]]
            DS = [[1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0],
                  [1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0]]
            DS_num = [[0,5],[0,5],[0,5],[0,5],[2,7],[2,7],[2,7],[2,7],   [0,5],[0,5],[0,5],[2,7],[2,7],[2,7]]
            DP_num = [0,3,4,2,1,2,1,3,             6,7,8,6,7,8,6,8]  # no unloading oil. so the order needed is what tank.
            DV = [400,500,300,300,300,300,350,300,    1600,1000,2000,  1000,1000,1600]
            DP = [[1,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],[0,0,0,0,1,0,0,0],[0,0,1,0,0,0,0,0],
                  [0,1,0,0,0,0,0,0],[0,0,1,0,0,0,0,0],[0,1,0,0,0,0,0,0],[0,0,0,1,0,0,0,0],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,1,0],
                  [0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,1],[0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1]]
            refinery(VF,numT,TC,gap,time,case,Tlist,numL,numL_g,numL_d,L_glist,L_dlist,Tarr,Vessel_V,Initial_S,Initial_B,DS,DS_num,DP_num,DV,DP)

CASE = [
        # 'ShiL-case1',
        # "12s3o",
        "18s3o",
        # 'VS-case1-10slots-Atuo',
        # 'VS-case1-10slots-40-2-600s',
        # 'VS-case1-10slots-60-1',
        # 'VS-case1-10slots-60-2',
        # 'VS-case1-10slots-100-1',
        # 'VS-case1-10slots-new',
        # 'VS-case1-10slots-VF1',
        # 'VS-case1-5slots-VF1-',
        # 'VS-case1-4slots-VF1',
        # 'VS-case1-4slots-VF1-time35000',
        # 'VS-case1-5slots-VF1',
        # 'VS-case1-6slots-VF1'
        # "VS-case1-4slots-VF1-gap24",
        # 'VS-case2-8slots-VF1'
        # 'VS-case2-8slots-VF1-revise'
        ]
# run(CASE)
