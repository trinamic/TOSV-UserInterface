# This Python file uses the following encoding: utf-8
'''
Created on 11.05.2020

@author: jh
This file is part of TOSV project. 
This should just be an inspiration or starting point for further development. 
A basic handler for alarms is implemented. 
'''
import time
from time import strftime
from PyQt5 import QtCore, QtGui
import pandas
from PyQt5.Qt import QColor

maxAlarms = 10

class AlarmHandler:
    def __init__(self):
        self.AlarmList = list()
        for x in range(maxAlarms):
            self.AlarmList.append(['', True, '',''])
    '''Init new alarm'''
    def newAlarm(self, Topic, Text, Status = False):
        Alarm =  list()  #Time, State, Topic, Text
        Alarm.append(strftime("%a, %d %b %Y %H:%M:%S"))
        Alarm.append(Status)
        Alarm.append(Topic)
        Alarm.append(Text)
        if Alarm[1:3] == self.lastAlarm()[1:3]: #avoid spamming 
            self.AlarmList[0] = Alarm
        else:
            self.AlarmList.insert(0, Alarm)
        if len(self.AlarmList) > maxAlarms:
            self.AlarmList.pop(maxAlarms)
    '''set alarm to cleared '''
    def clearAlarm(self, Index):
        self.AlarmList[Index][1] = True
    '''set all alarms to cleared '''
    def clearAll(self):
        leng = len(self.AlarmList)
        for x in range(leng):
            self.AlarmList[x][1] = True
        
    def lastAlarm(self):
        return  self.AlarmList[0]
    '''returns table model to display in UI'''
    def AlarmTable(self):
        data = pandas.DataFrame(self.AlarmList, columns = ['Time', 'Cleared', 'Topic', 'Description'])
        model = TableModel(data)
        return model 

class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)
        elif role == QtCore.Qt.BackgroundRole:
                state = self._data.iloc[index.row(), 1]
                if state == False:
                    color = QColor('#f7751f')
                    return color
    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]
    
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == QtCore.Qt.Vertical:
                return str(self._data.index[section])
    

    