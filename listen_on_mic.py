from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

import pyaudio
import struct
import math
import os
import time
import smtplib

import datetime
import threading

# Change those params
FROM = 'YouGmail@gmail.com'
TO = 'ToGmail@outlook.com'

GMAIL_USERNAME = 'YouGmail@gmail.com'
GMAIL_PASSWORD = 'password'

# Tune this one
NOISE_MIN = 0.2

INITIAL_NOISE = 0.010
FORMAT = pyaudio.paInt16
SHORT_NORMALIZE = (1.0 / 32768.0)
CHANNELS = 2
RATE = 44100
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE * INPUT_BLOCK_TIME)


def get_rms(block):
    # RMS amplitude is defined as the square root of the 
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into 
    # a string of 16-bit samples...

    # we will get one short out for each 
    # two chars in the string.
    count = len(block) / 2
    format = "%dh" % (count)
    shorts = struct.unpack(format, block)

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n * n

    return math.sqrt(sum_squares / count)


class NOISETester(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.tap_threshold = INITIAL_NOISE
        self.msg_sent = None

    def stop(self):
        self.stream.close()

    def find_input_device(self):
        device_index = None
        for i in range(self.pa.get_device_count()):
            devinfo = self.pa.get_device_info_by_index(i)
            print("Device %d: %s" % (i, devinfo["name"]))

            for keyword in ["mic", "input"]:
                if keyword in devinfo["name"].lower():
                    print("Found an input: device %d - %s" % (i, devinfo["name"]))
                    device_index = i
                    return device_index

        if device_index == None:
            print("No preferred input found; using default input device.")

        return device_index

    def open_mic_stream(self):
        device_index = self.find_input_device()

        stream = self.pa.open(format=FORMAT,
                              channels=CHANNELS,
                              rate=RATE,
                              input=True,
                              input_device_index=device_index,
                              frames_per_buffer=INPUT_FRAMES_PER_BLOCK)

        return stream

    def send_email(self):
        print("NOISE!")

        msg = MIMEMultipart()

        fromaddr = FROM
        toaddrs = TO
        msg['Subject'] = 'screenshoot %s' % datetime.datetime.now()
        os.system("screencapture screen.png")
        fp = open("screen.png", 'rb')
        msg.attach(MIMEImage(fp.read(), _subtype="png"))
        fp.close()

        # Credentials (if needed)
        username = GMAIL_USERNAME
        password = GMAIL_PASSWORD

        # The actual mail send
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username, password)
        server.sendmail(fromaddr, toaddrs, msg.as_string())
        server.quit()

    def listen(self):
        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
            amplitude = get_rms(block)
            print(amplitude)
            if amplitude > NOISE_MIN:

                if self.msg_sent is None or time.time() - self.msg_sent > 5:
                    self.msg_sent = time.time()
                    try:
                        threading.Thread(target=self.send_email).start()
                        # self.send_email()
                        self.msg_sent = time.time()
                    except Exception as e:
                        print(e)
        except IOError as e:
            print(e)


if __name__ == "__main__":
    tt = NOISETester()

    while True:
        tt.listen()
