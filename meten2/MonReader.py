#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import sys
import os
import serial
import shutil
import paho.mqtt.client as paho
import logging

from glob import glob
from math import sqrt

class MonReader:
    stopping=0
    last={}
    lastsave=0
    caching=0
    lastmsg={}

    def __init__(self,port,rrdpath,speed,lines):
         self.ser = serial.Serial(
             port=port,
             baudrate=speed,
             parity=serial.PARITY_NONE,
             stopbits=serial.STOPBITS_ONE,
             bytesize=serial.EIGHTBITS,
         )
         self.rrdpath=rrdpath
         self.client = client = paho.Client()
         self.client.on_connect = self.on_connect
         logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-13s) %(message)s',)
         self.lines=lines
    def addline(self,line):
        self.lines.append(line[0:100])
        if len(self.lines)>25: self.lines.pop(0)
    def docache(self,tmppath,caching):
        self.tmppath=tmppath
        self.caching=caching

    def on_connect(self, client, userdata, flags, rc):
        self.addline("Connected with result code "+str(rc))
    
    def quit(self):
        self.stopping=1

    def cache_files_startup(self):
        os.chdir(self.rrdpath)
        if not os.path.isdir(self.tmppath):
           os.mkdir(self.tmppath)
        for file in glob("*.rrd"):
           if not os.path.isfile(self.tmppath+"/"+file):
              print "Niet daar",file
              shutil.copy2(self.rrdpath+"/"+file,self.tmppath+"/"+file)
           elif os.path.getmtime(self.tmppath+"/"+file) < os.path.getmtime(self.rrdpath+"/"+file):
              print "Nieuwer in static storage",file
              shutil.copy2(self.rrdpath+"/"+file,self.tmppath+"/"+file)
              
    def cache_to_storage(self):
       if self.lastsave+1800<time.time():
          os.chdir(self.tmppath)
          for file in glob("*.rrd"):
              if not os.path.isfile(self.rrdpath+"/"+file):
                  print "Saved",file
                  shutil.copy2(self.tmppath+"/"+file,self.rrdpath+"/"+file)
              elif os.path.getmtime(self.tmppath+"/"+file) > os.path.getmtime(self.rrdpath+"/"+file):
                  print "Nieuwer in temp",file
                  shutil.copy2(self.tmppath+"/"+file,self.rrdpath+"/"+file)
          self.lastsave=time.time()
        

    def start(self):
         self.client.connect("192.168.142.66", 1883, 60)
         self.client.loop_start()
         if self.caching:
             self.cache_files_startup()
             os.chdir(self.tmppath)
         else:
             os.chdir(self.rrdpath)
         while not self.stopping:
           if self.caching:
               self.cache_to_storage()
           line=self.ser.readline().strip()
           try:
              self.runline(line)
           except:
              import traceback
              print traceback.format_exc()
              time.sleep(5)
              pass

    def publish(self,path,msg):
        if path in self.lastmsg:
           if self.lastmsg[path]!=msg:
               self.client.publish(path,msg,0,True)
               self.lastmsg[path]=msg
        else:
               self.client.publish(path,msg,0,True)
               self.lastmsg[path]=msg

    def runline(self,line):
      logging.debug("No handler runline defined")

class KachelReader(MonReader):
    def update_mqtt_kachel(self,output,input,retour,lounge,outside,valve):
        output=str(float(output)/10)
        input=str(float(input)/10)
        retour=str(float(retour)/10)
        lounge=str(float(lounge)/10)
        outside=str(float(outside)/10)
        self.publish("hack42/sensors/analog/output",output+" "+u"\u00B0"+"C")
        self.publish("hack42/sensors/analog/input",input+" "+u"\u00B0"+"C")
        self.publish("hack42/sensors/analog/retour",retour+" "+u"\u00B0"+"C")
        self.publish("hack42/sensors/analog/lounge",lounge+" "+u"\u00B0"+"C")
        self.publish("hack42/sensors/analog/outside",outside+" "+u"\u00B0"+"C")
        self.publish("hack42/sensors/analog/valve",valve+" "+"steps")

    def runline(self,line):
       if len(line)>0:
         if line.startswith("ROM = "):
            print "  "
         print line
       if line.startswith("Sensors "):
          parts=line.split(" ");
          if 'Sensors' in parts and len(parts)>=10:
              s0=str(int(parts[1]))
              s1=str(int(parts[2]))
              s2=str(int(parts[3]))
              s3=str(int(parts[4]))
              s4=str(int(parts[5]))
              s5=str(int(parts[6]))
              s6=str(int(parts[7]))
              s7=str(int(parts[8]))
              valve=str(int(parts[9]))
              step=str(int(parts[10]))
              os.system("rrdtool update temp2.rrd N:"+s0+":"+s1+":"+s2+":"+s3+":"+s4+":0:0:0:"+valve)
              if 'kachel' in self.last:
                  if self.last['kachel']+10<time.time():
                      self.last['kachel']=time.time()
                      self.update_mqtt_kachel(s0,s1,s2,s3,s4,valve)
              else:
                  self.last['kachel']=time.time()
                  self.update_mqtt_kachel(s0,s1,s2,s3,s4,valve)

class AmpReader(MonReader):
    def update_mqtt_amp(self,a1,a2,a3):
        a1=sqrt(float(int(a1,16))/1024)*0.25525664*140
        a2=sqrt(float(int(a2,16))/1024)*0.25525664*140
        a3=sqrt(float(int(a3,16))/1024)*0.25525664*140
        self.publish("hack42/power/3phase","L1: "+str(round(a1))+" L2: "+str(round(a2))+" L3: "+str(round(a3))+" Total: "+str(round(a1+a2+a3))+" Watt")
    
    def runline(self,line):
       if len(line)>0:
         print line
       if line.startswith("CA: "):
          parts=line.replace("\t"," ").split(" ");
          print parts
          if 'ST:' in parts and len(parts)>=15:
              print parts[parts.index("ST:"):]
              a1=parts[parts.index("ST:")+1]
              a2=parts[parts.index("ST:")+2]
              a3=parts[parts.index("ST:")+3]
              a4=parts[parts.index("ST:")+5]
              a5=parts[parts.index("ST:")+6]
              a6=parts[parts.index("ST:")+7]
              os.system("rrdtool update powerR.rrd N:"+a1+":"+a2+":"+a3+":"+a4+":"+a5+":"+a6)
              if 'amp' in self.last:
                  if self.last['amp']+10<time.time():
                      self.last['amp']=time.time()
                      self.update_mqtt_amp(a1,a2,a3)
              else:
                  self.last['amp']=time.time()
                  self.update_mqtt_amp(a1,a2,a3)


class OneWireReader(MonReader):
    timelast=0

    def update_mqtt(self,rom,temp):
        msg=str(round(float(temp),1))+" "+u"\u00B0"+"C";
        self.publish("hack42/sensors/1wire/"+rom,msg)

    def update_mqtt_power(self,power):                                                
        msg=power+" Watt";
        self.publish("hack42/power/usage",msg)
               
        
    def runline(self,line):
       self.timelast=time.time()
       if len(line)>0:
         self.addline(line)
       if line.startswith("ROM = "):
          parts=line.split(" ");
          if 'ROM' in parts and 'Temperature' in parts:
             temp = parts.index('Temperature')+2
             rom  = parts.index('ROM')+2 
             if os.path.isfile(parts[rom]+'.rrd'):
                 os.system("rrdtool update "+parts[rom]+'.rrd N:'+parts[temp])
             if parts[rom] in self.last:
                if self.last[parts[rom]]+10<time.time():
                    self.last[parts[rom]]=time.time()
                    self.update_mqtt(parts[rom],parts[temp])
             else:
                self.last[parts[rom]]=time.time()
                self.update_mqtt(parts[rom],parts[temp])
       if line.startswith("Sensors "):
          parts=line.split(" ");
          if 'Sensors' in parts and len(parts)>2:
              power=parts[2]
              os.system("rrdtool update power2.rrd N:"+power)
              if 'power' in self.last:
                  if self.last['power']+20<time.time():
                      self.last['power']=time.time()
                      self.update_mqtt_power(power)
              else:
                  self.last['power']=time.time()
                  self.update_mqtt_power(power)

class UPSReader(MonReader):
    def __init__(self,rrdpath):
         self.rrdpath=rrdpath
         self.client = client = paho.Client()
         self.client.on_connect = self.on_connect

    def update_mqtt_ups(self,obj):
        self.publish("hack42/power/ups/3cavia/linevoltage",obj['LINEV']+" V")
        self.publish("hack42/power/ups/3cavia/loadpercentage",obj['LOADPCT']+" %")
        self.publish("hack42/power/ups/3cavia/batterycharge",obj['BCHARGE']+" %")
        self.publish("hack42/power/ups/3cavia/timeleft",obj['TIMELEFT']+" minutes")
        self.publish("hack42/power/ups/3cavia/maxlinevoltage",obj['MAXLINEV']+" V")
        self.publish("hack42/power/ups/3cavia/minlinevoltage",obj['MINLINEV']+" V")
        self.publish("hack42/power/ups/3cavia/outputvoltage",obj['OUTPUTV']+" V")
        self.publish("hack42/power/ups/3cavia/internaltemperature",obj['ITEMP']+" "+u"\u00B0"+"C")
        self.publish("hack42/power/ups/3cavia/batteryvoltage",obj['BATTV']+" V")
        self.publish("hack42/power/ups/3cavia/linefreq",obj['LINEFREQ']+" Hz")

    def runline(self):
         import subprocess
         APCACCESS   = "/usr/sbin/apcaccess"
         keywords = ['LINEV','LOADPCT','BCHARGE','TIMELEFT','MAXLINEV','MINLINEV','OUTPUTV','ITEMP','BATTV','LINEFREQ']
         res = subprocess.check_output(APCACCESS) 
         obj={}
         for line in res.split('\n') :
             (key,spl,val) = line.partition(': ')
             key = key.rstrip()
             val = val.strip()
             val = val.split(' ',1)[0]
             if key in keywords :
                 obj[key]=val
         self.update_mqtt_ups(obj)
         time.sleep(30)
    def start(self):
         self.client.connect("192.168.42.66", 1883, 60)
         self.client.loop_start()
         if self.caching:
             self.cache_files_startup()
             os.chdir(self.tmppath)
         else:
             os.chdir(self.rrdpath)
         while not self.stopping:
           if self.caching:
               self.cache_to_storage()
           try:
              self.runline()
           except:
              import traceback
              print traceback.format_exc()
              time.sleep(5)
              pass
