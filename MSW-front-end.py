import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
import sys
from energyAnalysis import *
from economicAnalysis import *

np.set_printoptions(formatter={'float': '{: .5f}'.format})

df = pd.read_csv("cycle-params.txt")
data = df.to_numpy()
(m, n) = np.shape(data)

for i in range (0, m):

    filename = str(i+1) + '-Result-'+ data[i][0] + '.txt'
    #sys.stdout = open(filename, "w")

    n = 16

    P = np.zeros(n)
    T = np.zeros(n)
    h = np.zeros(n)
    s = np.zeros(n)
    X = np.zeros(n)
    C = np.zeros(n)
    cStream = np.zeros(n)

    lhv = data[i][1]#9861.408716
    bch = data[i][2]#11633.12108 #fuelExergy(chemComp)
    mFuel = data[i][3] # 43.1253171
    mAir = data[i][4]#334.8551657

    mSteam = (16.070/5.68) * mFuel
    mLPST = (14.062/5.68) * mFuel
    m4 = mAir + (0.0261 * mAir) #Assumption
    mAsh = mAir + mFuel - m4
    mCW = (711.015/5.68) * mFuel
    m = [mCW, mCW, mFuel,mAir, m4, m4, mSteam, mSteam, mSteam-mLPST, mLPST, mLPST, mLPST, mLPST, mSteam, mSteam, mAsh]

    pHPST = 4162e3
    pLPST = 160e3  # np.linspace(100,3000,30)
    pCond =  7e3  # np.linspace(1,20,20) * 1e3

    pressure = (pHPST, pLPST, pCond)

    (P, T, h, s, X, mis) = energyAnalysis(m, lhv, bch, pressure)

    (cStream, C, comList, total) = economicAnalysis(m, T, X, mis)

    (bch, qFuel, qOut, wST1, wST2, wPump1, wPump2, wOut, eta1, eta2) = mis

    properties = ['LHV', 'bch', 'qFuel', 'qOut', 'wST1', 'wST2', 'wPump1', 'wPump2', 'wOut', 'eta1', 'eta2']

    print('City - ', data[i][0])
    print('\n\t\t****** Energy Analysis ****** \n')
    print('Plant Capacities[kW]-\n')

    for i in range(0, len(properties)):
        if i == 0:
            print(properties[i], '= %5.2f' % (lhv))
        else:
            print(properties[i], '= %5.2f' % (mis[i - 1]))
    print('MSW[t/hr]', '= %5.2f' % (m[2]*3.6))
    print('\n\nStream Properties-\n')

    print("%19s  %10s %10s %10s %10s %10s %10s" % (
    "Flow(kg/s)", "Temp(K)", "Pressure(kPa)" , "Enthalpy(kJ/kg)", "Entropy(kJ/kg.k)", "Exergy (kW)", "c (USD/GJ)"))
    for i in range(0, n):
        print("Point %2d %10.3f %10.3f %10.3f %11.3f %17.3f %17.3f %11.3f" % (i, m[i], T[i], P[i]/1000 , h[i], s[i], X[i], cStream[i]))

    print('\n\t\t****** Economic Analysis ****** \n')

    print("%s  %10s %10s %8s %10s %10s %12s %15s %8s" % ("Components", "PEC(in k$)", "zRate(USD/hr)",\
                                                     "XF(kW)","XP(kW)", "XD(kW)","eta2" ,"CXD(USD/hr)", "f(%)"))
    for i in range(0, len(comList)):
        print("%s \t%14.3f %12.3f %10.3f %11.3f %11.3f %11.3f %11.3f %11.3f" \
              % (comList[i].name, comList[i].PEC / 1e3, comList[i].zRate,\
                 comList[i].XF,comList[i].XP,comList[i].XD, comList[i].etaII, comList[i].CXD, comList[i].f))

    print("%s \t%14.3f %12.3f %10.3f %11.3f %12.3f %10.3f %10.3f %11.3f " % ("System", total[0] / 1e3, total[1], total[2], total[3], total[4],total[5],total[6],total[7]))

    print("Payback Period is: %.3f" % (total[8]))
    #sys.stdout.close()


#plt.style.use('seaborn-whitegrid')
#plt.plot(pCond, out)


