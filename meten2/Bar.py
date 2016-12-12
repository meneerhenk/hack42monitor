#!/usr/bin/python
# -*- coding: utf-8 -*-

from threading import Timer
from Standard import Standard

class meet(Standard):
    name="bar"
    roms={}
    correctie1w={
    }


    def on_start(self):
       self.request("1")
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


    def runline(self,line):
       if line.startswith("1: "):
          if line.startswith("1: ROM"):
              s=line.split(" ")
              if len(s)>6:
                  self.update_mqtt_temp(s[3],s[6]);
                  self.roms[s[3]]=float(s[6])
       if line.startswith("R: Reboot"):
           self.on_start()
       if line.startswith("D: "):
          s=line.split(" ")
          if len(s)>6:
              self.publish("hack42/"+self.name+"/humidity",str(int(float(s[6])))+" %")
       if line.startswith("I: "):
          s=line.split(" ")
          if len(s)>5 and s[1]=="state":
              self.publish("hack42/"+self.name+"/input"+s[4],("open" if s[5]=="1" else "closed" ))
       if line.startswith("C: "):
          s=line.split(" ")
          if len(s)>3 and s[1]=="Port":
             self.publish("hack42/"+self.name+"/port"+s[2],s[3])


