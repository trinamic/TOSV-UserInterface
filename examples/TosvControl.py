'''
Created on 17.04.2020

@author: ed
'''

if __name__ == '__main__':
    pass

from PyTrinamic.connections.ConnectionManager import ConnectionManager
from modules.TMC4671_TMC6100_TOSV_REF import TMC4671_TMC6100_TOSV_REF
import time

connectionManager = ConnectionManager("--interface serial_tmcl --port COM4 --data-rate 115200".split())
myInterface = connectionManager.connect()

module = TMC4671_TMC6100_TOSV_REF(myInterface)

" motor configuration "
module.setAxisParameter(module.APs.MaxCurrent, 2000)
module.showMotorConfiguration()

" hall sensor configuration"
module.showHallConfiguration()

" PI controller configuration "
module.setAxisParameter(module.APs.PressureP, 500)
module.setAxisParameter(module.APs.PressureI, 1000)
module.showPIConfiguration()

" show selected feedback system "
module.showSelectedCommutationFeedback()

" tosv configuration"
module.setAxisParameter(module.APs.TosvInhalationRiseTime, 300)
module.setAxisParameter(module.APs.TosvInhalationPauseTime, 1000)
module.setAxisParameter(module.APs.TosvExhalationFallTime, 200)
module.setAxisParameter(module.APs.TosvExhalationPauseTime, 1500)
module.setAxisParameter(module.APs.TosvLimitPresssure, 10000)
module.setAxisParameter(module.APs.TosvPeepPressure, 1500)
module.showTosvConfiguration()

print()

" start ventilator state machine"
module.setAxisParameter(module.APs.TosvEnable, 1)

startTime = time.time()
lastState = module.axisParameter(module.APs.TosvState)
print("TOSV state: " + str(lastState) + " (" + module.stateToName(lastState) + ")")

while ((time.time() - startTime) <= 17.0):
    newState = module.axisParameter(module.APs.TosvState)
    if (lastState != newState):
        print("TOSV state: " + str(newState) + " (" + module.stateToName(newState) + ")")
        lastState = newState

" stop ventilator state machine "
module.setAxisParameter(module.APs.TosvEnable, 0)

newState = module.axisParameter(module.APs.TosvState)
print("TOSV state: " + str(newState) + " (" + module.stateToName(newState) + ")")

print()
print("Ready.")
myInterface.close()