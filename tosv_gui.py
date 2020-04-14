# This Python file uses the following encoding: utf-8
#Imports:
'''
Created on 14.04.2020

@author: jh
'''
#Imports
import sys
import numpy
import threading


from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic, QtCore, QtGui, Qt
import pyqtgraph as pg


import matplotlib
from matplotlib.figure import Figure
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

        #Define Varibles for Graph1 
        self.n_data = 50
        self.x_data = numpy.array(range(self.n_data))
        self.y_data = numpy.zeros(self.n_data)
        #self.y_data = numpy.sin(self.x_data/5)
        
        self.running = False

        #
        
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
        #Setting up Graph1
        self.graphWidget1 = self.findChild(pyqtgraph.PlotWidget, 'Graph1')
        self.pen = pg.mkPen(color=(0, 0, 0))
        self.graphWidget1.setBackground((20, 145, 204))
        self.graphWidget1.showGrid(x=True, y=True)
        self.graphWidget1.plot(self.x_data, self.y_data,fillLevel=0, pen=self.pen ,brush=(255,255,255,255))
        self.graphWidget1xaxis  = self.graphWidget1.getAxis('bottom')
        self.graphWidget1xaxis.setHeight(0)
         
        #Setting up Graph2
        self.graphWidget2 = self.findChild(pyqtgraph.PlotWidget, 'Graph2')
        self.pen = pg.mkPen(color=(0, 0, 0))
        self.graphWidget2.setBackground((20, 145, 204))
        self.graphWidget2.showGrid(x=True, y=True)
        self.graphWidget2.plot(self.x_data, self.y_data,fillLevel=0, pen=self.pen ,brush=(255,255,255,255))
        self.graphWidget2xaxis  = self.graphWidget1.getAxis('bottom')
        self.graphWidget2xaxis.setHeight(0)
 
        #Define Timers
        #Timer for long button press
        self.timer_start_stop_button = QtCore.QTimer()
        self.timer_start_stop_button.setSingleShot(True)
        self.timer_start_stop_button.timeout.connect(self.confirm_stop)
        #Timer for refreshing GUI
        self.timer_gui = QtCore.QTimer()
        self.timer_gui.timeout.connect(self.update_gui)
        self.timer_gui.start(50)  # every 50 millisecon
        #Timer for trying reconnect
        self.timer_reconnect = QtCore.QTimer()
        self.timer_reconnect.timeout.connect(self.reconnect)
        self.timer_reconnect.start(1000) #Dont set to low.. otherwise the connection will fail
        
        #Show Window, depending on Fullscreen setting. 
        global fullscreen
        if fullscreen == True:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.showFullScreen()
        else:
            self.show()        

    #Updating the GUI periodically, called by timer. 
    #ToDo: Cleanup 
    def update_gui(self):
        if self.Interface.getConnection() == True:
            #Update Graph1
            self.data1 = self.Interface.getActualVelocity()
            self.y_data = numpy.roll(self.y_data,-1)
            self.y_data[self.n_data-1] = self.data1
            self.graphWidget1.plot(self.x_data, self.y_data, clear=True,fillLevel=0, pen=self.pen ,brush=(255,255,255,255))
            
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
            
            
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    #app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    window = Ui()
    sys.exit(app.exec_())  