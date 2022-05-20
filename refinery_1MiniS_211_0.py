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

numT = 8
Tlist = range(numT)
R = [[10.,40.,20.,10.,55.,100.,60.,70.],
     [20.,30.,10.,10.,70.,80.,70.,90.]] # numL*numO
RT = [[1.,6.],[3.,8.]] # numL*2
QIinputL = [200.,300.,0.,300.,0.,300.,0.,300.,0.,300.,0.,300.,0.,300.,0.,300.,0.,300.]  # numU*2
# Parameter tYield
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

def buildmodel(prob,numT, Tlist, numL, Llist, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode):
    prob.objective.set_sense(prob.objective.sense.minimize)
    # list number is address, inlet is value. Orgenize the list number to get the value.  # ,QI_atm,QI_eth,QI_htu1
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
                        if T > 0 and T != Tlist[-1]:
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
                        if T > 0 and T != Tlist[-1]:
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
    # prob.variables.set_lower_bounds(zip(range(y_c, y_c + ycount), Mode))
    # prob.variables.set_upper_bounds(zip(range(y_c, y_c + ycount), Mode))
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
    

    return [y_c,ycount,x_c,xcount,xycount,xy_c,QI_c,QIcount,QO_c,QOcount,Otankout_c,Otankoutcount,Q_c,Qcount,OINV_c,OINVcount,
            xQI_c,xQIcount,xQI1_c,xQI1count,xyQI_c,xyQIcount,xyQI1_c,xyQI1count,OCcount,OC_c,OCINVcount,OCINV_c,
            OCtankoutcount,OCtankout_c]
global gap
def refinery(numT, Tlist, numL, Llist, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode):
    #,QI_atm,QI_eth,QI_htu1
    prob = cplex.Cplex()
    # prob.parameters.barrier.qcpconvergetol.set(1e-10)
    prob.parameters.mip.tolerances.mipgap.set(0)
    prob.parameters.timelimit.set(40)
    # if numT == 100:
    #     prob.parameters.timelimit.set(1200)
    # elif numT == 120:
    #     prob.parameters.timelimit.set(1400)
    # elif numT == 140:
    #     prob.parameters.timelimit.set(1600)
    # elif numT == 160:
    #     prob.parameters.timelimit.set(2000)
    # elif numT == 180:
    #     prob.parameters.timelimit.set(2400)
    # elif numT == 200:
    #     prob.parameters.timelimit.set(3000)
    [y_c,ycount,x_c,xcount,xycount,xy_c,QI_c,QIcount,QO_c,QOcount,Otankout_c,Otankoutcount,Q_c,Qcount,OINV_c,OINVcount,
            xQI_c,xQIcount,xQI1_c,xQI1count,xyQI_c,xyQIcount,xyQI1_c,xyQI1count,OCcount,OC_c,OCINVcount,OCINV_c,
            OCtankoutcount,OCtankout_c] = buildmodel(prob,
                                    numT, Tlist, numL, Llist, DS1, DV1, Pri, DS_num, sample, OCtank_ini, Otank_ini,Mode)
    # prob.write("refinery.lp")
    global gap
    class TimeLimitCallback(MIPInfoCallback):
        def __call__(self):
            global gap
            gap = self.get_MIP_relative_gap()
    timelim_cb = prob.register_callback(TimeLimitCallback)
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
    # print "sum xQI:",sum(M)
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
    return sol.get_objective_value(),  [QI[0*numT+T] for T in Tlist], gap    # + sum(sum(DV1[:numL])) * bp

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
