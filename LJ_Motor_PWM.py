"""
Stepper Motor test script for BASF custom hose reel project.

Drives a PWM signal through the LabJack into the Kollmorgen P6000 stepper drive.
See drive datasheet for hook up details. PWM signal driven out of DIO0 pin on T7 LabJack
Terminal outputs PWM, duty cycle, and calculated RPM

6.11.19 - Working to drive motor at given duty cycle and frequency. Default parameters are 200 step size,
1000 Hz, and 50% duty cycle.

"""

# Imports
from labjack import ljm
import time


# Open first found LabJack
handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier

#targetFreq = 1000 # in Hz
#dutyCycle = 50 # dDefined as %

# DRIVE PARAMETERS - Change as needed given driver set up.
targetRPM = 300
dutyCycle = 1
stepSize = 1600
targetFreq = (targetRPM*stepSize)/60

# Set up the clock
DIO_EF_CLOCK0_ENABLE = 0
DIO_EF_CLOCK0_DIVISOR = 1
DIO_EF_CLOCK0_ROLL_VALUE = (80e6)/(DIO_EF_CLOCK0_DIVISOR*targetFreq) # based on 80MHz clock
DIO_EF_CLOCK0_ENABLE = 1

# Set up PWM signal
DIO0_EF_ENABLE = 0
DIO0_EF_INDEX = 0
DIO0_EF_CONFIG_A = (dutyCycle*(8000/100))
DIO0_EF_ENABLE = 1
DIO_DUTY_CYCLE = 80000*(dutyCycle/100)
# Set up signal check
DIO1_EF_ENABALE = 0
DIO1_EF_INDEX = 5
DIO1_EF_OPTONS = 0
DIO1_EF_ENABALE = 1

# Get info and print settings
info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))
print("  ")
print("Roll Value: " + str(DIO_EF_CLOCK0_ROLL_VALUE))
print("CONFIG A: " + str(DIO0_EF_CONFIG_A))
print("Configuring clock.....")

# Configure Clock Registers:
ljm.eWriteName(handle, "DIO_EF_CLOCK0_ENABLE", 0) #Disable clock source

# Set Clock0's divisor and roll value to configure frequency: 80MHz/1/80000 = 1kHz
ljm.eWriteName(handle, "DIO_EF_CLOCK0_DIVISOR", 1)# Configure Clock0's divisor
#ljm.eWriteName(handle, "DIO_EF_CLOCK0_ROLL_VALUE", 80000)# Configure Clock0's roll value
ljm.eWriteName(handle, "DIO_EF_CLOCK0_ROLL_VALUE", DIO_EF_CLOCK0_ROLL_VALUE)# Configure Clock0's roll value
ljm.eWriteName(handle, "DIO_EF_CLOCK0_ENABLE", 1)# Enable the clock source

# Configure EF Channel Registers for signal:
ljm.eWriteName(handle, "DIO0_EF_ENABLE", 0)# Disable the EF system for initial configuration
ljm.eWriteName(handle, "DIO0_EF_INDEX", 0)# Configure EF system for PWM
ljm.eWriteName(handle, "DIO0_EF_OPTIONS", 0)# Configure what clock source to use: Clock0
#ljm.eWriteName(handle, "DIO0_EF_CONFIG_A",40000)# Configure duty cycle to be: 50%
ljm.eWriteName(handle, "DIO0_EF_CONFIG_A", DIO_DUTY_CYCLE)# Configure duty cycle to be: 50%
ljm.eWriteName(handle, "DIO0_EF_ENABLE", 1)# Enable the EF system, PWM wave is now being outputted

# Configure EF Channel Registers for digital input check:
ljm.eWriteName(handle, "DIO1_EF_ENABLE", 0)
ljm.eWriteName(handle, "DIO1_EF_INDEX", 5)
ljm.eWriteName(handle, "DIO1_EF_OPTIONS", 0)
ljm.eWriteName(handle, "DIO1_EF_ENABLE", 1)

# Hard code direction high
ljm.eWriteName(handle, "DIO3", 1)

# Test the function and write outputs to terminal
while True:
    highTime = ljm.eReadName(handle, "DIO1_EF_READ_A_F")
    lowTime = ljm.eReadName(handle, "DIO1_EF_READ_B_F")
    #print("High Time (s): " + str(highTime))
    #print("Low Time (s(): " + str(lowTime))
    total = highTime + lowTime
    time.sleep(2)
    if total > 0:
        recordFreq = 1 / total
        duty = (highTime/total)*100
        RPM = 60 * (recordFreq / stepSize)
        print ("PWM Frequency (Hz): " + str(recordFreq))
        print ("Duty Cycle (%): " + str(duty))
        print("Target RPM: " + str(RPM))
        print (" ")

ljm.close(handle)

