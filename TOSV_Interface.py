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
        #port = "COM8"#"/dev/ttyS0" #Change for different Interface type
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

    def getBoardReading(self, Parameter):
        try: 
            APsParam = getattr(self.module.APs, Parameter)
            return self.module.axisParameter(APsParam)
        except: 
            self.connected = False 
            print(f"Connection Error: {Parameter} could not be read")
    def setBoardParameter(self, Parameter, value):
        try: 
            APsParam = getattr(self.module.APs, Parameter)
            return self.module.setAxisParameter(APsParam, value)
        except: 
            self.connected = False 
            print(f"Connection Error: {Parameter} could not be written")
    #starts turning the motor, replace with start command for actual baord    
      
    def startVentilation(self):
        self.setBoardParameter("TosvEnable", 1)
            
    #stops turning the motor, replace with start command for actual baord      
    def stopVentilation(self):
        self.setBoardParameter("TosvEnable", 0)
            
    # read actual pressure from board
    def getActualPressure(self):
        self.getBoardReading("ActualPressure")

    # read actual flow from board
    def getActualFlow(self):
        try:
            return self.module.actualFlow()
        except: 
            self.connected = False 
            print("Connection Error: getActualFlow")
    def getActualVolume(self):
        try:
            return self.module.actualVolume()
        except: 
            self.connected = False 
            print("Connection Error: getActualVolume")
            
    def getStatus(self):
        enabled = self.getBoardReading("TosvEnable")
        if enabled == 1:
            return True
        else:
            return False
            
    def setInhalationRiseTime(self,value):
        self.setBoardParameter("TosvInhalationRiseTime", value)
            
    def setInhalationPauseTime(self, value):
        self.setBoardParameter("TosvInhalationPauseTime", value)
            
    def setExhalationFallTime(self, value):
        self.setBoardParameter("TosvExhalationFallTime", value)
            
    def setExhalationPauseTime(self, value):
        self.setBoardParameter("TosvExhalationPauseTime", value)
        
    def setMode(self, value):
        self.setBoardParameter("TosvMode", value)
        
    def setLimitPresssure(self, value):
        self.setBoardParameter("TosvLimitPresssure", value)
            
    def setPeepPressure(self, value):
        self.setBoardParameter("TosvPeepPressure", value)
        
    def setTargetVolume(self, value):
        self.setBoardParameter("TosvTargetVolume", value)
        
    def getCurrentState(self):
        return self.getBoardReading("TosvState")
        
    def getTargetVolume(self):
        return self.getBoardReading("TosvTargetVolume")      
            
    def getInhalationRiseTime(self):
        return self.getBoardReading("TosvInhalationRiseTime")
            
    def getInhalationPauseTime(self):
        return self.getBoardReading("TosvInhalationPauseTime")
            
    def getExhalationFallTime(self):
        return self.getBoardReading("TosvExhalationFallTime")
            
    def getExhalationPauseTime(self):
        return self.getBoardReading("TosvExhalationPauseTime")
            
    def getLimitPresssure(self):
        return self.getBoardReading("TosvLimitPresssure")
            
    def getPeepPressure(self):
        return self.getBoardReading("TosvPeepPressure")
        
    def getMode(self):
        return self.getBoardReading("TosvMode")
        
    def ZeroFlowSensor(self):
        self.setBoardParameter("ZeroFlowSensor", 0)