#!/usr/bin/python
# -*- coding: utf-8 -*-

from threading import Timer
from Standard import Standard

class meet(Standard):
    name="stookhok"
    roms={}
    correctie1w={
      '28EE50131D1602A1': 1.15,
      '28EEF00C1D160230': 1.15,
      '28EEC8151D160221': 1.15,
      '28EE5E241D1602CD': 1.15,
      '28EE49E31F1601F2': 1.15,
      '28EE6917201601F4': 1.15,
      '28EED917201601BB': 1.15,
      '28EEF51720160162': 1.15,
      '28EEC30E1D1602FD': 1.15,
      '28EE4FF01C1602D8': 1.15,
    }


    def on_start(self):
        pass

    def docalc(self):
       if '28AF7293050000D4' in self.roms and '28FFFB3617140038' in self.roms:
          if float(self.roms['28AF7293050000D4'])>43.0:
              powercalc=(self.roms['28AF7293050000D4']-self.roms['28FFFB3617140038'])  * 7  * 1000 * 4.2 / 1000
              if powercalc > 1000 or powercalc < 0: powercalc=0
              powercalc=round(powercalc,1)
          else:
              powercalc=0.0
          self.publish("hack42/"+self.name+"/power",str(powercalc)+" kW")

       stornum=0
       stored=0
       for x in ['28EE5E241D1602CD','28EEF00C1D160230','28EE50131D1602A1','28EE4FF01C1602D8','28EED917201601BB','28EE6917201601F4','28EEC30E1D1602FD','28EEF51720160162','28EEC8151D160221','28EE49E31F1601F2'] :
           if x in self.roms and round(float(self.roms[x]),1)!=85.0 and round(float(self.roms[x]),1)>30:
               stornum+=1
               stored+=(float(self.roms['28EE50131D1602A1'])-30)*1.164*5
       if stornum>0: self.publish("hack42/"+self.name+"/buffervat",str(round(stored/stornum,1))+" kWh")
       if '28AF7293050000D4' in self.roms and '28FFFB3617140038' in self.roms:
          kacheluit = float(self.roms['28AF7293050000D4'])
          kachelin  = float(self.roms['28FFFB3617140038'])
          if kachelin - 2 > kacheluit or kacheluit < 43:
             self.publish('hack42/stookhok/kachelpomp','off')
          elif kacheluit+2 > kachelin and kacheluit > 42:
             self.publish('hack42/stookhok/kachelpomp','on')

    def runinputoutput(self,line):
       if line.startswith("I: "):
          s=line.split(" ")
          if len(s)>5 and s[1]=="state":
              self.publish("hack42/"+self.name+"/input"+s[4],("open" if s[5]=="1" else "closed" ))
       if line.startswith("C: "):
          s=line.split(" ")
          if len(s)>3 and s[1]=="Port":
             self.publish("hack42/"+self.name+"/port"+s[2],s[3])
       if line.startswith("D: "):
          s=line.split(" ")
          if len(s)>6:
              self.publish("hack42/"+self.name+"/humidity",str(int(float(s[6])))+" %")


    def runline(self,line):
       if line.startswith("1: "):
          if line.startswith("1: ROM"):
              s=line.split(" ")
              if len(s)>6:
                  self.update_mqtt_temp(s[3],s[6]);
                  self.roms[s[3]]=float(s[6])
                  self.docalc()
       if line.startswith("R: Reboot"):
           self.on_start()
       self.runinputoutput(line)
