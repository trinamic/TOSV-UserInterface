'''
Created on 09.04.2020

@author: ED
'''
from PyTrinamic.helpers import TMC_helpers

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
        return TMC_helpers.toSigned32(reg_value)
    
    def actualFlow(self):
        reg_value = self.axisParameter(self.APs.ActualFlow)
        return TMC_helpers.toSigned32(reg_value)
    
    def actualVolume(self):
        reg_value = self.axisParameter(self.APs.ActualVolume)
        return TMC_helpers.toSigned32(reg_value)
    
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
        print("\tRamp enabled: " + ("disabled" if (self.axisParameter(self.APs.EnableVelocityRamp)==0) else "enabled"))

    def showPIConfiguration(self):
        print("PI configuration:")
        print("\tTorque   P: " + str(self.axisParameter(self.APs.TorqueP)) + " I: " + str(self.axisParameter(self.APs.TorqueI)))
        print("\tVelocity P: " + str(self.axisParameter(self.APs.VelocityP)) + " I: " + str(self.axisParameter(self.APs.VelocityI)))
        print("\tPressure P: " + str(self.axisParameter(self.APs.PressureP)) + " I: " + str(self.axisParameter(self.APs.PressureI)))

    def showSelectedCommutationFeedback(self):
        print("Sensor feedback selection:")
        print("\tCommutation mode: " + str(self.axisParameter(self.APs.CommutationMode)))

    def showTosvConfiguration(self):
        print("TOSV configuration:")
        print("\tStarup time:           " + str(self.axisParameter(self.APs.TosvStartupTime)))
        print("\tInhalation rise time:  " + str(self.axisParameter(self.APs.TosvInhalationRiseTime)))
        print("\tInhalation pause time: " + str(self.axisParameter(self.APs.TosvInhalationPauseTime)))
        print("\tExhalation fall time:  " + str(self.axisParameter(self.APs.TosvExhalationFallTime)))
        print("\tExhalation pause time: " + str(self.axisParameter(self.APs.TosvExhalationPauseTime)))
        print("\tLIMIT pressure: " + str(self.axisParameter(self.APs.TosvLimitPressure)))
        print("\tPEEP pressure:  " + str(self.axisParameter(self.APs.TosvPeepPressure)))
        
    def stateToName(self, i):
        switcher={
                0:'Stopped',
                1:'Startup',
                2:'Inhalation rise',
                3:'Inhalation pause',
                4:'Exhalation fall',
                5:'Exhalation pause'
        }
        return switcher.get(i,"Invalid state")
    
    def ModetoName(self, i):
        switcher={
                0:'Pressure Mode',
                1:'Volume Mode'
        }
        return switcher.get(i,"Invalid state")
    def reboot(self):
        self.connection.send(255, 0, 0, 1234)
        
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
    MotorType                   = 14
    CommutationMode             = 15
    PwmFrequency                = 16 
    TargetCurrent               = 20
    ActualCurrent               = 21
    TargetVelocity              = 24
    RampVelocity                = 25
    ActualVelocity              = 26
    MaxVelocity                 = 27
    EnableVelocityRamp          = 28
    Acceleration                = 29
    TargetPressure              = 31
    RampPressure                = 32
    ActualPressure              = 33
    MaxPressure                 = 34
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
    VolumePIErrorSum            = 45
    ActualOpenLoopAngle         = 47
    ActualDigitalHallAngle      = 48
    MaxNegativeCurrent          = 49
    HallPolarity                = 50
    HallDirection               = 51
    HallInterpolation           = 52
    HallPhiEOffset              = 53
    HallInputsRaw               = 54
    VolumeP                     = 56
    VolumeI                     = 57
    
    BrakeChopperEnable          = 95
    BrakeChopperVoltageLimit    = 96
    BrakeChopperHysteresis      = 97
    
    TosvMode                    = 99
    TosvEnable                  = 100
    TosvState                   = 101
    TosvTimer                   = 102
    TosvStartupTime             = 103
    TosvInhalationRiseTime      = 104
    TosvInhalationPauseTime     = 105
    TosvExhalationFallTime      = 106
    TosvExhalationPauseTime     = 107
    TosvLimitPressure           = 108
    TosvPeepPressure            = 109
    ActualFlow                  = 110
    ZeroFlowSensor              = 111
    TargetVolume                = 112
    ActualVolume                = 113
    MaxVolume                   = 114
    
    ASBenable                   = 120
    ASBThreshold                = 121
    
    ReInitFlowSensor            = 130
    
    DebugValue0                 = 240
    DebugValue1                 = 241
    DebugValue2                 = 242
    DebugValue3                 = 243
    DebugValue4                 = 244
    DebugValue5                 = 245
    DebugValue6                 = 246
    DebugValue7                 = 247
    DebugValue8                 = 248
    DebugValue9                 = 249
    
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

    " tosv states "    
    TOSV_STATE_STOPPED          = 0
    TOSV_STATE_STARTUP          = 1
    TOSV_STATE_INHALATION_RISE  = 2
    TOSV_STATE_INHALATION_PAUSE = 3
    TOSV_STATE_EXHALATION_FALL  = 4
    TOSV_STATE_EXHALATION_PAUSE = 5

class _GPs():
    " serial configuration "
    SerialBaudRate          = 65
    SerialModuleAddress     = 66
    SerialHostAddress       = 76
