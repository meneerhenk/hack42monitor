#!/usr/bin/python
# -*- coding: utf-8 -*-

from Standard import Standard
from threading import Timer

class meet(Standard):
    name="stookkelder"
    roms={}
    correctie1w={
      '28FF6B5A1714000D': 1.15,
      '28FFF6371714005B': 1.15,
      '28FF42C7161400D1': 1.15,
      '28FF4AE316140091': 1.15,
      '28FF3961171400C7': 1.15,
      '28FF5A741614008A': 1.15,
      '28FFE1C416140024': 1.15,
      '28FF4E5817140020': 1.15
    }

    def run_input(self,topic,payload):
       s=topic.split("/")
       if len(s)==4 and (s[3]=="O1" or s[3]=="O2" or s[3]=="O3" or s[3]=="O4"):
          if payload=="open":
              self.ser.write(s[3]+"O");
              Timer(5, self.request, ([s[3]+"C"])).start()
          elif payload=="close":
              self.ser.write(s[3]+"C");

    def on_start(self):
       self.request("O1C")
       self.request("O2C")
       self.request("O3C")
       self.request("O4C")

    def docalc(self):
       if '28FF6B5A1714000D' in self.roms and '28FF42C7161400D1' in self.roms:
          barin = float(self.roms['28FF6B5A1714000D'])
          bartoe = float(self.roms['28FF42C7161400D1'])
          if (bartoe-5) > barin:
             self.publish('hack42/stookkelder/barrakkenvalve','closed')
          elif bartoe>35 and bartoe-5<barin:
             self.publish('hack42/stookkelder/barrakkenvalve','open')
       if '28FF4AE316140091' in self.roms and '28FFE1C416140024' in self.roms:
          hoofdin = float(self.roms['28FF4AE316140091'])
          hoofdtoe = float(self.roms['28FFE1C416140024'])
          if (hoofdtoe-5) >hoofdin:
             self.publish('hack42/stookkelder/hoofdgebouwvalve','closed')
          elif hoofdtoe>35 and hoofdtoe-5<hoofdin:
             self.publish('hack42/stookkelder/hoofdgebouwvalve','open')
       if '28FF4AE316140091' in self.roms and '28FFE1C416140024' in self.roms and '28FF5A741614008A' in self.roms:
          hoofdin = float(self.roms['28FF4AE316140091'])
          hoofdtoe = float(self.roms['28FFE1C416140024'])
          hoofduit = float(self.roms['28FFE1C416140024'])
          if hoofdin>hoofdtoe+5 and hoofdin+5>hoofduit:
             self.publish('hack42/stookkelder/hoofdgebouwpomp','off')
          else:
             self.publish('hack42/stookkelder/hoofdgebouwpomp','on')
