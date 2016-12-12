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

class Standard:
    stopping=0
    last={}
    lastsave=0
    caching=0
    lastmsg={}
    name=""
    correctie1w={}
    names={}
    debug=1
    timelast=0

    def __init__(self,port,rrdpath,speed,lines):
         if port: self.ser = serial.Serial(
             port=port,
             baudrate=speed,
             parity=serial.PARITY_NONE,
             stopbits=serial.STOPBITS_ONE,
             bytesize=serial.EIGHTBITS,
         )
         if not port: self.ser=None
         logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-13s) %(message)s',)
         self.rrdpath=rrdpath
         self.client = client = paho.Client()
         self.client.on_connect = self.on_connect
         self.client.on_message = self.on_message
         if self.ser: self.ser.flush()
         self.lines=lines
    def addline(self,line):
        self.lines.append(line)
        if len(self.lines)>200: self.lines.pop(0)
    def docache(self,tmppath,caching):
        self.tmppath=tmppath
        self.caching=caching

    def on_connect(self, client, userdata, flags, rc):
        self.addline("Connected with result code "+str(rc))
        client.subscribe("hack42/"+self.name+"/input/#")

    def on_message(self,client, userdata, msg):
        self.addline("Input: "+msg.topic+" "+str(msg.payload))
        self.run_input(msg.topic,msg.payload)    
    
    def quit(self):
        self.stopping=1

    def cache_files_startup(self):
        os.chdir(self.rrdpath)
        if not os.path.isdir(self.tmppath):
           os.mkdir(self.tmppath)
        for file in glob("*.rrd"):
           if not os.path.isfile(self.tmppath+"/"+file):
              self.addline("Niet daar"+file)
              shutil.copy2(self.rrdpath+"/"+file,self.tmppath+"/"+file)
           elif os.path.getmtime(self.tmppath+"/"+file) < os.path.getmtime(self.rrdpath+"/"+file):
              self.addline("Nieuwer in static storage"+file)
              shutil.copy2(self.rrdpath+"/"+file,self.tmppath+"/"+file)
              
    def cache_to_storage(self):
       if self.lastsave+1800<time.time():
          os.chdir(self.tmppath)
          for file in glob("*.rrd"):
              if not os.path.isfile(self.rrdpath+"/"+file):
                  self.addline("Saved"+file)
                  shutil.copy2(self.tmppath+"/"+file,self.rrdpath+"/"+file)
              elif os.path.getmtime(self.tmppath+"/"+file) > os.path.getmtime(self.rrdpath+"/"+file):
                  self.addline("Nieuwer in temp"+file)
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
         try:
             self.on_start()
         except AttributeError:
             pass
         while not self.stopping:
           if self.caching:
               self.cache_to_storage()
           if self.ser:
               line=self.ser.readline().strip()
               self.timelast=time.time()
               try:
                  if self.debug:
                      self.addline(line)
                  self.runline(line)
               except:
                  import traceback
                  print traceback.format_exc()
           else:
                time.sleep(5)

    def publish(self,path,msg):
        if path in self.lastmsg:
           if self.lastmsg[path]!=msg:
               self.client.publish(path,msg,0,True)
               self.lastmsg[path]=msg
        else:
               self.client.publish(path,msg,0,True)
               self.lastmsg[path]=msg

    def runline(self,line):
        self.runinputoutput(line) 

    def update_mqtt_temp(self,rom,temp):
        if round(float(temp),1)==-127 or round(float(temp),1)==85: return
        temp=15 + (float(temp)-15) * ( self.correctie1w[rom] if rom in self.correctie1w else 1 )
        msg=str(round(float(temp) ,1))+" "+u"\u00B0"+"C";
        self.publish("hack42/sensors/1wire/"+rom,msg)

    def update_mqtt_power(self,power):
        msg=power+" Watt";
        self.publish("hack42/power/usage",msg)

    def update_mqtt_switch(self,rom,temp):
        msg=str(round(float(temp) * ( self.correctie1w[rom] if rom in self.correctie1w else 1 ) ,1))+" "+u"\u00B0"+"C";
        self.publish("hack42/sensors/1wire/"+rom,msg)

    def request(self,string):
       # TODO: reopen serial on error
       self.ser.write(string)

    def runinputoutput(self,line):
       if line.startswith("1: "):
          if line.startswith("1: ROM"):
              s=line.split(" ")
              if len(s)>6:
                  self.update_mqtt_temp(s[3],s[6]);
                  self.roms[s[3]]=float(s[6])
                  try:
                      self.docalc()
                  except AttributeError:
                      pass
       if line.startswith("R: Reboot"):
           try:
               self.on_start()
           except AttributeError:
               pass
       if line.startswith("I: "):
          s=line.split(" ")
          if len(s)>5 and s[1]=="state":
              self.publish("hack42/"+self.name+"/"+(self.names[s[4]] if s[4] in self.names else "input"+s[4]),("open" if s[5]=="1" else "closed" ))
       if line.startswith("C: "):
          s=line.split(" ")
          if len(s)>3 and s[1]=="Port":
             self.publish("hack42/"+self.name+"/port"+s[2],s[3])
       if line.startswith("D: "):
          s=line.split(" ")
          if len(s)>6:
              self.publish("hack42/"+self.name+"/humidity",str(int(float(s[6])))+" %")
