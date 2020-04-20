'''
Created on 09.04.2020

@author: ed
'''

if __name__ == '__main__':
    pass

from PyTrinamic.connections.ConnectionManager import ConnectionManager
from modules.TMC4671_TMC6100_TOSV_REF import TMC4671_TMC6100_TOSV_REF
import time

# connectionManager = ConnectionManager("--interface serial_tmcl --port COM20 --data-rate 115200".split())
connectionManager = ConnectionManager("--interface serial_tmcl --port COM4 --data-rate 115200".split())
myInterface = connectionManager.connect()

module = TMC4671_TMC6100_TOSV_REF(myInterface)

" motor configuration "
module.setAxisParameter(module.APs.MaxCurrent, 1000)
module.showMotorConfiguration()

" hall sensor configuration"
module.showHallConfiguration()

" motion configuration "
module.setAxisParameter(module.APs.MaxVelocity, 1000)
module.setAxisParameter(module.APs.Acceleration, 1000)
module.showMotionConfiguration()

" PI controller configuration "
module.showPIConfiguration()

" show selected feedback system "
module.showSelectedCommutationFeedback()

for x in range(5):
    
    module.setAxisParameter(module.APs.Acceleration, 2000)
    module.rotate(1000)
    time.sleep(1.2);
    
    module.setAxisParameter(module.APs.Acceleration, 4000)
    module.rotate(200)
    time.sleep(1.2);

" stop motor "
module.setAxisParameter(module.APs.TargetCurrent, 0)

print()
print("Ready.")
myInterface.close()