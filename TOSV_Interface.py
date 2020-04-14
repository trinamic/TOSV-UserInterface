# This Python file uses the following encoding: utf-8
'''
Created on 14.04.2020

@author: jh
'''
from PyTrinamic.connections.ConnectionManager import ConnectionManager
from PyTrinamic.modules.TMCC_160 import TMCC_160
import threading

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
        self.module = TMCC_160(self.myInterface)
        " motor/module settings "
        self.module.setMotorPoles(4)
        self.module.setMaxTorque(2000)
        self.module.showMotorConfiguration()
        
        " hall configuration "
        self.module.setHallInvert(0)
        self.module.showHallConfiguration()
        
        " encoder settings "
        self.module.setOpenLoopTorque(1500)
        self.module.setEncoderResolution(4096)
        self.module.setEncoderDirection(0)
        self.module.setEncoderInitMode(self.module.ENUMs.ENCODER_INIT_MODE_1)
        self.module.showEncoderConfiguration()
        
        " motion settings "
        self.module.setMaxVelocity(4000)
        self.module.setAcceleration(2000)
        self.module.setRampEnabled(1)
        self.module.setTargetReachedVelocity(1000)
        self.module.setTargetReachedDistance(5)
        self.module.showMotionConfiguration()
        
        " current PID values "
        self.module.setTorquePParameter(600)
        self.module.setTorqueIParameter(600)
        
        " velocity PID values "
        self.module.setVelocityPParameter(800)
        self.module.setVelocityIParameter(500)
        
        " position PID values "
        self.module.setPositionPParameter(300)
        self.module.showPIConfiguration()
        
        " set commutation mode to FOC based on hall sensor signals "
        self.module.setCommutationMode(self.module.ENUMs.COMM_MODE_FOC_ENCODER)
        
        " set position counter to zero"
        self.module.setActualPosition(0)
        
        " move to zero position"
        self.module.moveToPosition(0)
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
    def startTest(self):
        try:
            self.module.rotate(500)
        except: 
            self.connected = False 
            print("Connection Error")
    #stops turning the motor, replace with start command for actual baord      
    def stopTest(self):
        try:
            self.module.rotate(0)
        except: 
            self.connected = False 
            print("Connection Error")
    #getValues from Board, replace with actual board values
    def getActualVelocity(self):
        try:
            return self.module.actualVelocity()
        except: 
            self.connected = False 
            print("Connection Error")
    def getTargetVelocity(self):
        try: 
            return self.module.targetReachedVelocity()
        except: 
            self.connected = False 
            print("Connection Error")