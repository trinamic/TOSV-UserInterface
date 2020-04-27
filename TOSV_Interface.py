# This Python file uses the following encoding: utf-8
'''
Created on 14.04.2020

@author: jh
'''
from PyTrinamic.connections.ConnectionManager import ConnectionManager
import threading
from modules.TMC4671_TMC6100_TOSV_REF import TMC4671_TMC6100_TOSV_REF


#Interface class... Handles connection with the board via PyTrinamic
#ToDo: detect when connection drops. 
class TOSV_Interface:
    def __init__(self):
        port = "COM20"#"/dev/ttyS0" #Change for different Interface type
        #port = "/dev/ttyS0" #Change for different Interface type
        interface = "serial_tmcl"
        datarate = "115200"
        arg= f"--interface {interface} --port {port} --data-rate {datarate}" 
        print(arg)
        self.connectionManager = ConnectionManager(arg.split())
        self.connected = True 

    #Try to establish connection
    def connect(self):
        try:    
            try:
                self.myInterface.close()
            finally:
                self.myInterface = self.connectionManager.connect()
                try:
                    self.setUpThread = threading.Thread(target=self.setUpMotor) #Using Thread to deal with connection errors
                    self.setUpThread.start()
                    self.module = self.setUpThread.result()
                    print("Connected")
                except:
                    print("could not connect, module")
        except:
            print("could not connect, interface")
    
    #returns if board is connected
    def isConnected(self):
        return self.connected

    #set up Motor parameters, now in test setup with TMCC_160
    def setUpMotor(self):
        self.module = TMC4671_TMC6100_TOSV_REF(self.myInterface)
        self.module.showMotorConfiguration()
        self.module.showPIConfiguration()
        self.module.showSelectedCommutationFeedback()
        self.module.showTosvConfiguration()
        self.module.setAxisParameter(self.module.APs.PressureP, 3000)
        self.module.setAxisParameter(self.module.APs.PressureI, 2500)

        " motor/module settings "
        print("Motor set up done")
        self.connected = True
        return self.module
    
    #disconnect 
    def disconnect(self):
        try:
            self.myInterface.close()
            self.connected = False
            return False
        except: 
            print("closing connection failed... was a connection open?")

    #starts turning the motor, replace with start command for actual baord      
    def startVentilation(self):
        try:
            self.module.setAxisParameter(self.module.APs.TosvEnable, 1)
        except: 
            self.connected = False 
            print("Connection Error: startVentilation")
            
    #stops turning the motor, replace with start command for actual baord      
    def stopVentilation(self):
        try:
            self.module.setAxisParameter(self.module.APs.TosvEnable, 0)
        except: 
            self.connected = False 
            print("Connection Error: stopVentilation")
            
    # read actual pressure from board
    def getActualPressure(self):
        try:
            return self.module.axisParameter(self.module.APs.ActualPressure)
        except: 
            self.connected = False 
            print("Connection Error: getActualPressure")

    # read actual flow from board
    def getActualFlow(self):
        try:
            # todo: update with real flow value
            return self.module.actualFlow()
        except: 
            self.connected = False 
            print("Connection Error: getActualFlow")
    def getActualVolume(self):
        try:
            # todo: update with real flow value
            return self.module.actualVolume()
        except: 
            self.connected = False 
            print("Connection Error: getActualVolume")
            
    def getStatus(self):
        try:
            if self.module.axisParameter(self.module.APs.TosvEnable) == 1:
                return True
            else:
                return False
        except: 
            self.connected = False 
            print("Connection Error: getStatus")
            
    def setInhalationRiseTime(self,value):
        try:
            self.module.setAxisParameter(self.module.APs.TosvInhalationRiseTime, value)
        except: 
            self.connected = False 
            print("Connection Error: setInhalationRiseTime")
            
    def setInhalationPauseTime(self, value):
        try:
            self.module.setAxisParameter(self.module.APs.TosvInhalationPauseTime, value)
        except: 
            self.connected = False 
            print("Connection Error: setInhalationPauseTime")
            
    def setExhalationFallTime(self, value):
        try:
            self.module.setAxisParameter(self.module.APs.TosvExhalationFallTime, value)
        except: 
            self.connected = False 
            print("Connection Error: setExhalationFallTime")
            
    def setExhalationPauseTime(self, value):
        try:
            self.module.setAxisParameter(self.module.APs.TosvExhalationPauseTime, value)
        except: 
            self.connected = False 
            print("Connection Error: setExhalationPauseTime")
            
    def setLimitPresssure(self, value):
        try:
            self.module.setAxisParameter(self.module.APs.TosvLimitPresssure, value)
        except: 
            self.connected = False 
            print("Connection Error: setLIMITPresssure")
            
    def setPeepPressure(self, value):
        try:
            self.module.setAxisParameter(self.module.APs.TosvPeepPressure, value)
        except: 
            self.connected = False 
            print("Connection Error: setPeepPressure")
            
    def getInhalationRiseTime(self):
        try:
            return self.module.axisParameter(self.module.APs.TosvInhalationRiseTime)
        except: 
            self.connected = False 
            print("Connection Error: getInhalationRiseTime")
            
    def getInhalationPauseTime(self):
        try:
            return self.module.axisParameter(self.module.APs.TosvInhalationPauseTime)
        except: 
            self.connected = False 
            print("Connection Error: getInhalationPauseTime")
            
    def getExhalationFallTime(self):
        try:
            return self.module.axisParameter(self.module.APs.TosvExhalationFallTime)
        except: 
            self.connected = False 
            print("Connection Error: getExhalationFallTime")
            
    def getExhalationPauseTime(self):
        try:
            return self.module.axisParameter(self.module.APs.TosvExhalationPauseTime)
        except: 
            self.connected = False 
            print("Connection Error: getExhalationPauseTime")
            
    def getLimitPresssure(self):
        try:
            return self.module.axisParameter(self.module.APs.TosvLimitPresssure)
        except: 
            self.connected = False 
            print("Connection Error: getLimitPresssure")
            
    def getPeepPressure(self):
        try:
            return self.module.axisParameter(self.module.APs.TosvPeepPressure)
        except: 
            self.connected = False 
            print("Connection Error: getPeepPressure")
    def NullFlowSensor(self):
        try:
            return
            #return self.module.axisParameter(self.module.APs.TosvPeepPressure)
        except: 
            self.connected = False 
            print("Connection Error: getPeepPressure")