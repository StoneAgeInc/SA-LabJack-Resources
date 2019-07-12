'''
Basic building blocks for PWM-driven servo motor driver via Labjack T7
Author: Chris Antle
Created: 7.12.19
Modified: 7.12.19

LabJack PWM Documentation: https://labjack.com/support/datasheets/t-series/digital-io/extended-features/pwm-out
Labjack Pulse Documentation: https://labjack.com/support/datasheets/t-series/digital-io/extended-features/pulse-out

'''


from labjack import ljm
import time

# Open first found LabJack
handle = ljm.openS("T7", "ANY", "ANY")  # T7 device, Any connection, Any identifier

# Define globals
motorEnabled = False # Initially have motor stopped
motorEnable = 5 # Initially set to have motor disabled
microstep = 4000 # Microstep based on motor driven dip switch setting
motorEnable = "DAC0"


'''
Creates a default 1 kHz PWM wave with 50% duty cycle
RPM calculation depends on microstep size
Assumes 80MHz clock and clock divisor of 1
'''
def generateDefaultPWM():
    # Configure Clock Registers:
    ljm.eWriteName(handle, "DIO_EF_CLOCK0_ENABLE", 0)  # Disable clock source
    # Set Clock0's divisor and roll value to configure frequency: 80MHz/1/80000 = 1kHz
    ljm.eWriteName(handle, "DIO_EF_CLOCK0_DIVISOR", 1)  # Configure Clock0's divisor
    # ljm.eWriteName(handle, "DIO_EF_CLOCK0_ROLL_VALUE", 80000)# Configure Clock0's roll value
    ljm.eWriteName(handle, "DIO_EF_CLOCK0_ROLL_VALUE", 8000)  # Configure Clock0's roll value
    ljm.eWriteName(handle, "DIO_EF_CLOCK0_ENABLE", 1)  # Enable the clock source

    # Configure EF Channel Registers for signal:
    ljm.eWriteName(handle, "DIO2_EF_ENABLE", 0)  # Disable the EF system for initial configuration
    ljm.eWriteName(handle, "DIO2_EF_INDEX", 0)  # Configure EF system for PWM
    ljm.eWriteName(handle, "DIO2_EF_OPTIONS", 0)  # Configure what clock source to use: Clock0
    ljm.eWriteName(handle, "DIO2_EF_CONFIG_A", 4000)  # Configure duty cycle to be: 50%
    ljm.eWriteName(handle, "DIO2_EF_ENABLE", 1)  # Enable the EF system, PWM wave is now being outputted

    RPM = (1/microstep)*1000*60
    print("Motor RPM: " + str(RPM))


'''
Creates a user-defined PWM signal with variables of output pin, frequency, and duty cycle
RPM calculation depends on microstep size
Assumes 80MHz clock and clock divisor of 1
T7 Pro valid PWM outputs are 0, 2-5 only
'''
def generateUserPWM(pin, freq, duty):
    #Check output pin valid
    if pin == 0 or pin in range(2, 6):
        # Set up math
        clock = 80E6
        clockDivisor = 1
        rollValue = (clock/clockDivisor)/freq
        dutyConfig = rollValue*duty
        RPM = (1/microstep)*freq*60

        # Print statements for debug
        print("Output Pin (DIO): " + str(pin))
        print("PWM Frequency (Hz): " + str(freq))
        print("Roll Value: " + str(rollValue))
        print("Duty Cycle (%): " + str(duty*100))
        print("Motor RPM: " + str(RPM))
        print(" ")

        # Configure Clock Registers:
        ljm.eWriteName(handle, "DIO_EF_CLOCK0_ENABLE", 0)  # Disable clock source
        # Set Clock0's divisor and roll value to configure frequency: 80MHz/1/80000 = 1kHz
        ljm.eWriteName(handle, "DIO_EF_CLOCK0_DIVISOR", clockDivisor)  # Configure Clock0's divisor
        # ljm.eWriteName(handle, "DIO_EF_CLOCK0_ROLL_VALUE", 80000)# Configure Clock0's roll value
        ljm.eWriteName(handle, "DIO_EF_CLOCK0_ROLL_VALUE", rollValue)  # Configure Clock0's roll value
        ljm.eWriteName(handle, "DIO_EF_CLOCK0_ENABLE", 1)  # Enable the clock source

        # Configure EF Channel Registers for signal:
        ljm.eWriteName(handle, "DIO" + str(pin) + "_EF_ENABLE", 0)  # Disable the EF system for initial configuration
        ljm.eWriteName(handle, "DIO" + str(pin) + "_EF_INDEX", 0)  # Configure EF system for PWM
        ljm.eWriteName(handle, "DIO" + str(pin) + "_EF_OPTIONS", 0)  # Configure what clock source to use: Clock0
        ljm.eWriteName(handle, "DIO" + str(pin) + "_EF_CONFIG_A", dutyConfig)  # Configure duty cycle to be: 50%
        ljm.eWriteName(handle, "DIO" + str(pin) + "_EF_ENABLE", 1)  # Enable the EF system, PWM wave is now being outputted

    else:
        print("IO Input Pin Not Valid *(T7 LabJack DIO 0, 2-5 ONLY)")


'''
Generates a specific number of pulse outputs for motor movement. 
Assumes direction and enable are pre-configured
Frequency calculation based on desired RPM and configured microstep
Outputs on user-defined pin
Assumes a low to high transition at 0, and computes high to low based on duty cycle
Input duty cycle expressed as decimal (not percent)
'''
def goStep(pin, steps, RPM, duty):
    # Check output pin valid
    if pin == 0 or pin in range(2, 6):
        # Set up math
        clock = 80E6
        clockDivisor = 1
        lowToHigh = 0

        freq = RPM /((1/microstep)*60)
        rollValue = (clock / clockDivisor) / freq
        dutyConfig = rollValue * duty
        clockFreq = clock/clockDivisor
        highToLow = duty*clockFreq + lowToHigh
        lowToHigh = 0

        # Enable clock
        ljm.eWriteName(handle, "DIO_EF_CLOCK0_DIVISOR", clockDivisor)
        ljm.eWriteName(handle, "DIO_EF_CLOCK0_ROLL_VALUE", rollValue)
        ljm.eWriteName(handle, "DIO_EF_CLOCK0_ENABLE", 1)

        # Configure pulse
        ljm.eWriteName(handle, "DIO" + str(pin) + "_EF_ENABLE", 0)
        ljm.eWriteName(handle, "DIO" + str(pin), 0)
        ljm.eWriteName(handle, "DIO" + str(pin) + "_EF_INDEX", 2)
        ljm.eWriteName(handle, "DIO" + str(pin) + "_EF_CONFIG_A", highToLow)
        ljm.eWriteName(handle, "DIO" + str(pin) + "_EF_CONFIG_B", lowToHigh)
        ljm.eWriteName(handle, "DIO" + str(pin) + "_EF_CONFIG_A", highToLow)
        ljm.eWriteName(handle, "DIO" + str(pin) + "_EF_CONFIG_C", steps)
        ljm.eWriteName(handle, "DIO" + str(pin) + "_EF_ENABLE", 1)

        # Print statement for debug
        print("Output Pin: " + str(pin))
        print("Total Steps Out: " + str(steps))
        print("Motor RPM: " + str(RPM))
        print("PWM Frequency: " + str(freq))
        print("PWM Duty Cycle: " + str(duty * 100))
        print("")

    else:
        print("IO Input Pin Not Valid *(T7 LabJack DIO 0, 2-5 ONLY)")


# Test the functionality
#time.sleep(10)
#ljm.eWriteName(handle, "DAC0", 5)
# generateDefaultPWM()
# time.sleep(10)
# ljm.eWriteName(handle, motorEnable, 0)
# runCheckRun()
# ljm.eWriteName(handle, motorEnable, 5)
goStep(0, 5000, 1000, .1)