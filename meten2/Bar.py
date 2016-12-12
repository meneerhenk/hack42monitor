#!/usr/bin/python
# -*- coding: utf-8 -*-

from threading import Timer
from Standard import Standard

class meet(Standard):
    name="bar"
    roms={}

    def on_connect(self,client, userdata, flags, rc):
        client.subscribe("hack42/state")

    def on_message(self,client, userdata, msg):
        if msg.payload=="open" and msg.topic=="hack42/state":
            self.request("O1C")
            self.request("O2C")
            self.request("O3C")
        if msg.payload=="closed" and msg.topic=="hack42/state":
            self.request("O1O")
            self.request("O2O")
            self.request("O3O")
