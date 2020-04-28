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

from PyQt5 import QtWidgets, uic, QtCore, QtGui
import pyqtgraph 

from TOSV_Interface import TOSV_Interface

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
        self.cycleTime = 0
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
                    
        self.running = False
        self.wasconnected = False

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
        #Define Sliders
        self.TInspRiseSlider = self.findChild(QtWidgets.QSlider, 'SliderTInspRise')
        self.TInspHoldSlider = self.findChild(QtWidgets.QSlider, 'SliderTInspHold')
        self.TExpFallSlider = self.findChild(QtWidgets.QSlider, 'SliderTExpFall')
        self.TExpHoldSlider = self.findChild(QtWidgets.QSlider, 'SliderTExpHold')
        
        self.PEEPSlider = self.findChild(QtWidgets.QSlider, 'SliderPEEP')
        self.PLimitSlider = self.findChild(QtWidgets.QSlider, 'SliderPLimit')
            
        #Define Labels
        #Labels in Overview
        self.LabelVolume = self.findChild(QtWidgets.QLabel, 'VTLabel')
        self.LabelAMV = self.findChild(QtWidgets.QLabel, 'AMVLabel')
        self.LabelPMax = self.findChild(QtWidgets.QLabel, 'PMaxLabel')
        self.LabelPLimit = self.findChild(QtWidgets.QLabel, 'PLimLabel')
        self.LabelPEEP = self.findChild(QtWidgets.QLabel, 'PeepLabel')
        self.Labelfreq = self.findChild(QtWidgets.QLabel, 'fLabel')
        
        #Labels in MedSettings
        self.LabelSetTInspRise = self.findChild(QtWidgets.QLabel, 'SetTInspRise')
        self.LabelSetTInspHold = self.findChild(QtWidgets.QLabel, 'SetTInspHold')
        self.LabelSetTExpFall = self.findChild(QtWidgets.QLabel, 'SetTExpFall')
        self.LabelSetTExpHold = self.findChild(QtWidgets.QLabel, 'SetTExpHold')
        self.LabelSetPEEP = self.findChild(QtWidgets.QLabel, 'SetPeepLabel')
        self.LabelSetPLimit = self.findChild(QtWidgets.QLabel, 'setPLimitLabel')
        self.LabelResultFreq = self.findChild(QtWidgets.QLabel, 'ResultingFreqLabel')
    
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
 
        #Define Timers
        #Timer for long button press
        self.timer_start_stop_button = QtCore.QTimer()
        self.timer_start_stop_button.setSingleShot(True)
        self.timer_start_stop_button.timeout.connect(self.confirm_stop)
        
        #Timer for refreshing GUI
        self.timer_gui = QtCore.QTimer()
        self.timer_gui.timeout.connect(self.update_gui)
        self.timer_gui.start(self.updatetime)  # every 50 millisecon
        
        #Timer for trying reconnect
        self.timer_reconnect = QtCore.QTimer()
        self.timer_reconnect.timeout.connect(self.reconnect)
        self.timer_reconnect.start(1000) #Dont set to low.. otherwise the connection will fail
        
        
        #Show Window, depending on Fullscreen setting. 
        self.setWindowTitle('TOSV UserInterface')
        if fullscreen:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.showFullScreen()
            #self.setCursor(QtCore.Qt.BlankCursor)
        else:
            self.show()
        
    #Updating the GUI periodically, called by timer. 
    #ToDo: Cleanup 
    def update_gui(self):
        if self.Interface.isConnected() == True:
            self.SetMedSettingsButton.setEnabled(True)
            self.CancelMedSettingsButton.setEnabled(True)
            # update pressure graph
            #self.getValues()
            multiprocessing.Process(target=self.getValues())
            self.updateGraph()
            #multiprocessing.Process(target=self.updateGraph())
            self.writeOverviewLabels()
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
    def checkSliderChanged(self):
        #ToDo. rewrite with local Variables
        changedStyle = """.QSlider {} 
        .QSlider::groove:vertical {border: 1px solid #262626;width: 5px;background: rgb(255, 255, 255) ;margin: 0 12px;}
        .QSlider::handle:vertical {background:#3a5b78 ; border: 1px solid rgb(0, 0, 0); height: 30px; margin: -0px -35px;}"""
        unchangedStyle = """.QSlider {}
        .QSlider::groove:vertical {border: 1px solid #262626;width: 5px;background: rgb(255, 255, 255) ;margin: 0 12px;}
        .QSlider::handle:vertical {background:#afb3b6 ; border: 1px solid rgb(0, 0, 0); height: 30px; margin: -0px -35px;}"""

        if self.TInspRiseSlider.value() != self.Interface.getInhalationRiseTime():
            self.TInspRiseSlider.setStyleSheet(changedStyle)
        else:
            self.TInspRiseSlider.setStyleSheet(unchangedStyle)
            
        if self.TInspHoldSlider.value() != self.Interface.getInhalationPauseTime():
            self.TInspHoldSlider.setStyleSheet(changedStyle)
        else:
            self.TInspHoldSlider.setStyleSheet(unchangedStyle)
             
        if self.TExpFallSlider.value() != self.Interface.getExhalationFallTime():
            self.TExpFallSlider.setStyleSheet(changedStyle)
        else:
            self.TExpFallSlider.setStyleSheet(unchangedStyle)
             
        if self.TExpHoldSlider.value() != self.Interface.getExhalationPauseTime():
            self.TExpHoldSlider.setStyleSheet(changedStyle)
        else:
            self.TExpHoldSlider.setStyleSheet(unchangedStyle)
#             
        if self.PEEPSlider.value() != self.Interface.getPeepPressure():
            self.PEEPSlider.setStyleSheet(changedStyle)
        else:
            self.PEEPSlider.setStyleSheet(unchangedStyle)
            
        if self.PLimitSlider.value() != self.Interface.getLimitPresssure():
            self.PLimitSlider.setStyleSheet(changedStyle)
        else:
            self.PLimitSlider.setStyleSheet(unchangedStyle)
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
    def getValues(self):
        #Get Sensor Data
        self.actualPressure = self.Interface.getActualPressure()
        self.actualVolume = self.Interface.getActualVolume()
        self.actualFlow = self.Interface.getActualFlow()
        self.currentState = self.Interface.getCurrentState()
        
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
                if self.cycleTime != 0:
                    self.actualAMV = self.cycleMaxVolume*self.cycleFreq

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
        self.LabelAMV.setText(str("{:.2f}".format(self.actualAMV))+"ml/min")
        self.LabelPMax.setText(str(max(self.pressureData))+"mbar")
        
    def writeMedSettingsLabels(self):
        self.LabelSetTInspRise.setText(str(self.TInspRiseSlider.value()/1000)+"s")
        self.LabelSetTInspHold.setText(str(self.TInspHoldSlider.value()/1000)+"s")
        self.LabelSetTExpFall.setText(str(self.TExpFallSlider.value()/1000)+"s")
        self.LabelSetTExpHold.setText(str(self.TExpHoldSlider.value()/1000)+"s")
        
        self.LabelSetPEEP.setText(str(self.PEEPSlider.value()/1000)+"mbar")
        self.LabelSetPLimit.setText(str(self.PLimitSlider.value()/1000)+"mbar")
        self.cycleTime = self.TInspRiseSlider.value()+self.TInspHoldSlider.value()+self.TExpFallSlider.value()+self.TExpHoldSlider.value()
        
        if self.cycleTime != 0:
            self.cycleFreq = 60000/self.cycleTime
            self.LabelResultFreq.setText(str("{:.2f}".format(self.cycleFreq))+" /min")
            self.Labelfreq.setText(str("{:.2f}".format(self.cycleFreq))+" /min")

        else: 
            self.LabelResultFreq.setText("--")
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

    #Function writes the setted MedSetting values on button press to module              
    def writeMedSettings(self):
        self.Interface.setInhalationRiseTime(self.TInspRiseSlider.value())
        self.Interface.setInhalationPauseTime(self.TInspHoldSlider.value())
        self.Interface.setExhalationFallTime(self.TExpFallSlider.value())
        self.Interface.setExhalationPauseTime(self.TExpHoldSlider.value())
        self.Interface.setLimitPresssure(self.PLimitSlider.value())
        self.Interface.setPeepPressure(self.PEEPSlider.value())
        #Values on Overviewpage
        self.LabelPEEP.setText(str(self.Interface.getPeepPressure()/1000)+"mbar")
        self.LabelPLimit.setText(str(self.Interface.getLimitPresssure()/1000)+"mbar")

    #Function setts the slieders in MedSettings back to values set in module 
    def clearMedChanges(self):
        self.TInspRiseSlider.setValue(self.Interface.getInhalationRiseTime())
        self.TInspHoldSlider.setValue(self.Interface.getInhalationPauseTime())
        self.TExpFallSlider.setValue(self.Interface.getExhalationFallTime())
        self.TExpHoldSlider.setValue(self.Interface.getExhalationPauseTime())
        self.PLimitSlider.setValue(self.Interface.getLimitPresssure())
        self.PEEPSlider.setValue(self.Interface.getPeepPressure())
        #Set Labels  on overview page
        self.LabelPEEP.setText(str(self.Interface.getPeepPressure()/1000)+"mbar")
        self.LabelPLimit.setText(str(self.Interface.getLimitPresssure()/1000)+"mbar")

        print("Loaded Settings from board")
    
    def NullFlowSensor(self):
        self.Interface.ZeroFlowSensor()
        return
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
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    #app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    window = Ui()
    sys.exit(app.exec_())  