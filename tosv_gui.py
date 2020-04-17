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

from PyQt5 import QtWidgets, uic, QtCore, QtGui, Qt
import pyqtgraph as pg


import matplotlib
from TOSV_Interface import TOSV_Interface
import pyqtgraph

matplotlib.use('Qt5Agg')

#Set to True in for fullscreen 
fullscreen = False 

class Ui(QtWidgets.QWidget):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('TOSV-GUI.ui', self)
        self.Interface = TOSV_Interface()
        self.updatetime = 50        
                
        #Define Varibles for VolumeGraph 
        self.maxDataPoints = 12*60*60*(1000/self.updatetime)#For aprox. 12h of data record
        #self.n_data = 50 
        #self.x_data = numpy.array(range(self.n_data))
        self.time_data = numpy.array([time.time()])
        self.Volume_data = numpy.array([0])
        self.Flow_data = numpy.array([0])
        self.Pressure_data = numpy.array([0])

        
        #self.y_data = numpy.sin(self.x_data/5)
        
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
        self.LabelVolume = self.findChild(QtWidgets.QLabel, 'VolumeLabel')
        self.LabelFlow = self.findChild(QtWidgets.QLabel, 'FlowLabel')
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
        self.VolumeGraph = self.findChild(pyqtgraph.PlotWidget,'VolumeGraph')
        self.pen = pg.mkPen(color=(0, 0, 0))
        self.VolumeGraph.setBackground((20, 145, 204))
        self.VolumeGraph.showGrid(x=True, y=True)
        self.VolumeGraph.plot(self.time_data, self.Volume_data,fillLevel=0, pen=self.pen ,brush=(255,255,255,255))
        self.VolumeGraphxaxis  = self.VolumeGraph.getAxis('bottom')
        self.VolumeGraph.setXRange(-60,0)
         
        #Setting up FlowGraph
        self.FlowGraph = self.findChild(pyqtgraph.PlotWidget, 'FlowGraph')
        self.pen = pg.mkPen(color=(0, 0, 0))
        self.FlowGraph.setBackground((20, 145, 204))
        self.FlowGraph.showGrid(x=True, y=True)
        #self.FlowGraph.plot(self.x_data, self.y_data,fillLevel=0, pen=self.pen ,brush=(255,255,255,255))
        self.FlowGraphxaxis  = self.FlowGraph.getAxis('bottom')
        
        #Setting up PressureGraph
        self.PressureGraph = self.findChild(pyqtgraph.PlotWidget, 'PressureGraph')
        self.pen = pg.mkPen(color=(0, 0, 0))
        self.PressureGraph.setBackground((20, 145, 204))
        self.PressureGraph.showGrid(x=True, y=True)
        #self.FlowGraph.plot(self.x_data, self.y_data,fillLevel=0, pen=self.pen ,brush=(255,255,255,255))
        self.PressureGraphxaxis  = self.FlowGraph.getAxis('bottom')
 
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
        global fullscreen
        if fullscreen == True:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.showFullScreen()
            #self.setCursor(QtCore.Qt.BlankCursor)
        else:
            self.show()
            
    #Updating the GUI periodically, called by timer. 
    #ToDo: Cleanup 
    def update_gui(self):
        if self.Interface.getConnection() == True:
            self.SetMedSettingsButton.setEnabled(True);
            self.CancelMedSettingsButton.setEnabled(True);
            #Update VolumeGraph
            self.data = self.Interface.getActualPressure()
            if self.data:
                if self.Pressure_data.size < self.maxDataPoints:
                    self.Pressure_data = numpy.append(self.Pressure_data , self.data)
                    self.time_data = numpy.append(self.time_data , time.time())
                else:
                    self.Pressure_data = numpy.roll(self.Pressure_data,-1)
                    self.time_data = numpy.roll(self.time_data,-1)
                    self.y_data[self.Volume_data.size-1] = self.data1
                    self.time_data[self.time_data.size-1] = time.time()
            x_axis = numpy.subtract(self.time_data,time.time())
            y_axix = self.Pressure_data
            self.PressureGraph.plot(x_axis, y_axix, clear=True,fillLevel=0, pen=self.pen ,brush=(255,255,255,255))
            
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
            self.SetMedSettingsButton.setEnabled(False);
            self.CancelMedSettingsButton.setEnabled(False);
            self.Start_Stop_Button.setStyleSheet("background-color : rgb(255, 255, 0)")  
    
        #Update Values under slieder
        self.LabelSetTInspRise.setText(str(self.TInspRiseSlider.value()/1000)+"s")
        self.LabelSetTInspHold.setText(str(self.TInspHoldSlider.value()/1000)+"s")
        self.LabelSetTExpFall.setText(str(self.TExpFallSlider.value()/1000)+"s")
        self.LabelSetTExpHold.setText(str(self.TExpHoldSlider.value()/1000)+"s")
        
        self.LabelSetPEEP.setText(str(self.PEEPSlider.value()/100)+"mbar")
        self.LabelSetPLimit.setText(str(self.PLimitSlider.value()/100)+"mbar")
        CycleTime = self.TInspRiseSlider.value()+self.TInspHoldSlider.value()+self.TExpFallSlider.value()+self.TExpHoldSlider.value()
        if CycleTime != 0:
            CycleFreq = 60000/CycleTime
            self.LabelResultFreq.setText(str("{:.2f}".format(CycleFreq))+" /min")
        else: 
            self.LabelResultFreq.setText("--")

    
    
    #function called when start/stop button pressed. Starting program or counting down to confirm stop            
    #Paint Trinamic logo
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        xcor = 689
        ycor = 395
        xsize = 125
        ysize = 110/170*xsize
        painter.drawImage(QtCore.QRectF(xcor, ycor ,xsize, ysize), QtGui.QImage('resources/trinamic_logo.svg'))
        painter.setPen(QtGui.QColor(0,0,0))
        painter.setFont(QtGui.QFont('OpenSans', 10))
        painter.drawText(QtCore.QRectF(xcor, ycor+ysize, ysize, ysize), QtCore.Qt.AlignCenter, "TOSV")
        painter.save()
    
    def start_Stop_Button_pressed(self):
        print("running") 
        if self.Interface.getConnection() == True:
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
        if self.Interface.getConnection() == False:
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
        self.Interface.setInhalationPouseTime(self.TInspHoldSlider.value())
        self.Interface.setExhalationFallTime(self.TExpFallSlider.value())
        self.Interface.setExhalationPauseTime(self.TExpHoldSlider.value())
        self.Interface.setLIMITPresssure(self.PLimitSlider.value())
        self.Interface.setPEEPPressure(self.PEEPSlider.value())
        return 
    #Function setts the slieders in MedSettings back to values set in module 
    def clearMedChanges(self):
        try:
            self.TInspRiseSlider.setValue(self.Interface.getInhalationRiseTime())
            self.TInspHoldSlider.setValue(self.Interface.getInhalationPouseTime())
            self.TInspRiseSlider.setValue(self.Interface.getInhalationRiseTime())
            self.TExpFallSlider.setValue(self.Interface.getExhalationFallTime())
            self.TExpHoldSlider.setValue(self.Interface.getExhalationPauseTime())
            self.PLimitSlider.setValue(self.Interface.getLIMITPresssure())
            self.PEEPSlider.setValue(self.Interface.getPEEPPressure())
            print("Loading Settings from board")
        except:
            print("ERROR, Loading Settings from board")
       
         
                
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    #app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    window = Ui()
    sys.exit(app.exec_())  