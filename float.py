from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import sys
import cv2
import zbar
import Image
import time
import requests
from datetime import datetime

from music import Music
from ssrelay import SSRelay

import logging

DEBUG = False
RESOLUTION = (640, 480)

FULLSCREEN = not DEBUG

RELAY_FILTER = 22
RELAY_SHOWER = 27

# Initialise OpenCV window
if FULLSCREEN:
    cv2.namedWindow("floathanoi", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("floathanoi", cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)
else:
    cv2.namedWindow("floathanoi")

class FloatRoom:

    state = None # 0 busy / 1 ready to scan 
    camera = None
    rawCapture = None
    scanner = None
    music = None
    r_shower = None
    r_filter = None


    def __init__(self):
        # set in ready state 
        logging.basicConfig(filename='/tmp/float.log',level=logging.INFO)
        self.state = 1
        self.camera = PiCamera()
        self.camera.resolution = RESOLUTION
        self.rawCapture = PiRGBArray(self.camera, size=RESOLUTION)

        logging.info("{} PiCamera ready".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        self.r_shower = SSRelay(RELAY_SHOWER)
        self.r_filter = SSRelay(RELAY_FILTER)

        self.r_shower.set_output(0)
        self.r_filter.set_output(0)
        logging.info("{} Relays initial off".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        

        self.music = Music()

        time.sleep(0.1)

        self.scanner = zbar.ImageScanner()
        self.scanner.parse_config('enable')

        

    def start(self):
         # Capture frames from the camera
        logging.info("{} Scanner active".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
            
            # as raw NumPy array
            output = frame.array.copy()
            
            # raw detection code
            gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY, dstCn=0)
            pil = Image.fromarray(gray)
            width, height = pil.size
            raw = pil.tobytes()

            # create a reader
            image = zbar.Image(width, height, 'Y800', raw)
            self.scanner.scan(image)

            # extract results
            for symbol in image:
                logging.info("{} Decoded {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol.data))

                if self.redeem(symbol.data):
                    self.start_session(symbol.data)
                else:
                    self.code_invalid(symbol.data)



            # show the frame
            cv2.imshow("floathanoi", output)
            
            # clear stream for next frame
            self.rawCapture.truncate(0)


            # Wait for the magic key
            keypress = cv2.waitKey(1) & 0xFF
            if keypress == ord('q'):
                break

    def redeem(self, code):
        r = requests.get('http://127.0.0.1/tickets/redeem?c={}'.format(code))
        return bool(r.json())

    def start_session(self, code):

        try:
            duration = code.split('#')[2]
            logging.info("{} Start session, duration: {}min".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), duration))

        except:
            logging.info("{} Code decoding error: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), code))
            duration = 60
            logging.info("{} Start session, duration: {}min".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), code))
            
        self.music.play('music')
        
        # shower on
        logging.info("{} Shower on for 5min".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.r_shower.set_output(1)
        # keep it on for 5 min
        time.sleep(300)
        
        # shower off
        self.r_shower.set_output(0)
        
        # wait for float duration  sec
        logging.info("{} Float on for {}min".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), duration))
        time.sleep(int(duration) * 60)

        # shower back on
        logging.info("{} End session, shower on".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))            )
        self.r_shower.set_output(1)
        
        # music back on
        self.music.play('ok')
        time.sleep(3)
        self.music.play('ok')
        time.sleep(3)
        self.music.play('ok')
        
        time.sleep(30)
        
        self.music.play('ok')
        time.sleep(3)
        self.music.play('ok')
        time.sleep(3)
        self.music.play('ok')        

        # wait 30 sec before filter on
        time.sleep(30)
        logging.info("{} End session, filters on".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.r_filter.set_output(1)
        # wait 10min before show and filter off  
        time.sleep(600)
        
        self.r_shower.set_output(0)
        self.r_filter.set_output(0)
        logging.info("{} End session, shower and filters off".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def code_invalid(self, code):
        self.music.play('invalid')
        time.sleep(5)
        logging.info("{} Code invalid {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), code))


room = FloatRoom()
room.start()

