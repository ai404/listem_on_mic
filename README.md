Python Mic Listener
==================

![alt text](https://img.shields.io/badge/python-3.6-green.svg "Python3.6")

This script is executed in background and listen for noises around. Once the noise reaches a given limit, the script takes a screenshot and sends it via email.

Dependecies:
-------------
* Pyaudio

```pip install pyaudio```

* Or alternatively

```pip install -r requirements.txt```

How to start:
-------------

* Set your Gmail Account's email and password
* Set Sender and Recipient emails
* execute the app. You ll see some numbers. make some noise and watch those numbers change. choose the perfect number for you (default is '''NOISE_MIN = 0.2''')
* (Tune some other options if you like)
* run this script on background $ pythonw listen_on_mic.py

Compatibility
-------------

Compatible with Python 3.x ,tested  on Python 3.6.
