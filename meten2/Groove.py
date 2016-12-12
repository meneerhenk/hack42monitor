from Standard import Standard
from threading import Timer
import time
import os
import subprocess
import paho.mqtt.client as paho


class meet(Standard):
    player=None
    def start(self):
         self.client.connect("192.168.42.108", 1883, 60)
         self.client.loop_start()
         if self.caching:
             self.cache_files_startup()
             os.chdir(self.tmppath)
         else:
             os.chdir(self.rrdpath)
         while not self.stopping:
           if self.caching:
               self.cache_to_storage()
           time.sleep(0.5)
         self.client2 = paho.Client()
         self.client2.on_connect = self.on_connect2
         self.client2.on_message = self.on_message2
         self.client2.connect("localhost", 1883, 60)
         self.client2.loop_start()

    def on_connect2(self,client, userdata, flags, rc):
        client2.subscribe("hack42/state")

    def on_connect(self,client, userdata, flags, rc):
        client.subscribe("hack42bar/output/session/main/groove")

    def on_message2(self,client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
        if msg.topic=="hack42/state" and msg.payload=="closed":
          if self.player:
             if self.player.poll(): self.player.terminate()
             self.player=None

    def on_message(self,client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
        if msg.payload=="on" and self.player==None:
          self.player=subprocess.Popen(['mplayer','http://ice1.somafm.com/groovesalad-128-mp3'])
        elif player:
             if self.player.poll(): self.player.terminate()
             self.player=None
             
