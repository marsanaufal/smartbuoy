from time import sleep
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def setServoAngle(servo, angle):
	pwm = GPIO.PWM(servo, 50)
	pwm.start(0)
	dutyCycle = angle /25.7  + 2.5
	pwm.ChangeDutyCycle(dutyCycle)
	sleep(0.5)
	pwm.stop()

if __name__ == '__main__':
	import sys
	servo = int(sys.argv[1])
	GPIO.setup(servo, GPIO.OUT)
	setServoAngle(servo, int(sys.argv[2]))
	GPIO.cleanup()