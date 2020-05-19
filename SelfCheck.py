'''
Created on 11.05.2020

@author: jh

This file is part of TOSV project and implements some basic examples for some self checks.
This should just be an inspiration or starting point for further development. 
Currently it is checked that:
- the pressure sensor readings correlate to the velocity of the turbine. 
- the set and the reached VT are close enough
- the flow sensors static offset is not too high. (during standby)
'''

import time
import numpy as np

'''
Limits for Triggering Errors
'''
checkafterXPeriod = 2
checkLastXPeriods = 2
allowedVTError = 5#% from setVT
allowedRPMPressureLag = 10
allowedRPMPressureCorr = 0.9
allowedVTError = 10#% from setV
allowedStaticFlowMean = 20 #ml/min

class SelfCheck:
    def __init__(self, Alarm):
        self.Alarm =  Alarm
        self.Data = list() #Data = [0= volumeData, 1=volumeTimeData, 2=flowData, 3=flowTimeData, 4=pressureData, 5=pressureTimeData, 6=stateData, 7=stateTimeData, 8=RPMData, 9=RPMTimeData, 10=actualVT]
        self.Settings = list()  #Settings = [0 = Running, 1=RunningSince,2= InspRiseTime,3= InspHoldTime, 4=ExpFallTime, 5=ExpHoldTime, 6=PressureLimit, 7=PressurePeep, 8=CurrentMode, 9=ASBenable, 10=ASBThreshold, 11=MaxPressure, 12=TargetVT]
    '''Calling checks depending on state'''
    def runChecks(self, Data, Settings):
        self.Data = Data
        self.Settings = Settings
        if self.Data and self.Settings:
            if time.time()-self.Settings[1] > self.T()*checkafterXPeriod: 
                if self.Settings[0] == True:
                    self.CheckPressureSensor()
                    self.CheckVT()
                self.CheckFlowSensorStatic()

        return
    '''Cross-correlation function'''
    def XCorr(self, data1, data2):
        data1 = data1/np.linalg.norm(data1)
        data2 = data2/np.linalg.norm(data2)
        c = np.correlate(data1,data2,mode='full')
        maxshift = int((len(c)+1)/2-1)
        lag = range(-maxshift,maxshift) 
        return [c,lag]
    '''Used to find the data points to a certain time interval from referred to current moment'''
    def FindPointInLastTime(self, timedata, tlast):
        ftime = time.time()
        for x in range(len(timedata)):
            if ftime-timedata[x] < tlast:
                return x
        return 0
    '''Get period time '''
    def T(self):
        T = 0
        for x in range(2,5):
            T = T + self.Settings[x]/1000
        return T
    '''Check pressure sensor data  for plausibility'''
    def CheckPressureSensor(self):
        PressureData = self.Data[4]
        PressureTimeData = self.Data[5]
        RPMData = self.Data[8]
        RPMTimeData = self.Data[9]
        if self.CheckForData(PressureData):
            XLast = self.FindPointInLastTime(PressureTimeData, self.T()*checkLastXPeriods)
            [c, lag] = self.XCorr(PressureData[XLast:len(PressureData)], RPMData[XLast:len(PressureData)])
            maxcorr = np.amax(c)
            k = lag[np.argmax(c)]
            if maxcorr < allowedRPMPressureCorr:
                self.Alarm.newAlarm('Pressure Sensor','Unplausible pressure data')
                return
            elif abs(k) > allowedRPMPressureLag:
                self.Alarm.newAlarm('Pressure Sensor', 'Unplausible pressure data')
        else: 
            self.Alarm.newAlarm('Pressure Sensor','No valid pressure data')
            return
    '''Check flow sensor static '''
    def CheckFlowSensorStatic(self):
        if self.Settings[0] == False:
            Data = self.Data[2]
            if abs(np.average(Data[len(self.Data[2])-15:len(self.Data[2])])) > allowedStaticFlowMean:
                self.Alarm.newAlarm('Flow Sensor', 'Recalibrate and check sensor')
        return 
    '''Check VT '''
    def CheckVT(self):
        if self.Settings[8] == 1:
            if abs(self.Settings[12]-self.Data[10]) > self.Settings[12]*allowedVTError*1/100:
                self.Alarm.newAlarm('Medical Issue', 'Set VT is not reached.')
    
    '''Check if list has data other than zero'''
    def CheckForData(self, Data):
        for x in range(len(Data)):
            if Data[x] != 0: 
                return True 
        return False 
    
    
    