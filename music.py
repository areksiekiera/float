import os

class Music:

	def play(self, name):

		if name == 'ok':
			os.system('mpg321 /home/pi/sound/ok.mp3 &')
		elif name == 'invalid':
			os.system('mpg321 /home/pi/sound/invalid.mp3 &')
		elif name == 'music':
			os.system('mpg321 /home/pi/sound/10.mp3 &')
		else:
			raise ValueError("make sure you pass correct file name")
