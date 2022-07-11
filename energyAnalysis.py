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
import json, CoolProp.CoolProp as CP
from CoolProp.CoolProp import PropsSI

np.set_printoptions(formatter={'float': '{: .5f}'.format})
CP.set_config_string(CP.ALTERNATIVE_REFPROP_PATH, 'C:\\Program Files (x86)\\REFPROP\\')
CP.get_global_param_string("REFPROP_version")

def energyAnalysis (m, lhv, bch, pressure ):
    n = 16

    P = np.zeros((n))
    T = np.zeros((n))
    Q = np.zeros((n))
    h = np.zeros((n))
    s = np.zeros((n))
    x = np.zeros((n))
    X = np.zeros((n))

    (P[6], P[7], P[10]) = pressure
    # P6, P14 --> Boiling Pressure and HPST inlet pressure
    # P7, P12, P13 --> LPST inlet pressure
    # P10, P11 --> Condensing Pressure


    T[0] = 298
    P[0] = 101000
    h[0] = 104920
    s[0] = 367.22

    # Pump 1
    P[11] = P[10] #7e3 # This pressure can be varied for our case
    Q[11] = 0

    h[11] = (PropsSI('H', 'P', P[11], 'Q', Q[11], "REFPROP::water"))
    s[11] = (PropsSI('S', 'P', P[11], 'Q', Q[11], "REFPROP::water"))
    T[11] = (PropsSI('T', 'P', P[11], 'Q', Q[11], "REFPROP::water"))
    x[11] = ((h[11] - h[0]) - T[0] * (s[11] - s[0]))

    P[12] =  P[7] #160e3 -->pLPST
    s12isen = s[11]
    h12isen = PropsSI('H', 'P', P[12], 'S', s12isen, "REFPROP::water")
    h[12] = h[11] + ((h12isen - h[11]) / 0.88)
    s[12] = (PropsSI('S', 'P', P[12], 'H', h[12], "REFPROP::water"))
    T[12] = (PropsSI('T', 'P', P[12], 'H', h[12], "REFPROP::water"))
    x[12] = ((h[12] - h[0]) - T[0] * (s[12] - s[0]))

    # Pump 2
    P[13] = P[12]
    Q[13] = 0
    h[13] = (PropsSI('H', 'P', P[13], 'Q', Q[13], "REFPROP::water"))
    s[13] = (PropsSI('S', 'P', P[13], 'Q', Q[13], "REFPROP::water"))
    T[13] = (PropsSI('T', 'P', P[13], 'Q', Q[13], "REFPROP::water"))
    x[13] = ((h[13] - h[0]) - T[0] * (s[13] - s[0]))

    P[14] = P[6] #4162e3  --> pHPST/ Boiling Pressure
    s14isen = s[13]
    h14isen = PropsSI('H', 'P', P[14], 'S', s14isen, "REFPROP::water")
    h[14] = h[13] + ((h14isen - h[13]) / 0.88)
    s[14] = PropsSI('S', 'H', h[14], 'P', P[14], "REFPROP::water")
    T[14] = PropsSI('T', 'H', h[14], 'P', P[14], "REFPROP::water")
    x[14] = ((h[14] - h[0]) - T[0] * (s[14] - s[0]))

    T[2] = 298
    P[2] = 101000
    h[2] = lhv

    # Air Circuit
    h_airRef = 298296.77
    s_airRef = 6860.758

    P[3] = 111000
    T[3] = 298.15
    h[3] = 298425
    s[3] = 6834
    x[3] = ((h[3] - h_airRef) - T[0] * (s[3] - s_airRef))

    # Incinerator

    qFuel = m[2] * bch * 1000
    h[4] = (m[3] * h[3] + qFuel) / m[3]
    P[4] = 111e3
    s[4] = PropsSI('S', 'H', h[4], 'P', P[4], "REFPROP::exhaustTrindade.mix")
    T[4] = PropsSI('T', 'H', h[4], 'P', P[4], "REFPROP::exhaustTrindade.mix")
    x[4] = ((h[4] - h_airRef) - T[0] * (s[4] - s_airRef))

    # Ash enthalpy and exergy
    T[15] = 298
    P[15] = 101000
    h[15] = (0.0002155 * T[4] ** 2 + 0.7618 * T[4] - 254.2) * 1000
    x[15] = (0.000456 * T[4] ** 2 + 0.01057 * T[4] - 54.44) * 1000

    # Inside Steam Generator
    T[5] = 472.15 # Determine the outlet temperature for our case
    P[5] = 110878
    h[5] = PropsSI("H", "P", P[5], "T", T[5], "REFPROP::exhaustTrindade.mix")
    s[5] = PropsSI("S", "P", P[5], "T", T[5], "REFPROP::exhaustTrindade.mix")
    x[5] = ((h[5] - h_airRef) - T[0] * (s[5] - s_airRef))

    #P[6] = 4162e3 --> pHPST
    h[6] = h[14] + (m[3] * (h[4] - h[5]) / m[6])
    s[6] = PropsSI('S', 'P', P[6], 'H', h[6], "REFPROP::water")
    x[6] = ((h[6] - h[0]) - T[0] * (s[6] - s[0]))
    T[6] = PropsSI('T', 'P', P[6], 'H', h[6], "REFPROP::water")

    # Turbine 1
    #P[7] = 160e3 --> pLPST
    s7isen = s[6]
    h7isen = PropsSI('H', 'P', P[7], 'S', s7isen, "REFPROP::water")
    h[7] = h[6] - (0.85 * (h[6] - h7isen))
    s[7] = PropsSI('S', 'P', P[7], 'H', h[7], "REFPROP::water")
    T[7] = PropsSI('T', 'P', P[7], 'H', h[7], "REFPROP::water")
    x[7] = ((h[7] - h[0]) - T[0] * (s[7] - s[0]))

    h[8] = h[7]
    s[8] = s[7]
    P[8] = P[7]
    T[8] = T[7]
    x[8] = x[7]

    h[9] = h[7]
    s[9] = s[7]
    P[9] = P[7]
    T[9] = T[7]
    x[9] = x[7]

    # Turbine 2
    #P[10] = 7e3 --> pCond
    s10isen = s[7]
    h10isen = PropsSI('H', 'P', P[10], 'S', s10isen, "REFPROP::water")
    h[10] = h[7] - (0.85 * (h[7] - h10isen))
    s[10] = PropsSI('S', 'H', h[10], 'P', P[10], "REFPROP::water")
    T[10] = PropsSI('T', 'H', h[10], 'P', P[10], "REFPROP::water")
    x[10] = ((h[10] - h[0]) - T[0] * (s[10] - s[0]))

    # Condernser

    qOut = m[10] * (h[10] - h[11])

    h[1] = (qOut / m[1]) + h[0]  # Vary this mass flow of water
    s[1] = PropsSI('S', 'H', h[1], 'P', P[0], "REFPROP::water")
    T[1] = PropsSI('T', 'H', h[1], 'P', P[0], "REFPROP::water")
    x[1] = ((h[1] - h[0]) - T[0] * (s[1] - s[0]))
    P[1] = P[0]

    # Energy Analysis [in KW]
    h = h / 1000
    s = s / 1000
    qFuel = qFuel / 1000
    qOut = qOut / 1000
    wST1 = m[6] * (h[6] - h[7])
    wST2 = m[9] * (h[7] - h[10])
    wPump1 = m[11] * (h[12] - h[11])
    wPump2 = m[13] * (h[14] - h[13])
    wOut = wST1 + wST2 - wPump1 - wPump2
    wOutGWh = wOut * 8000 / (1e6)  # in GWh per Year
    eta1 = (wOut / (m[2] * lhv)) * 100

    eta2 = wOut* 100/qFuel

    mis = [bch, qFuel, qOut, wST1, wST2, wPump1, wPump2, wOut, eta1, eta2]

    # Exergy Analysis
    x[2] = bch * 1000
    X = m * x


    X= X/ 1000

    return (P, T, h, s, X, mis)

'''
def fuelExergy (chemComp):
    (H, O, N) = chemComp
    beta = (1.044 + (0.016 * H) - ((0.3493 * O) * (1 + (0.0531 * H))) + (0.0493 * N)) / (1 - (0.4124 * O))
    bch = (9230e3 * beta) + (9683e3 * 0.0011) + (49.87e3 * 0.4130)
    return bch
'''

