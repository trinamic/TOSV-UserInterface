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

from PyQt5 import QtWidgets, uic, QtCore
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
        
        #self.y_data = numpy.sin(self.x_data/5)
        
        self.running = False

        #Define Buttons
        self.ConnectButton = self.findChild(QtWidgets.QPushButton, 'ConnectButton')
        self.Start_Stop_Button = self.findChild(QtWidgets.QPushButton, 'StartButton')
        self.StopButton = self.findChild(QtWidgets.QPushButton, 'StopButton')
        self.CancelButton = self.findChild(QtWidgets.QPushButton, 'CancelButton')
        self.DisconnectButton = self.findChild(QtWidgets.QPushButton, 'DisconnectButton')
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
        #Buttons are disabled
        #self.ConnectButton.clicked.connect(self.Interface.connect)
        #self.DisconnectButton.clicked.connect(self.Interface.disconnect)
    
    
        #Define Labels
        #self.LabelCurrRPM = self.findChild(QtWidgets.QLabel, 'CurrentMotorRPM')
        
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
            #Update VolumeGraph
            self.data = self.Interface.getActualVelocity()
            if self.data:
                if self.Volume_data.size < self.maxDataPoints:
                    self.Volume_data = numpy.append(self.Volume_data , self.data)
                    self.time_data = numpy.append(self.time_data , time.time())
                else:
                    self.Volume_data = numpy.roll(self.Volume_data,-1)
                    self.time_data = numpy.roll(self.time_data,-1)
                    self.y_data[self.Volume_data.size-1] = self.data1
                    self.time_data[self.time_data.size-1] = time.time()
            x_axis = numpy.subtract(self.time_data,time.time())
            y_axix = self.Volume_data
            self.VolumeGraph.plot(x_axis, y_axix, clear=True,fillLevel=0, pen=self.pen ,brush=(255,255,255,255))
            
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
            self.Start_Stop_Button.setStyleSheet("background-color : rgb(255, 255, 0)")  
    
    #function called when start/stop button pressed. Starting program or counting down to confirm stop            
    def start_Stop_Button_pressed(self):
        print("running") 
        if self.Interface.getConnection() == True:
            if self.running == False:
                print("startTest") 
                self.Interface.startTest()
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
        self.Interface.stopTest()
        self.Start_Stop_Button.show()
        self.StopButton.hide()
        self.CancelButton.hide()
    #cancel button pressed
    def cancel(self):
        self.Start_Stop_Button.show()
        self.StopButton.hide()
        self.CancelButton.hide()    
    #reconnect when no connection 
    #ToDo: try to detekt lost connection
    def reconnect(self):
        if(self.Interface.getConnection() == False):
            self.Interface.connect()
            
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F11:
            if self.windowState() & QtCore.Qt.WindowFullScreen:
                self.showNormal()
            else:
                self.showFullScreen()
            
            
            
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    #app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    window = Ui()
    sys.exit(app.exec_())  