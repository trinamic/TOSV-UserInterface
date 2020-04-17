'''
Created on 09.04.2020

@author: ED
'''

class TMC4671_TMC6100_TOSV_REF(object):

    def __init__(self, connection):
        self.connection = connection
        self.GPs   = _GPs
        self.APs   = _APs
        self.ENUMs = _ENUMs
        self.motor = 0

    def showChipInfo(self):
        print("TMC4671-TMC6100-TOSV-REF. Voltage supply: 12 - 36V")

    " axis parameter access "
    def axisParameter(self, apType):
        return self.connection.axisParameter(apType, self.motor)

    def setAxisParameter(self, apType, value):
        self.connection.setAxisParameter(apType, self.motor, value)

    " global parameter access "
    def globalParameter(self, gpType):
        return self.connection.globalParameter(gpType, self.motor)

    def setGlobalParameter(self, gpType, value):
        self.connection.setGlobalParameter(gpType, self.motor, value)

    " standard functions "
    def rotate(self, velocity):
        self.setAxisParameter(self.APs.TargetVelocity, velocity)

    def actualVelocity(self):
        reg_value = self.axisParameter(self.APs.ActualVelocity)
        return twos_comp(reg_value, 32)

    def showMotorConfiguration(self):
        print("Motor configuration:")
        print("\tMotor pole pairs: " + str(self.axisParameter(self.APs.MotorPolePairs)))
        print("\tMax current:      " + str(self.axisParameter(self.APs.MaxCurrent)) + " mA")

    def showHallConfiguration(self):
        print("Hall configuration:")
        print("\tHall polarity:      " + str(self.axisParameter(self.APs.HallPolarity)))
        print("\tHall direction:     " + str(self.axisParameter(self.APs.HallDirection)))
        print("\tHall interpolation: " + str(self.axisParameter(self.APs.HallInterpolation)))
        print("\tHall Phi_E offset:  " + str(self.axisParameter(self.APs.HallPhiEOffset)))

    def showMotionConfiguration(self):
        print("Motion configuration:")
        print("\tMax velocity: " + str(self.axisParameter(self.APs.MaxVelocity)))
        print("\tAcceleration: " + str(self.axisParameter(self.APs.Acceleration)))
        print("\tDeceleration: " + str(self.axisParameter(self.APs.Deceleration)))
        print("\tRamp enabled: " + ("disabled" if (self.axisParameter(self.APs.EnableVelocityRamp)==0) else "enabled"))

    def showPIConfiguration(self):
        print("PI configuration:")
        print("\tTorque   P: " + str(self.axisParameter(self.APs.TorqueP)) + " I: " + str(self.axisParameter(self.APs.TorqueI)))
        print("\tVelocity P: " + str(self.axisParameter(self.APs.VelocityP)) + " I: " + str(self.axisParameter(self.APs.VelocityI)))

    def showSelectedCommutationFeedback(self):
        print("\tCommutation mode: " + str(self.axisParameter(self.APs.CommutationMode)))

class _APs():
    " motor control parameter "
    StatusFlags                 = 0
    SupplyVoltage               = 1
    DriverTemperature           = 2
    AdcI0Raw                    = 3
    AdcI1Raw                    = 4
    CurrentPhaseU               = 5
    CurrentPhaseV               = 6
    CurrentPhaseW               = 7
    AdcI0Offset                 = 8
    AdcI1Offset                 = 9
    MotorPolePairs              = 10
    MaxCurrent                  = 11
    OpenLoopCurrent             = 12
    MotorDirection              = 13
    CommutationMode             = 15
    PwmFrequency                = 16 
    TargetCurrent               = 20
    ActualCurrent               = 21
    TargetVelocity              = 25
    RampVelocity                = 26
    ActualVelocity              = 27
    MaxVelocity                 = 28
    EnableVelocityRamp          = 29
    Acceleration                = 30
    Deceleration                = 31
    TargetPressure              = 32
    RampPressure                = 33
    ActualPressure              = 34
    TorqueP                     = 35
    TorqueI                     = 36
    VelocityP                   = 37
    VelocityI                   = 38
    PressureP                   = 39
    PressureI                   = 40
    TorquePIErrorSum            = 41
    FluxPIErrorSum              = 42
    VelocityPIErrorSum          = 43
    PressurePIErrorSum          = 44
    HallPolarity                = 50
    HallDirection               = 51
    HallInterpolation           = 52
    HallPhiEOffset              = 53

    TOSVEnable                  = 100
    TOSVState                   = 101
    TOSVTimer                   = 102
    TOSVStatupTime              = 103
    TOSVInhalationRiseTime      = 104
    TOSVInhalationPouseTime     = 105
    TOSVExhalationFallTime      = 106
    TOSVExhalationPauseTime     = 107
    TOSVLIMITPresssure          = 108
    TOSVPEEPPressure            = 109
    
    " diagnostic parameter "
    MainLoopsPerSecond          = 250
    VelocityLoopsPerSecond      = 251
    CommunicationLoopsPerSecond = 252
    
    " driver enable/disable"
    EnableDriver                = 255

class _ENUMs():
    " motor feedback modes "
    COMM_MODE_DISABLED      = 0
    COMM_MODE_OPEN_LOOP     = 1
    COMM_MODE_DIGITAL_HALL  = 2

class _GPs():
    " serial configuration "
    SerialBaudRate          = 65
    SerialModuleAddress     = 66
    SerialHostAddress       = 76


def twos_comp(val, bits):
    """computes the 2's complement of an int value

    taken from: https://stackoverflow.com/questions/1604464/twos-complement-in-python
    """
    if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)         # compute negative value
    return val                          # return positive value as is
