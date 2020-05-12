# This Python file uses the following encoding: utf-8
'''
Created on 11.05.2020

@author: jh
'''
import time
from time import gmtime, strftime
from PyQt5 import QtCore
import pandas


class AlarmHandler:
    def __init__(self):
        self.Alarm =  list()
        self.maxAlarms = 50 
        self.AlarmList = list()
        self.newAlarm("System","AlarmSystem initialised", True)
    def newAlarm(self, Topic, Text, Status = False):
        self.Alarm.clear()
        self.Alarm.append(strftime("%a, %d %b %Y %H:%M:%S"))
        self.Alarm.append(Status)
        self.Alarm.append(Topic)
        self.Alarm.append(Text)
        self.AlarmList.append(self.Alarm)
        if len(self.AlarmList) > self.maxAlarms:
            self.AlarmList.pop(0)
            
    def clearAlarm(self, Index):
        return
    def lastAlarm(self):
        leng = len(self.AlarmList)
        return  self.AlarmList[leng-1]
    def clearAll(self):
        leng = len(self.AlarmList)
        for x in range(leng):
            self.AlarmList[x][1] = True
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
    