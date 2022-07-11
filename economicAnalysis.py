%  Licensing:
%
%    This code is distributed under the GNU GPL license.
%
%  Author:
%
%   Mohammed Raihan Uddin
%
% Paper:
%
%  https://doi.org/10.1016/j.wasman.2021.08.006

import math
import numpy as np
def economicAnalysis(m, T, X, mis):
    (bch, qFuel, qOut, wST1, wST2, wPump1, wPump2, wOut, eta,eta2) = mis

    Top = 8000
    i = 10 / 100
    N = 25
    CRF = (i * ((1 + i) ** N)) / (((1 + i) ** N) - 1)

    PEC_WIU = 1.1 * ((275.8 * m[2] * 3.6 * 8000) + 18231500)  # msw in ton per year
    PEC_PCU = 1.1 * ((38.17 * m[2] * 3.6 * 8000) + 2500000)

    y = [0, 4745, 11820, 658, 6000, 3540, 1773]

    PEC_SG = y[1] * ((qFuel / (math.log(T[4] - T[5]))) ** 0.8) + y[2] * m[6] + y[3] * m[3]
    PEC_ST1 = y[4] * (wST1 ** 0.7)
    PEC_ST2 = y[4] * (wST2 ** 0.7)
    PEC_Pump1 = y[5] * (wPump1 ** 0.71)
    PEC_Pump2 = y[5] * (wPump2 ** 0.71)
    PEC_Cond = y[6] * m[1]
    PEC_Dea = 145315 * m[6] ** 0.7  ##

    components = ['INC ', 'SG ', 'HPST ', 'LPST ', 'COND ', 'FWP1 ', 'FWP2 ', 'DEA', 'PCU ']

    PEC_INC = ((PEC_WIU - PEC_PCU) * 607.5/444.2) - (PEC_SG * 607.5/550.8)
    CI = np.array([1, 1.1029, 1.1029, 1.1029, 1.1029, 1.1029, 1.1029, 1.091, 1.3676])

    PEC = np.array([PEC_INC, PEC_SG, PEC_ST1, PEC_ST2, PEC_Cond, PEC_Pump1, PEC_Pump2, PEC_Dea, PEC_PCU])

    zRate = PEC * CI * CRF * 1.06 / (Top)  # in $/hr

    # Exergoeconomic Analysis

    A = np.zeros((9, 9))
    B = np.zeros((9,1))
    irr = np.zeros(9)
    CXD = np.zeros(9)
    XF = np.zeros(9)
    XP = np.zeros(9)
    XL = np.zeros(9)
    f = np.zeros(9)

    c2 = 2 / 1e6  # waste cost rate 2 US/GJ --> Convert into KJ as X is in KW

    A[0][1] = X[15] + X[4]  # Incinerator

    A[1][1] = X[5] - X[4]  # SG
    A[1][2] = X[6]
    A[1][5] = -X[14]

    A[2][2] = X[7] - X[6]  # Turbine 1
    A[2][6] = wST1

    A[3][2] = X[10] - X[9]  # Turbine 2
    A[3][7] = wST2

    A[4][0] = X[1]  # Condenser
    A[4][2] = X[11] - X[10]

    A[5][2] = -X[11]  # Pump 1
    A[5][3] = X[12]
    A[5][8] = -wPump1

    A[6][4] = -X[13]  # Pump 2
    A[6][5] = X[14]
    A[6][8] = -wPump2

    A[7][2] = -X[8]  # Deaerator
    A[7][3] = -X[12]
    A[7][4] = X[13]

    A[8][6] = -wST1 # Average COE for pumps
    A[8][7] = -wST2
    A[8][8] = wST1 + wST2

    B = np.transpose(zRate[0:8] / 3600) # Leaving PCU
    B = np.append(B, 0)   # Average: cost of the work done on pump
    B[0] = B[0] + c2 * X[2]

    invA = np.linalg.inv(A)
    c = np.dot(invA, B)

    cStream = np.array([0, c[1], c2, 0, c[1], c[1], c[2],c[2],c[2],c[2],c[2],c[2],c[3],c[4],c[5],c[1]]) #--> USD/KJ
    C = cStream * X * 3600 #--> USD/hr

    cStream = cStream * 1e6 #--> USD/GJ

    # ['INC ', 'SG ', 'HPST ', 'LPST ', 'COND ', 'FWP1 ', 'FWP2 ', 'DEA', 'PCU ']
    XF[0] = X[2] + X[3]
    XP[0] = X[4] + X[15]

    XF[1] = X[4]
    XP[1] = X[6] - X[14] + X[5]

    XF[2] = X[6] - X[7]
    XP[2] = wST1

    XF[3] = X[9] - X[10]
    XP[3] = wST2

    XF[4] = X[10] + X[0]
    XP[4] = X[11] + X[1]

    XF[5] = wPump1
    XP[5] = X[12] - X[11]

    XF[6] = wPump2
    XP[6] = X[14] - X[13]

    XF[7] = X[12] + X[8]
    XP[7] = X[13]

    XF[8] = 0
    XP[8] = 0

    # Cost of exergy destruction in --> $/hr
    CXD[0] = c2
    CXD[1] = c[1]  # c4
    CXD[2] = c[6]  # cST1
    CXD[3] = c[7]
    CXD[4] = c[6]
    CXD[5] = c[8]
    CXD[6] = c[8]
    CXD[7] = c[2]
    CXD[8] = 0

    XD = XF - XP- XL

    CXD = CXD * (XD) * 3600
    c = c * 1e6 # --> USD/GJ

    # Exergoeconomic factor
    f[0:8] = ((zRate[0:8]) / ((zRate[0:8]) + CXD[0:8])) * 100
    class comClass:
        def __init__(self,name, PEC, zRate,XF,XP, XD, CXD,f):
            self.name = name
            self.PEC = PEC
            self.zRate = zRate
            self.XF = XF
            self.XP = XP
            self.XD = XD
            self.etaII = (XP / XF) * 100
            self.CXD = CXD
            self.f = f


    comList = []
    for i in range (0, len(components)):
        temp = comClass(components[i], PEC[i], zRate[i], XF[i], XP[i], XD[i], CXD[i],f[i])
        comList.append(temp)

    sumPEC = sum(PEC)
    sumZ = sum(zRate)
    sumXF = XF[0]
    sumXP = wOut
    sumXD = sum(XD) #Behzadi 2018
    sumCXD = sum(CXD)
    fPlant = (sum(zRate[0:8]) / (sum(zRate[0:8]) + sum(CXD[0:8]))) * 100
    cP = c[-1]/ 1e6
    pb = sumPEC / ((((wST1 + wST2)*3600) * Top * cP))

    total = [sumPEC, sumZ, sumXF, sumXP, sumXD ,(sumXP*100/sumXF), sumCXD, fPlant,pb]




    return (cStream, C, comList, total )

'''
    # Irreversibilities in --> kW
    irr[0] = X[2] + X[3] - X[4] - X[15]
    irr[1] = X[4] + X[14] - X[5] - X[6]
    irr[2] = X[6] - X[7] - wST1
    irr[3] = X[9] - X[10] - wST2
    irr[4] = X[10] - X[1] - X[11]
    irr[5] = X[11] + wPump1 - X[12]
    irr[6] = X[13] + wPump2 - X[14]
    irr[7] = X[8] + X[12] - X[13]

'''
