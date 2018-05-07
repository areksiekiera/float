import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
chan_list = [17,22,27]
GPIO.setup(chan_list, GPIO.OUT)

class SSRelay:

	chan = None
	state = GPIO.LOW

	def __init__(self, chan=None):
		if not chan:
			raise ValueError("'chan' param required - channel number")
		self.chan = chan

		# set initial state
		self.set_output(self.state)

	def set_output(self, state):
		self.state = state
		# print("outputing {} on channel {}".format(self.state, self.chan))
		GPIO.output(self.chan, self.state) 



