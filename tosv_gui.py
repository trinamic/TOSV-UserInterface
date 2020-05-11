# This Python file uses the following encoding: utf-8
#Imports:
'''
Created on 14.04.2020

@author: jh
'''
#Imports
import sys
import numpy
import time
import multiprocessing
import netifaces as ni

from PyQt5 import QtWidgets, uic, QtCore, QtGui
import pyqtgraph 

from TOSV_Interface import TOSV_Interface
#from winreg import SetValue

#Set to True in for fullscreen 
fullscreen = False 

class Ui(QtWidgets.QWidget):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('TOSV-GUI.ui', self)
        self.Interface = TOSV_Interface()
        self.updatetime = 50        
                
        #Define Varibles for VolumeGraph 
        #self.maxDataPoints = 12*60*60*(1000/self.updatetime)#For aprox. 12h of data record
        self.maxDataPoints = int(10*(1000/self.updatetime))

        self.volumeData = list()
        self.volumeTimeData = list()
        
        self.flowData = list()
        self.flowTimeData = list()
        
        self.pressureData = list()
        self.pressureTimeData = list()
        
        self.stateData = list()
        self.stateTimeData = list()
        
        self.actualPressure = 0 
        self.actualVolume = 0
        self.actualFlow  = 0
        self.currentState = 0
        self.cycleFreq = 0
        
        self.cycleMaxVolume = 0
        self.actualAMV = 0
        print("maxDataPoints: " + str(self.maxDataPoints))
        
        #init values
        for x in range(self.maxDataPoints):
            initTime = time.time()- (self.maxDataPoints-(x+1))*50/1000
            self.volumeData.append(0)
            self.volumeTimeData.append(initTime)
            self.flowData.append(0)
            self.flowTimeData.append(initTime)
            self.pressureData.append(0)
            self.pressureTimeData.append(initTime)
            self.stateData.append(0)
            self.stateTimeData.append(initTime)
        
        #Buffer and Used Variables.  
        self.running = False
        self.wasconnected = False
        
        self.CurrentMode = 0
        self.InspRiseTime  = 0
        self.InspHoldTime = 0
        self.ExpFallTime = 0
        self.ExpHoldTime = 0
        self.InspExp = 1
        self.Freq = 0
        self.PressureLimit = 0
        self.MaxPressure = 0
        self.PressurePeep = 0
        self.ASBenable = 0
        self.ASBThreshold = 0
        self.TargetVT = 0

        #Define Buttons
        self.ConnectButton = self.findChild(QtWidgets.QPushButton, 'ConnectButton')
        self.Start_Stop_Button = self.findChild(QtWidgets.QPushButton, 'StartButton')
        self.StopButton = self.findChild(QtWidgets.QPushButton, 'StopButton')
        self.CancelButton = self.findChild(QtWidgets.QPushButton, 'CancelButton')
        self.DisconnectButton = self.findChild(QtWidgets.QPushButton, 'DisconnectButton')
        self.SetMedSettingsButton = self.findChild(QtWidgets.QPushButton, 'SetMedSettingsButton')
        self.CancelMedSettingsButton = self.findChild(QtWidgets.QPushButton, 'CancelMedSettingsButton')
        self.NullFlowsensorButton = self.findChild(QtWidgets.QPushButton, 'NullFlowsensorButton')
        self.ModeDropdown = self.findChild(QtWidgets.QComboBox, 'ModeDropDown')
        self.StackedModes = self.findChild(QtWidgets.QStackedWidget, 'ModeSettings')
        self.TabWidget = self.findChild(QtWidgets.QTabWidget, 'tabWidget')

        #Set up Buttons
        self.StopButton.hide()
        self.CancelButton.hide()
        self.DisconnectButton.hide()
        self.ConnectButton.hide()
    
        #Define Button clicks    
        self.Start_Stop_Button.pressed.connect(self.start_Stop_Button_pressed)
        self.Start_Stop_Button.released.connect(self.start_Stop_Button_released)
             
        self.StopButton.clicked.connect(self.stop)
        self.CancelButton.clicked.connect(self.cancel)
        
        self.SetMedSettingsButton.clicked.connect(self.writeMedSettings)
        self.CancelMedSettingsButton.clicked.connect(self.clearMedChanges)
        
        self.NullFlowsensorButton.clicked.connect(self.NullFlowSensor)
        
        self.ModeDropdown.currentIndexChanged.connect(self.changeStackedModes)
        #Buttons are disabled
        #self.ConnectButton.clicked.connect(self.Interface.connect)
        #self.DisconnectButton.clicked.connect(self.Interface.disconnect)
        
        '''Define slieders'''
        #Define sliders for pressure based control mode 
        self.SliderPressureInspExp = self.findChild(QtWidgets.QSlider, 'SliderPressureInspExp')
        self.SliderPressureFreq = self.findChild(QtWidgets.QSlider, 'SliderPressureFreq')
        self.SliderPressureRiseTime = self.findChild(QtWidgets.QSlider, 'SliderPressureRiseTime')
        self.SliderPressurePeep = self.findChild(QtWidgets.QSlider, 'SliderPressurePEEP')
        self.SliderPressurePInsp = self.findChild(QtWidgets.QSlider, 'SliderPressurePInsp')
        self.SliderPressureASBTrigger = self.findChild(QtWidgets.QSlider, 'SliderPressureASBTrigger')
        #Define sliders for volume based control mode. 
        self.SliderVolumeInspExp = self.findChild(QtWidgets.QSlider, 'SliderVolumeInspExp')
        self.SliderVolumeFreq = self.findChild(QtWidgets.QSlider, 'SliderVolumeFreq')
        self.SliderVolumeRiseTime = self.findChild(QtWidgets.QSlider, 'SliderVolumeRiseTime')
        self.SliderVolumePeep = self.findChild(QtWidgets.QSlider, 'SliderVolumePEEP')
        self.SliderVolumePMax = self.findChild(QtWidgets.QSlider, 'SliderVolumePLimit')    
        self.SliderVolumeVT = self.findChild(QtWidgets.QSlider, 'SliderVolumeVT')
        self.SliderVolumeASBTrigger = self.findChild(QtWidgets.QSlider, 'SliderVolumeASBTrigger')
        '''Define checkBoxes'''
        self.checkBoxPressureASBEnabled = self.findChild(QtWidgets.QCheckBox, 'checkBoxPressureASBEnabled')
        self.checkBoxVolumeASBEnabled = self.findChild(QtWidgets.QCheckBox, 'checkBoxVolumeASBEnabled') 
        '''Define labels'''
        #Labels in Overview
        self.LabelMode = self.findChild(QtWidgets.QLabel, 'LabelMode')
        self.LabelVolume = self.findChild(QtWidgets.QLabel, 'VTLabel')
        self.LabelAMV = self.findChild(QtWidgets.QLabel, 'AMVLabel')
        self.LabelPMax = self.findChild(QtWidgets.QLabel, 'PMaxLabel')
        self.LabelPLimit = self.findChild(QtWidgets.QLabel, 'PLimLabel')
        self.LabelPEEP = self.findChild(QtWidgets.QLabel, 'PeepLabel')
        self.Labelfreq = self.findChild(QtWidgets.QLabel, 'fLabel')
        
        #Labels in MedSettings for pressure based control
        self.LabelSetPressureInspExp = self.findChild(QtWidgets.QLabel, 'SetPressureInspExp')
        self.LabelSetPressureFreq = self.findChild(QtWidgets.QLabel, 'SetPressureFreq')
        self.LabelSetPressureRiseTime = self.findChild(QtWidgets.QLabel, 'SetPressureRiseTime')
        self.LabelSetPressurePEEP = self.findChild(QtWidgets.QLabel, 'SetPressurePeepLabel')
        self.LabelSetPressurePLimit = self.findChild(QtWidgets.QLabel, 'SetPressurePLimitLabel')
        self.LabelSetPressureASB = self.findChild(QtWidgets.QLabel, 'LabelSetPressureASB')
        #Labels in MedSettings for volume based control
        self.LabelSetVolumeInspExp = self.findChild(QtWidgets.QLabel, 'SetVolumeInspExp')
        self.LabelSetVolumeFreq = self.findChild(QtWidgets.QLabel, 'SetVolumeFreq')
        self.LabelSetVolumeRiseTime = self.findChild(QtWidgets.QLabel, 'SetVolumeRiseTime')
        self.LabelSetVolumeVT = self.findChild(QtWidgets.QLabel, 'SetVolumeVT')
        self.LabelSetVolumePEEP = self.findChild(QtWidgets.QLabel, 'SetVolumePeepLabel')
        self.LabelSetVolumePLimit = self.findChild(QtWidgets.QLabel, 'SetVolumePLimitLabel')
        self.LabelSetVolumeASB = self.findChild(QtWidgets.QLabel, 'LabelSetVolumeASB')

        self.LabelIpAddress = self.findChild(QtWidgets.QLabel, 'LabelIpAddress')
        self.LabelFrameRate = self.findChild(QtWidgets.QLabel, 'LabelFrameRate')
        self.LabelDataUpdateRate = self.findChild(QtWidgets.QLabel, 'DataUpdateRate')
        #Setting up Graphs
        #Setting up VolumeGraph
        self.pen = pyqtgraph.mkPen(color=(0, 0, 0))

        self.VolumeGraph = self.findChild(pyqtgraph.PlotWidget,'VolumeGraph')
        self.VolumeGraph.setBackground(('#0069b4'))
        self.VolumeGraph.showGrid(x=True, y=True)
        self.VolumeGraphxaxis = self.VolumeGraph.getAxis('bottom')
         
        #Setting up FlowGraph
        self.FlowGraph = self.findChild(pyqtgraph.PlotWidget, 'FlowGraph')
        self.FlowGraph.setBackground(('#0069b4'))
        self.FlowGraph.showGrid(x=True, y=True)
        self.FlowGraphxaxis = self.FlowGraph.getAxis('bottom')
        
        #Setting up PressureGraph
        self.PressureGraph = self.findChild(pyqtgraph.PlotWidget, 'PressureGraph')
        self.PressureGraph.setBackground(('#0069b4'))
        self.PressureGraph.showGrid(x=True, y=True)
        self.PressureGraphxaxis = self.PressureGraph.getAxis('bottom')
        self.PressureGraph.setMouseEnabled(x=False, y= False)
        #Define Timers
        #Timer for long button press
        self.timer_start_stop_button = QtCore.QTimer()
        self.timer_start_stop_button.setSingleShot(True)
        self.timer_start_stop_button.timeout.connect(self.confirm_stop)
        
        '''Timers'''
        #Timer for refreshing GUI
        self.timer_gui = QtCore.QTimer()
        self.timer_gui.timeout.connect(self.update_gui)
        self.timer_gui.start(self.updatetime)  # every 50 millisecon
        #Timer for getting Sensor Data
        self.timer_getdata = QtCore.QTimer()
        self.timer_getdata.timeout.connect(self.getValues)
        self.timer_getdata.start(self.updatetime)
        #Timer for trying reconnect
        self.timer_reconnect = QtCore.QTimer()
        self.timer_reconnect.timeout.connect(self.reconnect)
        self.timer_reconnect.start(1000) #Dont set to low.. otherwise the connection will fail
        
        
        #Show Window, depending on Fullscreen setting. 
        self.setWindowTitle('TOSV UserInterface')
        if fullscreen:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.showFullScreen()
            self.setCursor(QtCore.Qt.BlankCursor)
        else:
            self.show()
        
        
        
    #Updating the GUI periodically, called by timer. 
    #ToDo: Cleanup 
    def update_gui(self):
        starttime = time.time()
        if self.Interface.isConnected() == True:
            self.SetMedSettingsButton.setEnabled(True)
            self.CancelMedSettingsButton.setEnabled(True)
            #self.getValues()
            '''Update depending on current view. '''
            if self.TabWidget.currentIndex() == 0:
                self.updateGraph()
                self.writeOverviewLabels()

            if self.TabWidget.currentIndex() == 1: 
                self.checkSliderChanged()
                self.writeMedSettingsLabels()


            #Setting            
            if self.running == True:
                if self.timer_start_stop_button.isActive() == True:
                    self.Start_Stop_Button.setText(str(self.timer_start_stop_button.remainingTime()))
                else:
                    self.Start_Stop_Button.setText("STOP")
                    self.Start_Stop_Button.setStyleSheet("background-color : rgb(255, 0, 0)")

            else:
                self.Start_Stop_Button.setText("START")
                self.Start_Stop_Button.setStyleSheet("background-color : rgb(0, 255, 0)")

        else: 
            #self.LabelCurrRPM.setText("-")
            #self.LabelTarRPM.setText("-")
            self.Start_Stop_Button.setText("NO MODULE")
            self.SetMedSettingsButton.setEnabled(False)
            self.CancelMedSettingsButton.setEnabled(False)
            self.Start_Stop_Button.setStyleSheet("background-color : #f7751f ")  
        self.showIpInTecConfig()
        cycletime = time.time()-starttime
        self.LabelFrameRate.setText(str("{:.2f}".format(1/cycletime)))
        
    def getValues(self):
        if self.Interface.isConnected() == True:
            starttime = time.time()
            #Get Sensor Data
            self.actualPressure = self.Interface.getActualPressure()
            self.actualVolume = self.Interface.getActualVolume()
            self.actualFlow = self.Interface.getActualFlow()
            self.currentState = self.Interface.getBoardParameter("TosvState")
            
            if self.actualPressure:
                self.actualPressure = self.actualPressure/1000
                self.pressureData.append(self.actualPressure)
                self.pressureTimeData.append(time.time())
                
                if len(self.pressureData) > self.maxDataPoints:
                    self.pressureData.pop(0)
                    self.pressureTimeData.pop(0)
                    
            if self.actualFlow != None:
                self.flowData.append(self.actualFlow)
                self.flowTimeData.append(time.time())
                
                if len(self.flowData) > self.maxDataPoints:
                    self.flowData.pop(0)
                    self.flowTimeData.pop(0)
            
            if self.actualVolume != None:
                self.volumeData.append(self.actualVolume)
                self.volumeTimeData.append(time.time())
                
                if len(self.volumeData) > self.maxDataPoints:
                    self.volumeData.pop(0)
                    self.volumeTimeData.pop(0)
                    
            if self.currentState != None:
                self.stateData.append(self.currentState)
                self.stateTimeData.append(time.time())
                
                if len(self.stateData) > self.maxDataPoints:
                    self.stateData.pop(0)
                    self.stateTimeData.pop(0)
            
                findmax = self.findMaxInCycle(self.volumeData, self.stateData)
                if findmax:
                    self.cycleMaxVolume=findmax
                    self.actualAMV = self.cycleMaxVolume*self.Freq*60*1000
                    
            cycletime = time.time()-starttime
            if cycletime != 0:
                self.LabelDataUpdateRate.setText(str("{:.2f}".format(1/cycletime)))        

    def checkSliderChanged(self):
        #ToDo. expand for Volume
        SliderchangedStyle = """.QSlider {} 
        .QSlider::groove:vertical {border: 1px solid #262626;width: 5px;background: rgb(255, 255, 255) ;margin: 0 12px;}
        .QSlider::handle:vertical {background:#3a5b78 ; border: 1px solid rgb(0, 0, 0); height: 30px; margin: -0px -35px;}"""
        SliderunchangedStyle = """.QSlider {}
        .QSlider::groove:vertical {border: 1px solid #262626;width: 5px;background: rgb(255, 255, 255) ;margin: 0 12px;}
        .QSlider::handle:vertical {background:#afb3b6 ; border: 1px solid rgb(0, 0, 0); height: 30px; margin: -0px -35px;}"""
        CheckBoxunchangedStyle = """ QCheckBox::indicator { width: 20px; height: 20px;}"""
        CheckBoxchangedStyle = """QCheckBox::indicator { width: 20px; height: 20px;} QCheckBox{ background: #3a5b78}"""


        if abs(self.SliderPressureInspExp.value() - self.InspExp*50) > 1:
            self.SliderPressureInspExp.setStyleSheet(SliderchangedStyle)
        else:
            self.SliderPressureInspExp.setStyleSheet(SliderunchangedStyle)
            
        if abs(self.SliderPressureFreq.value() - self.Freq*1000*10*60) > 0.1:
            self.SliderPressureFreq.setStyleSheet(SliderchangedStyle)
        else:
            self.SliderPressureFreq.setStyleSheet(SliderunchangedStyle)
        
        if self.SliderPressureRiseTime.value() != self.InspRiseTime:
            self.SliderPressureRiseTime.setStyleSheet(SliderchangedStyle)
        else:
            self.SliderPressureRiseTime.setStyleSheet(SliderunchangedStyle)
         
        if self.SliderPressurePeep.value() != self.PressurePeep:
            self.SliderPressurePeep.setStyleSheet(SliderchangedStyle)
        else:
            self.SliderPressurePeep.setStyleSheet(SliderunchangedStyle)
        
        if self.SliderPressurePInsp.value() != self.PressureLimit:
            self.SliderPressurePInsp.setStyleSheet(SliderchangedStyle)
        else:
            self.SliderPressurePInsp.setStyleSheet(SliderunchangedStyle)
            
        if self.SliderPressureASBTrigger.value() != self.ASBThreshold:
            self.SliderPressureASBTrigger.setStyleSheet(SliderchangedStyle)
        else:
            self.SliderPressureASBTrigger.setStyleSheet(SliderunchangedStyle)
        
        if self.checkBoxPressureASBEnabled.isChecked() == True: 
            if self.ASBenable == 1: 
                self.checkBoxPressureASBEnabled.setStyleSheet(CheckBoxunchangedStyle)
            else: 
                self.checkBoxPressureASBEnabled.setStyleSheet(CheckBoxchangedStyle)
        else:
            if self.ASBenable == 0: 
                self.checkBoxPressureASBEnabled.setStyleSheet(CheckBoxunchangedStyle)
            else: 
                self.checkBoxPressureASBEnabled.setStyleSheet(CheckBoxchangedStyle)
        
        
        if abs(self.SliderVolumeInspExp.value() - self.InspExp*50) > 1:
            self.SliderVolumeInspExp.setStyleSheet(SliderchangedStyle)
        else:
            self.SliderVolumeInspExp.setStyleSheet(SliderunchangedStyle)
            
        if abs(self.SliderVolumeFreq.value() - self.Freq*1000*10*60) > 0.1:
            self.SliderVolumeFreq.setStyleSheet(SliderchangedStyle)
        else:
            self.SliderVolumeFreq.setStyleSheet(SliderunchangedStyle)
        
        if self.SliderVolumeRiseTime.value() != self.InspRiseTime:
            self.SliderVolumeRiseTime.setStyleSheet(SliderchangedStyle)
        else:
            self.SliderVolumeRiseTime.setStyleSheet(SliderunchangedStyle)
         
        if self.SliderVolumePeep.value() != self.PressurePeep:
            self.SliderVolumePeep.setStyleSheet(SliderchangedStyle)
        else:
            self.SliderVolumePeep.setStyleSheet(SliderunchangedStyle)
        
        if self.SliderVolumePMax.value() != self.MaxPressure:
            self.SliderVolumePMax.setStyleSheet(SliderchangedStyle)
        else:
            self.SliderVolumePMax.setStyleSheet(SliderunchangedStyle)
            
        if self.SliderVolumeASBTrigger.value() != self.ASBThreshold:
            self.SliderVolumeASBTrigger.setStyleSheet(SliderchangedStyle)
        else:
            self.SliderVolumeASBTrigger.setStyleSheet(SliderunchangedStyle)
            
        if self.checkBoxVolumeASBEnabled.isChecked() == True: 
            if self.ASBenable == 1: 
                self.checkBoxVolumeASBEnabled.setStyleSheet(CheckBoxunchangedStyle)
            else: 
                self.checkBoxVolumeASBEnabled.setStyleSheet(CheckBoxchangedStyle)
        else:
            if self.ASBenable == 0: 
                self.checkBoxVolumeASBEnabled.setStyleSheet(CheckBoxunchangedStyle)
            else: 
                self.checkBoxVolumeASBEnabled.setStyleSheet(CheckBoxchangedStyle)
        
        
    #Paint Trinamic logo   
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        windowWidth = self.width()
        windowheigt = self.height()
    
        xsize = 75
        ysize = 350/250*xsize
        
        xpadding = 3
        ypadding = 3
        
        xcor = windowWidth-xsize-xpadding
        ycor = windowheigt-ysize-ypadding
        painter.drawImage(QtCore.QRectF(xcor, ycor ,xsize, ysize), QtGui.QImage('resources/logos.svg'))
        painter.save()

    
    
    def getSettings(self):
        #Settings for Pressure Based Control 
        self.InspRiseTime  = self.Interface.getBoardParameter("TosvInhalationRiseTime")
        self.InspHoldTime = self.Interface.getBoardParameter("TosvInhalationPauseTime")
        self.ExpFallTime = self.Interface.getBoardParameter("TosvExhalationFallTime")
        self.ExpHoldTime = self.Interface.getBoardParameter("TosvExhalationPauseTime")
        self.PressureLimit = self.Interface.getBoardParameter("TosvLimitPressure")
        self.PressurePeep = self.Interface.getBoardParameter("TosvPeepPressure")
        self.CurrentMode  = self.Interface.getBoardParameter("TosvMode")
        self.ASBenable = self.Interface.getBoardParameter('ASBenable')
        self.ASBThreshold = self.Interface.getBoardParameter('ASBThreshold')
        self.MaxPressure = self.Interface.getBoardParameter("MaxPressure")
        self.TargetVT= self.Interface.getBoardParameter("MaxVolume")
    def updateGraph(self):
        
        x_axis = numpy.subtract(self.pressureTimeData, time.time())
        y_axis = self.pressureData
        self.PressureGraph.plot(x_axis, y_axis, clear=True,fillLevel=0, pen=self.pen ,brush=(255,255,255,255))
            
        x_axis = numpy.subtract(self.flowTimeData, time.time())
        y_axix = self.flowData
        self.FlowGraph.plot(x_axis, y_axix, clear=True,fillLevel=0, pen=self.pen ,brush=(255,255,255,255))

        x_axis = numpy.subtract(self.volumeTimeData, time.time())
        y_axix = self.volumeData
        self.VolumeGraph.plot(x_axis, y_axix, clear=True,fillLevel=0, pen=self.pen ,brush=(255,255,255,255))

    def writeOverviewLabels(self):
        self.LabelVolume.setText(str(self.cycleMaxVolume)+"ml")
        self.LabelAMV.setText(str("{:.2f}".format(self.actualAMV/1000))+"l/min")
        self.LabelPMax.setText(str(max(self.pressureData))+"mbar")
        if self.CurrentMode == 0:
            if self.ASBenable == 0:
                self.LabelMode.setText("P")
            else: 
                self.LabelMode.setText("P+ASB")
        else: 
            if self.ASBenable == 0:
                self.LabelMode.setText("V")
            else: 
                self.LabelMode.setText("V+ASB")
    #function called when start/stop button pressed. Starting program or counting down to confirm stop            
    def start_Stop_Button_pressed(self):
        print("running") 
        if self.Interface.isConnected() == True:
            if self.running == False:
                print("startTest") 
                self.Interface.startVentilation()
                self.running = True
            else:
                print("start timer") 
                self.timer_start_stop_button.start(1000)
                print("started timer") 
        
    #function called when start/stop button released. Stopping Timer for stop confrimation countdown             
    def start_Stop_Button_released(self):
        if self.running == True:
            print("stop timer") 
            self.timer_start_stop_button.stop()
        else:
            return
    
    #show buttons to confirm stop
    def confirm_stop(self):
        #insert change of buttons
        self.Start_Stop_Button.hide()
        self.StopButton.show()
        self.CancelButton.show()

    #stop button pressed
    def stop(self):
        self.running = False
        self.Interface.stopVentilation()
        self.Start_Stop_Button.show()
        self.StopButton.hide()
        self.CancelButton.hide()

    #cancel button pressed
    def cancel(self):
        self.Start_Stop_Button.show()
        self.StopButton.hide()
        self.CancelButton.hide()  
  
    #reconnect when no connection 
    #ToDo: try to detect lost connection
    def reconnect(self):
        if self.Interface.isConnected() == False:
            self.Interface.connect()
            self.wasconnected = False
        else: 
            if (self.wasconnected == False):
            #load values in board on connection start
                self.running = self.Interface.getStatus()
                self.clearMedChanges()
                self.wasconnected = True
                
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F11:
            if self.windowState() & QtCore.Qt.WindowFullScreen:
                self.showNormal()
            else:
                self.showFullScreen()

    '''Function writes the setted MedSetting values on button press to module   '''           
    def writeMedSettings(self):
        self.Interface.setBoardParameter("TosvMode",self.StackedModes.currentIndex())
        #For pressure based settings
        if self.StackedModes.currentIndex() == 0:
            self.Freq = self.SliderPressureFreq.value()/(10*60*1000)
            self.InspExp =  self.SliderPressureInspExp.value()/50
            self.InspRiseTime = self.SliderPressureRiseTime.value()
            self.PressureLimit = self.SliderPressurePInsp.value()
            self.Interface.setBoardParameter("TosvLimitPressure", int(self.PressureLimit))

            self.PressurePeep = self.SliderPressurePeep.value()
            self.Interface.setBoardParameter("ASBThreshold", self.SliderPressureASBTrigger.value())
            if self.checkBoxPressureASBEnabled.isChecked() == True:
                self.Interface.setBoardParameter("ASBenable", 1)
            else: 
                self.Interface.setBoardParameter("ASBenable", 0)
        #For volume based settings
        if self.StackedModes.currentIndex() == 1:
            self.Freq = self.SliderVolumeFreq.value()/(10*60*1000)
            self.InspExp =  self.SliderVolumeInspExp.value()/50
            self.InspRiseTime = self.SliderVolumeRiseTime.value()
            self.MaxPressure = self.SliderVolumePLimit.value()
            self.PressurePeep = self.SliderVolumePeep.value()
            self.Interface.setBoardParameter("MaxVolume",self.SliderVolumeVT.value())
            self.Interface.setBoardParameter("ASBThreshold", self.SliderVolumeASBTrigger.value())
            if self.checkBoxVolumeASBEnabled.isChecked() == True:
                self.Interface.setBoardParameter("ASBenable", 1)
            else: 
                self.Interface.setBoardParameter("ASBenable", 0)
            self.Interface.setBoardParameter("MaxPressure", int(self.MaxPressure))

            
        self.CalcPressTimes()
        self.Interface.setBoardParameter("TosvInhalationRiseTime",int(self.InspRiseTime))
        self.Interface.setBoardParameter("TosvInhalationPauseTime",int(self.InspHoldTime))
        self.Interface.setBoardParameter("TosvExhalationFallTime",int(self.ExpFallTime))
        self.Interface.setBoardParameter("TosvExhalationPauseTime",int(self.ExpHoldTime))
        self.Interface.setBoardParameter("TosvPeepPressure",int(self.PressurePeep))
        #Values on Overviewpage
        self.LabelPEEP.setText(str(self.PressurePeep/1000)+"mbar")
        self.LabelPLimit.setText(str(self.MaxPressure/1000)+"mbar")
        self.clearMedChanges()

    #Function setts the slieders in MedSettings back to values set in module 
    def clearMedChanges(self):
        self.getSettings()
        self.CalcPressSettings()
        self.StackedModes.setCurrentIndex(self.CurrentMode)
        self.ModeDropdown.setCurrentIndex(self.CurrentMode)
        #Set Slider for pressure control 
        self.SliderPressureInspExp.setValue(self.InspExp*50)
        self.SliderPressureFreq.setValue(self.Freq*1000*10*60)
        self.SliderPressureRiseTime.setValue(self.InspRiseTime)
        self.SliderPressurePInsp.setValue(self.PressureLimit)
        self.SliderPressurePeep.setValue(self.PressurePeep)
        self.SliderPressureASBTrigger.setValue(self.ASBThreshold)
        
        #Set Slider for volume control
        self.SliderVolumeInspExp.setValue(self.InspExp*50)
        self.SliderVolumeFreq.setValue(self.Freq*1000*10*60)
        self.SliderVolumeRiseTime.setValue(self.InspRiseTime)
        self.SliderVolumePMax.setValue(self.MaxPressure)
        self.SliderVolumePeep.setValue(self.PressurePeep)
        self.SliderVolumeVT.setValue(self.TargetVT)
        self.SliderVolumeASBTrigger.setValue(self.ASBThreshold)
        
        if self.ASBenable == 1:
            self.checkBoxPressureASBEnabled.setChecked(True)
            self.checkBoxVolumeASBEnabled.setChecked(True)
        else: 
            self.checkBoxPressureASBEnabled.setChecked(False)
            self.checkBoxVolumeASBEnabled.setChecked(False)
        
        #Set Labels  on overview page
        self.LabelPEEP.setText(str(self.PressurePeep/1000)+"mbar")
        self.LabelPLimit.setText(str(self.MaxPressure/1000)+"mbar")

        print("Loaded Settings from board")

    def writeMedSettingsLabels(self):
        #Pressure Settings
        if self.StackedModes.currentIndex() == 0:
            self.LabelSetPressureInspExp.setText(str(self.SliderPressureInspExp.value()/50))
            self.LabelSetPressureFreq.setText(str(self.SliderPressureFreq.value()/10)+"/min")
            self.LabelSetPressureRiseTime.setText(str(self.SliderPressureRiseTime.value()/1000)+"s")
            self.LabelSetPressurePEEP.setText(str(self.SliderPressurePeep.value()/1000)+"mbar")
            self.LabelSetPressurePLimit.setText(str(self.SliderPressurePInsp.value()/1000)+"mbar")
            self.Labelfreq.setText(str("{:.2f}".format(self.SliderPressureFreq.value()/10))+" /min")
            self.LabelSetPressureASB.setText(str(self.SliderPressureASBTrigger.value())+ "ml/min")

        #Volume Settings
        if self.StackedModes.currentIndex() == 1:
            self.LabelSetVolumeInspExp.setText(str(self.SliderVolumeInspExp.value()/50))
            self.LabelSetVolumeFreq.setText(str(self.SliderVolumeFreq.value()/10)+"/min")
            self.LabelSetVolumeRiseTime.setText(str(self.SliderVolumeRiseTime.value()/1000)+"s")
            self.LabelSetVolumePEEP.setText(str(self.SliderVolumePeep.value()/1000)+"mbar")
            self.LabelSetVolumePLimit.setText(str(self.SliderVolumePLimit.value()/1000)+"mbar")
            self.LabelSetVolumeVT.setText(str(self.SliderVolumeVT.value()))
            self.Labelfreq.setText(str("{:.2f}".format(self.SliderVolumeFreq.value()/10))+" /min")
            self.LabelSetVolumeASB.setText(str(self.SliderVolumeASBTrigger.value())+ "ml/min")

    def NullFlowSensor(self):
        self.Interface.setBoardParameter('ReInitFlowSensor', 1)
        self.Interface.ZeroFlowSensor()
        return
    
    def CalcPressTimes(self):
        TInsp = (1/self.Freq)/(1+(1/self.InspExp))
        TExp  = (1/self.Freq)-TInsp
        if TInsp >= self.InspRiseTime:
            self.InspHoldTime = TInsp-self.InspRiseTime 
        else: 
            #ToDo: Insert Error
            print("Settings not valid. Pressure ramp longer than inspiration time")
            self.InspRiseTime = TInsp 
            self.InspHoldTime = 0

        if TExp >= self.ExpFallTime:
            self.ExpHoldTime = TExp-self.ExpFallTime 
        else: 
            #ToDo: Insert Error
            print("Settings not valid. Expiration time to short")
            self.ExpHoldTime = 0
            self.Freq = 1/(TInsp+self.ExpFallTime) 
        self.CalcPressSettings()
    
    def CalcPressSettings(self):
        T = self.InspRiseTime+self.InspHoldTime+self.ExpFallTime+self.ExpHoldTime
        if T != 0:
            self.Freq = 1/T
        else:
            #ToDo:  Insert Error 
            return 
        self.InspExp = (self.InspRiseTime+self.InspHoldTime)/(self.ExpFallTime+self.ExpHoldTime)
        
        
    #Find Max in last cycle 
    def findMaxInCycle(self, ydata, statedata):
        if statedata[self.maxDataPoints-1] == 4:
            max = 0
            for x in range(self.maxDataPoints):
                if statedata[self.maxDataPoints-1] == 5:
                    break
                else:
                    if  ydata[(self.maxDataPoints-1)-x] > max:
                        max = ydata[(self.maxDataPoints-1)-x]
            return max
        return 
    
    def changeStackedModes(self):
        self.StackedModes.setCurrentIndex(self.ModeDropdown.currentIndex())
        
    def showIpInTecConfig(self):
        try: 
            ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
            self.LabelIpAddress.setText(str(ip))
        except:
            self.LabelIpAddress.setText('No Network')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    #app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    window = Ui()
    sys.exit(app.exec_())  