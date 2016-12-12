#!/usr/bin/python
# -*- coding: utf-8 -*-

from doorduino import doorduino
from threading import Timer
import os

class meet(doorduino):
    name="1door"
    MAX_FAILURES = 10
    guest_enable=True # Allow a list of unencrypted buttons named 'guests.acl' if the space is open
    spacestate=""
    def on_start(self):
        self.ser.write("R")
    def closedoor(self):
      if self.spacestate!="open":
          self.request("S")

    def on_connect(self,client, userdata, flags, rc):
        client.subscribe("hack42/state")
    def on_message(self,client, userdata, msg):
        self.addline("Mendel "+msg.topic+" "+msg.payload)
        if msg.payload=="open" and msg.topic=="hack42/state":
           self.ser.write("O")
           self.ser.write("P")
           os.system("./twitter open")
        if msg.payload=="closed" and msg.topic=="hack42/state":
           Timer(5, self.closedoor, ()).start()
           self.ser.write("Z")
           os.system("./twitter closed")

