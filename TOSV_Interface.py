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
        interface = "serial_tmcl"
        datarate = "115200"
        arg= "--interface "+ interface +" --port "+ port + " --data-rate " + datarate
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
    def getConnection(self):
        return self.connected
    #set up Motor parameters, now in test setup with TMCC_160
    def setUpMotor(self):
        self.module = TMC4671_TMC6100_TOSV_REF(self.myInterface)
        self.module.showMotorConfiguration()

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
            self.module.setAxisParameter(self.module.APs.TOSVEnable, 1)
        except: 
            self.connected = False 
            print("Connection Error")
    #stops turning the motor, replace with start command for actual baord      
    def stopVentilation(self):
        try:
            self.module.setAxisParameter(self.module.APs.TOSVEnable, 0)
        except: 
            self.connected = False 
            print("Connection Error")
    #getValues from Board, replace with actual board values
    def getActualPressure(self):
        try:
            return self.module.axisParameter(self.module.APs.ActualPressure)
        except: 
            self.connected = False 
            print("Connection Error")
    def getStatus(self):
        try:
            if self.module.axisParameter(self.module.APs.TOSVEnable) == 1:
                return True
            else:
                return False
        except: 
            self.connected = False 
            print("Connection Error")
            
    def setInhalationRiseTime(self,value):
        try:
            self.module.setAxisParameter(self.module.APs.TOSVInhalationRiseTime, value)
        except: 
            self.connected = False 
            print("Connection Error")
    def setInhalationPouseTime(self, value):
        try:
            self.module.setAxisParameter(self.module.APs.TOSVInhalationPouseTime, value)
        except: 
            self.connected = False 
            print("Connection Error")
    def setExhalationFallTime(self, value):
        try:
            self.module.setAxisParameter(self.module.APs.TOSVExhalationFallTime, value)
        except: 
            self.connected = False 
            print("Connection Error")
    def setExhalationPauseTime(self, value):
        try:
            self.module.setAxisParameter(self.module.APs.TOSVExhalationPauseTime, value)
        except: 
            self.connected = False 
            print("Connection Error")
    def setLIMITPresssure(self, value):
        try:
            self.module.setAxisParameter(self.module.APs.TOSVLIMITPresssure, value)
        except: 
            self.connected = False 
            print("Connection Error")
    def setPEEPPressure(self, value):
        try:
            self.module.setAxisParameter(self.module.APs.TOSVPEEPPressure, value)
        except: 
            self.connected = False 
            print("Connection Error")
    def getInhalationRiseTime(self):
        try:
            return self.module.axisParameter(self.module.APs.TOSVInhalationRiseTime)
        except: 
            self.connected = False 
            print("Connection Error")
    def getInhalationPouseTime(self):
        try:
            return self.module.axisParameter(self.module.APs.TOSVInhalationPouseTime)
        except: 
            self.connected = False 
            print("Connection Error")
    def getExhalationFallTime(self):
        try:
            return self.module.axisParameter(self.module.APs.TOSVExhalationFallTime)
        except: 
            self.connected = False 
            print("Connection Error")
    def getExhalationPauseTime(self):
        try:
            return self.module.axisParameter(self.module.APs.TOSVExhalationPauseTime)
        except: 
            self.connected = False 
            print("Connection Error")
    def getLIMITPresssure(self):
        try:
            return self.module.axisParameter(self.module.APs.TOSVLIMITPresssure)
        except: 
            self.connected = False 
            print("Connection Error")
    def getPEEPPressure(self):
        try:
            return self.module.axisParameter(self.module.APs.TOSVPEEPPressure)
        except: 
            self.connected = False 
            print("Connection Error")