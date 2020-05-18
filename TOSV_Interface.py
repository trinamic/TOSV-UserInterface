# This Python file uses the following encoding: utf-8
'''
Created on 14.04.2020

@author: jh
This file is part of TOSV project.  
This should just be an inspiration or starting point for further development. 
Handles connection with the board via PyTrinamic
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
        interface = "serial_tmcl"
        datarate = "115200"
        arg= f"--interface {interface} --port {port} --data-rate {datarate}" 
        print(arg)
        self.connectionManager = ConnectionManager(arg.split())
        self.connected = False  

    '''Try to establish connection. Threading is used to avoid crashes on failed connections'''
    def connect(self):
        try:    
            try:
                self.myInterface.close()
            finally:
                self.myInterface = self.connectionManager.connect()
                try:
                    self.setUpThread = threading.Thread(target=self.setUpMotor)
                    self.setUpThread.start()
                    print("Connected")
                except:
                    print("could not connect, module")
        except:
            print("could not connect, interface")
    
    def isConnected(self):
        return self.connected

    '''set up Motor parameters'''
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
    
    def disconnect(self):
        try:
            self.myInterface.close()
            self.connected = False
            return False
        except: 
            print("closing connection failed... was a connection open?")

    '''get parameters from Board'''
    def getBoardParameter(self, Parameter):
        try: 
            APsParam = getattr(self.module.APs, Parameter)
            return self.module.axisParameter(APsParam)
        except: 
            self.connected = False 
            print(f"Connection Error: {Parameter} could not be read")
    '''write parameters to board'''
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
        return self.getBoardParameter("ActualPressure")

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
        enabled = self.getBoardParameter("TosvEnable")
        if enabled == 1:
            return True
        else:
            return False
        
    def ZeroFlowSensor(self):
        self.setBoardParameter("ZeroFlowSensor", 0)
        
    '''reboot module '''
    def reboot(self):
        self.module.connection.send(255, 0, 0, 1234)
        self.connected = False