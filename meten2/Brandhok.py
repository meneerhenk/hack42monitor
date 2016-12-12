#!/usr/bin/python
# -*- coding: utf-8 -*-

from Standard import Standard
from threading import Timer
import time

class meet(Standard):
    roms={}
    name="brandhok"
    names={'1': "nooddeur1", '7': "nooddeur2", '3': "nooddeur3", '4': "achterdeur", "5": "zijdeur", "6": "deuropen", "2": "door1b", "8": "none"}
    debug=0
    def on_start(self):
      pass
    def runline(self,line):
       self.addline(line)
       if line.startswith("I: "):
          s=line.split(" ")
          if len(s)>5 and s[1]=="state":
              self.publish("hack42/"+self.name+"/"+self.names[s[4]],("open" if s[5]=="1" else "closed" ))
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

