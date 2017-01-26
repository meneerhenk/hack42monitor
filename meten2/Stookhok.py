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
      '28EE95151D160258': 1.15,
      '28EEDB18201601A2': 1.15,
      '28EED7FA1C16024A': 1.15,
      '28EEBEE11F160102': 1.15,
      '28EE95041D1602EF': 1.15,
    }

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
               stored+=(float(self.roms[x])-30)*1.164*0.5
       if stornum>0: self.publish("hack42/"+self.name+"/buffervat",str(round(stored,1))+" kWh")
       if '28AF7293050000D4' in self.roms and '28FFFB3617140038' in self.roms:
          kacheluit = float(self.roms['28AF7293050000D4'])
          kachelin  = float(self.roms['28FFFB3617140038'])
          if kachelin - 2 > kacheluit or kacheluit < 43:
             self.publish('hack42/stookhok/kachelpomp','off')
          elif kacheluit+2 > kachelin and kacheluit > 42:
             self.publish('hack42/stookhok/kachelpomp','on')
