#!/usr/bin/python
# (c) 2018 Ian Leiman, ian.leiman@gmail.com
# pydplan_buhlmann
# PYDPLAN module for Bühlmann 16 compartment tissue model, a Python Dive Planner with PyQt5 GUI
# inspiration taken from from dipplanner and decotengu
#
import math
import copy

class tcCoefficients():
    """
    Object that stores coefficients for one Buhlmann model compartment
    """
    def __init__(self, name,
                 NitrogenHT, HeliumHT,  # Nitrogen and Helium half times
                 NitrogenA, NitrogenB,  # a coefficients
                 HeliumA, HeliumB ):    # b coefficients
        self.name = name
        self.NitrogenHT = NitrogenHT
        self.HeliumHT   = HeliumHT
        self.NitrogenA  = NitrogenA
        self.NitrogenB  = NitrogenB
        self.HeliumA    = HeliumA
        self.HeliumB    = HeliumB

        self.NitrogenK  = math.log(2) / NitrogenHT
        self.HeliumK    = math.log(2) / HeliumHT


BUHLMANN_COEF = {
        "ZHL16c": [
            tcCoefficients(name='1',
                            NitrogenHT=5.00, HeliumHT=1.88,
                            NitrogenA=1.1696, NitrogenB=0.5578,
                            HeliumA=1.6189, HeliumB=0.4770),
            tcCoefficients(name='2',
                            NitrogenHT=8.00, HeliumHT=3.02,
                            NitrogenA=1.0000, NitrogenB=0.6514,
                            HeliumA=1.3830, HeliumB=0.5747),
            tcCoefficients(name='3',
                            NitrogenHT=12.50, HeliumHT=4.72,
                            NitrogenA=0.8618, NitrogenB=0.7222,
                            HeliumA=1.1919, HeliumB=0.6527),
            tcCoefficients(name='4',
                            NitrogenHT=18.50, HeliumHT=6.99,
                            NitrogenA=0.7562, NitrogenB=0.7825,
                            HeliumA=1.0458, HeliumB=0.7223),
            tcCoefficients(name='5',
                            NitrogenHT=27.00, HeliumHT=10.21,
                            NitrogenA=0.6200, NitrogenB=0.8126,
                            HeliumA=0.9220, HeliumB=0.7582),
            tcCoefficients(name='6',
                            NitrogenHT=38.30, HeliumHT=14.48,
                            NitrogenA=0.5043, NitrogenB=0.8434,
                            HeliumA=0.8205, HeliumB=0.7957),
            tcCoefficients(name='7',
                            NitrogenHT=54.30, HeliumHT=20.53,
                            NitrogenA=0.4410, NitrogenB=0.8693,
                            HeliumA=0.7305, HeliumB=0.8279),
            tcCoefficients(name='8',
                            NitrogenHT=77.00, HeliumHT=29.11,
                            NitrogenA=0.4000, NitrogenB=0.8910,
                            HeliumA=0.6502, HeliumB=0.8553),
            tcCoefficients(name='9',
                            NitrogenHT=109.00, HeliumHT=41.20,
                            NitrogenA=0.3750, NitrogenB=0.9092,
                            HeliumA=0.5950, HeliumB=0.8757),
            tcCoefficients(name='10',
                            NitrogenHT=146.00, HeliumHT=55.19,
                            NitrogenA=0.3500, NitrogenB=0.9222,
                            HeliumA=0.5545, HeliumB=0.8903),
            tcCoefficients(name='11',
                            NitrogenHT=187.00, HeliumHT=70.69,
                            NitrogenA=0.3295, NitrogenB=0.9319,
                            HeliumA=0.5333, HeliumB=0.8997),
            tcCoefficients(name='12',
                            NitrogenHT=239.00, HeliumHT=90.34,
                            NitrogenA=0.3065, NitrogenB=0.9403,
                            HeliumA=0.5189, HeliumB=0.9073),
            tcCoefficients(name='13',
                            NitrogenHT=305.00, HeliumHT=115.29,
                            NitrogenA=0.2835, NitrogenB=0.9477,
                            HeliumA=0.5181, HeliumB=0.9122),
            tcCoefficients(name='14',
                            NitrogenHT=390.00, HeliumHT=147.42,
                            NitrogenA=0.2610, NitrogenB=0.9544,
                            HeliumA=0.5176, HeliumB=0.9171),
            tcCoefficients(name='15',
                            NitrogenHT=498.00, HeliumHT=188.24,
                            NitrogenA=0.2480, NitrogenB=0.9602,
                            HeliumA=0.5172, HeliumB=0.9217),
            tcCoefficients(name='16',
                            NitrogenHT=635.00, HeliumHT=240.03,
                            NitrogenA=0.2327, NitrogenB=0.9653,
                            HeliumA=0.5119, HeliumB=0.9267),
        ],
    }


class Constants ():
    '''
    constants used in calculations
    '''
    surfacePressure = 1.01325  #: surface pressure (in bar)
    surfaceTemperature = 20
    AirHelium = 0.0  #: fraction of HE in standard AIR
    AirNitrogen = 0.7808  #: fraction of N2 in standard AIR
    AirOxygen = 0.2095  #: fraction of O2 in standard AIR
    AirArgon = 0.00934  #: fraction of AR (argon) in standard AIR
    # fraction of inert gas in standard AIR
    AirInertGasFraction = AirHelium + AirNitrogen + AirArgon
    # WaterVaporSurface = 0.0567 # dipplanner
    WaterVaporSurface = 0.0627   # decotengu, used in OSTC
    initN2 = 0.745

class Buhlmann():
    """
    object that stores all the coefficients for all variants of the Buhlmann decompression models
    "ZHL16a", "ZHL16b", "ZHL16c"
    the coefficients are generated by a separate Python script from text copied from source literature
    """
    model = dict()

    def __init__(self):
        self.model = BUHLMANN_COEF


class ModelPoint():
    """
    object that stores a Buhlmann model state for 16 tissue compartments
    """
    COMPS = len(BUHLMANN_COEF['ZHL16c'])

    def __init__(self, modelUsed = 'ZHL16c'):
        self.modelUsed = modelUsed

        self.tissues = []
        self.ambient = 0.0 # store the ambient pressure used to calculate this point
        self.leadMaxAmbBars = -100.0
        self.ceilings = []
        self.gfNow = 1.0
        self.leadTissue = -1
        self.leadCeilingMeters = -100.0
        self.leadCeilingStop = -1

        self.leadCeilingBarsNitrogen = 0.0
        self.leadCeilingBarsHelium = 0.0
        self.maxNitrogenPressure = 0.0
        self.maxHeliumPressure = 0.0

        # self.ox_tox = OxTox()

        # store water wapor partial pressure
        self.waterVapor =  Constants.WaterVaporSurface
        # create tissue compartments
        for index in range(self.COMPS):
            self.tissues.append(Compartment(index))
            self.ceilings.append(0.0)

    def __deepcopy__(self, memo):
        newobj = ModelPoint()
        newobj.modelUsed = self.modelUsed
        newobj.ambient = self.ambient
        newobj.leadMaxAmbBars = self.leadMaxAmbBars
        newobj.ceilings = copy.deepcopy( self.ceilings)
        newobj.gfNow = self.gfNow
        newobj.leadTissue = self.leadTissue
        newobj.leadCeilingMeters = self.leadCeilingMeters
        newobj.leadCeilingStop = self.leadCeilingStop

        newobj.leadCeilingBarsNitrogen = self.leadCeilingBarsNitrogen
        newobj.leadCeilingBarsHelium   = self.leadCeilingBarsHelium
        newobj.maxNitrogenPressure = self.maxNitrogenPressure
        newobj.maxHeliumPressure = self.maxHeliumPressure

        # newobj.ox_tox = copy.deepcopy(self.ox_tox)

        for i in range(0, len(self.tissues)):
            newobj.tissues[i] = copy.deepcopy(self.tissues[i])
        return newobj

    def initSurface(self, mc):
        for comp in self.tissues:
            comp.setNewPressures(mc[comp.index], heliumPressure=0.0, nitrogenPressure = Constants.initN2)


    def control_compartment(self, gradient):
        control_compartment_number = 0
        max_pressure = 0.0

        for comp_number in range(0, self.COMPS):
            pressure = self.tissues[comp_number].get_max_amb(gradient) - Constants.surfacePressure

            if pressure > max_pressure:
                control_compartment_number = comp_number
                max_pressure = pressure
        return control_compartment_number + 1

    def ceiling(self, gradient):

        pressure = 0.0
        for comp in self.tissues:
            # Get compartment tolerated ambient pressure and convert from
            # absolute pressure to depth
            comp_pressure = comp.get_max_amb(gradient) - Constants.surfacePressure
            if comp_pressure > pressure:
                pressure = comp_pressure
        return pressure2depth(pressure)

    def ceiling_in_pabs(self, gradient):

        pressure = 0.0
        for comp in self.tissues:
            # Get compartment tolerated ambient pressure and convert from
            # absolute pressure to depth
            comp_pressure = comp.get_max_amb(gradient)
            if comp_pressure > pressure:
                pressure = comp_pressure
        return pressure

    def m_value(self, pressure):

        p_absolute = pressure + Constants.surfacePressure
        compartment_mv = 0.0
        max_mv = 0.0

        for comp in self.tissues:
            compartment_mv = comp.get_mv(p_absolute)
            if compartment_mv > max_mv:
                max_mv = compartment_mv

        return max_mv

    #################################################################################
    ############# do it all calculation function, both constant depth, ascend/descend
    def calculateAllTissues(self, modelUsed, beginPressure, endPressure,
                            intervalMinutes,  # in minutes
                            heliumFraction, nitrogenFraction, gfNow):
        ''' Calculate all tissue compartments for the given model constants
        :param modelUsed: the model coefficients list to be used in calculation
        :type modelUsed: Buhlmann.model
        :param beginPressure: bar of pressure at begin of the segment calculated
        :type beginPressure: float
        :param endPressure: bar of pressure at end of the segment calculated
        :type endPressure: float
        :param intervalMinutes: minutes of exposure of the segment
        :type intervalMinutes: float
        :param heliumFraction: fraction of Helium, 1.0 = 100%, 0.0 = no helium
        :type heliumFraction: float
        :param nitrogenFraction: fraction of Nitrogen
        :type nitrogenFraction: float
        :param gfNow: gradient factor for ceiling calculation
        :type gfNow: float
        :return: nothing
        :rtype: None
        '''

        beginAmbientPressure = beginPressure #+ Constants.surfacePressure
        endAmbientPressure   = endPressure   #+ Constants.surfacePressure
        heliumInspired = (beginAmbientPressure - self.waterVapor) * heliumFraction
        nitrogenInspired = (beginAmbientPressure - self.waterVapor) * nitrogenFraction

        if beginPressure == endPressure :
            # constant depth case, gas rate not changing
            heliumBarPerMin = 0.0
            nitrogenBarPerMin = 0.0

        else:
            # ascending or descending, calculate BAR/min change rate for inert gases
            barPerMin = (endPressure - beginPressure) / intervalMinutes
            heliumBarPerMin   = barPerMin * heliumFraction
            nitrogenBarPerMin = barPerMin * nitrogenFraction

        # common part for constant depth & ascending or descending
        self.ambient = endAmbientPressure
        # now iterate all compartments
        maxCeiling_now = -100.0
        maxHeliumP_now = 0.0
        maxNitrogenP_now = 0.0
        self.gfNow = gfNow
        for compartment in self.tissues:
            coefficients: tcCoefficients = modelUsed[compartment.index]
            compartment.calculateCompartment(coefficients, heliumInspired, nitrogenInspired,
                                      heliumBarPerMin, nitrogenBarPerMin, intervalMinutes)
            compartment.ambTolP = compartment.ambientToleratedPressure(endAmbientPressure)

            # the actual ceiling to use, based on gfNow
            maxAmbBars = compartment.get_max_amb(gfNow) - Constants.surfacePressure
            tcCeiling_now = pressure2depth(maxAmbBars)
            self.ceilings[compartment.index] = tcCeiling_now
            # find out the leading tissue and record it
            if tcCeiling_now > maxCeiling_now:
                maxCeiling_now = tcCeiling_now
                self.leadTissue = compartment.index
                self.leadMaxAmbBars = maxAmbBars
                self.leadCeilingMeters = maxCeiling_now
                self.leadCeilingStop = int(math.ceil(maxCeiling_now / 3.0) * 3.0)
                #self.leadCeilingBarsNitrogen = compartment.get_max_amb_n2(gfNow) - Constants.surfacePressure
                #self.leadCeilingBarsHelium =   compartment.get_max_amb_he(gfNow) - Constants.surfacePressure
            # search for maximum pressures
            if compartment.nitrogenPressure > maxNitrogenP_now:
                maxNitrogenP_now = compartment.nitrogenPressure
                self.maxNitrogenPressure = maxNitrogenP_now
            if compartment.heliumPressure > maxHeliumP_now:
                maxHeliumP_now = compartment.heliumPressure
                self.maxHeliumPressure = maxHeliumP_now


    def calculateAllTissuesDepth(self, modelUsed, beginDepth, endDepth,
                            intervalMinutes,  # in minutes
                            heliumFraction, nitrogenFraction, gfNow):
        """
        same as calculateAllTissues() but depths as arguments, instead of pressures
        we calculate the pressures here
        :param modelUsed:
        :type modelUsed:
        :param beginDepth:
        :type beginDepth:
        :param endDepth:
        :type endDepth:
        :param intervalMinutes:
        :type intervalMinutes:
        :param heliumFraction:
        :type heliumFraction:
        :param nitrogenFraction:
        :type nitrogenFraction:
        :param gfNow:
        :type gfNow:
        :return:
        :rtype:
        """
        beginPressure = depth2absolutePressure(beginDepth)
        endPressure = depth2absolutePressure(endDepth)
        self.calculateAllTissues(modelUsed, beginPressure, endPressure,
                                intervalMinutes,  # in minutes
                                heliumFraction, nitrogenFraction, gfNow)

###################################################################################################
## tissue compartment
class Compartment():
    '''
    tissue compartment object
    '''
    def __init__(self, index):
        self.index = index

        self.heliumPressure = 0.0
        self.nitrogenPressure = 0.0

        self.HeliumNitrogenA = 0.0
        self.HeliumNitrogenB = 0.0

        self.mv = 0.0
        self.ambTolP = 0.0

        self.const_exp_const_depth_he = None
        self.const_exp_const_depth_n2 = None
        self.old_k_he = None
        self.old_seg_time = None

    def __deepcopy__(self, memo):
        newobj = Compartment(self.index)

        newobj.heliumPressure = self.heliumPressure
        newobj.nitrogenPressure = self.nitrogenPressure

        newobj.HeliumNitrogenA = self.HeliumNitrogenA
        newobj.HeliumNitrogenB = self.HeliumNitrogenB
        newobj.mv = self.mv
        newobj.ambTolP = self.ambTolP
        newobj.const_exp_const_depth_he = self.const_exp_const_depth_he
        newobj.const_exp_const_depth_n2 = self.const_exp_const_depth_n2
        newobj.old_k_he = self.old_k_he
        newobj.old_seg_time = self.old_seg_time
        return newobj

    ####
    def setNewPressures(self, coefficient, heliumPressure, nitrogenPressure):
        '''set new pressures to a tissue compartment, and update the HeliumNitrogen A&B coefficients

        :param coefficient: coefficients of Buhlmann model to be used
        :type coefficient:tcCoefficients
        :param heliumPressure: new Helium partial pressure for the compartment
        :type heliumPressure:float
        :param nitrogenPressure: new Nitrogen partial pressure for the compartment
        :type nitrogenPressure:float
        :return: nothing returned, sets the Compartment self variables
        :rtype: None
        '''
        self.heliumPressure = heliumPressure
        self.nitrogenPressure = nitrogenPressure

        self.HeliumNitrogenA = (((coefficient.HeliumA * heliumPressure) + (coefficient.NitrogenA * nitrogenPressure)) /
                                (heliumPressure + nitrogenPressure))
        self.HeliumNitrogenB = (((coefficient.HeliumB * heliumPressure) + (coefficient.NitrogenB * nitrogenPressure)) /
                                (heliumPressure + nitrogenPressure))
        self.mv = self.get_mv(Constants.surfacePressure)

    ####
    def calculateCompartment(self, coefficient, heliumInspired, nitrogenInspired,
                             heliumRate, nitrogenRate, minutes):
        '''calculate for one tissue compartment the new partial pressures for Nitrogen and Helium
            then store the new values into the compartment
        :param coefficient: coefficients of Buhlmann model to be used
        :type coefficient:tcCoefficients
        :param heliumInspired: 
        :type heliumInspired:float
        :param nitrogenInspired:
        :type nitrogenInspired:float
        :param heliumRate:
        :type heliumRate:float
        :param nitrogenRate:
        :type nitrogenRate:float
        :param minutes:
        :type minutes:float
        :return: does not return anything, calls setNewPressures()
        :rtype: None
        '''
        # first check if we are staying at constant depth or ascending/descending
        if heliumRate != 0 and nitrogenRate != 0 :
            # ascending or descending -> we use Schreiner equation
            # heliumRate, nitrogenRate units are BAR/min
            heliumNewPressure = \
                self.newPressureSchreiner(oldPressure= self.heliumPressure,
                                          constK= coefficient.HeliumK,
                                          gasInspired= heliumInspired,
                                          gasRate= heliumRate,
                                          minutes= minutes)
            nitrogenNewPressure = \
                self.newPressureSchreiner(oldPressure= self.nitrogenPressure,
                                          constK= coefficient.NitrogenK,
                                          gasInspired= nitrogenInspired,
                                          gasRate= nitrogenRate,
                                          minutes= minutes)
        else:
            # at constant depth -> we use simplified Haldane or the instantaneous equation
            # we can also reuse the previously calculated component, no need to calculate it again
            if self.old_seg_time is None or self.old_seg_time != minutes:
                self.old_seg_time = minutes
                self.const_exp_const_depth_he = (1 - math.exp(-coefficient.HeliumK   * minutes))
                self.const_exp_const_depth_n2 = (1 - math.exp(-coefficient.NitrogenK * minutes ))
            heliumNewPressure = \
                self.heliumPressure + ((heliumInspired - self.heliumPressure) * self.const_exp_const_depth_he)
            nitrogenNewPressure = \
                self.nitrogenPressure + ((nitrogenInspired - self.nitrogenPressure) * self.const_exp_const_depth_n2)

        self.setNewPressures(coefficient,
                             heliumPressure= heliumNewPressure,
                             nitrogenPressure= nitrogenNewPressure)


    def newPressureSchreiner(self, oldPressure, constK, gasInspired, gasRate, minutes):
        '''Schreiner equation, used when depth is changing

        :param oldPressure: the previous partial pressure for the given gas
        :type oldPressure: float
        :param constK: the K constant for this gas type
        :type constK: float
        :param gasInspired:
        :type gasInspired: float
        :param gasRate:
        :type gasRate: float
        :param minutes:
        :type minutes: float
        :return: the new tissue partial pressure for the given gas
        :rtype: float
        '''
        pressure = (gasInspired +
                    gasRate * (minutes - (1.0 / constK)) -
                    (gasInspired - oldPressure -
                    (gasRate / constK)) *
                    math.exp(-constK * minutes))
        return pressure

    def ambientToleratedPressure(self, pressure):
        m_value = float(pressure) / self.HeliumNitrogenB + self.HeliumNitrogenA
        return m_value

    def get_max_amb(self, gf):
        maxAmb = (((self.heliumPressure + self.nitrogenPressure) - self.HeliumNitrogenA * gf) /
                (gf / self.HeliumNitrogenB - gf + 1.0))
        return maxAmb

    def get_mv(self, p_amb):
        mv = ((self.heliumPressure + self.nitrogenPressure) /
                       (float(p_amb) / self.HeliumNitrogenB + self.HeliumNitrogenA))
        return mv

def depth2pressure(depth):
    pressure =  float(depth) / 10.0
    return pressure

def pressure2depth(pressure):
    depth = float(pressure) * 10.0
    return depth

def depth2absolutePressure(depth):
    pressure = Constants.surfacePressure + float(depth) / 10.0
    return pressure