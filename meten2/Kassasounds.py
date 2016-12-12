from Standard import Standard
from threading import Timer
import time
import os
import subprocess

class meet(Standard):
    def start(self):
         self.client.connect("192.168.42.151", 1883, 60)
         self.client.on_message = self.on_message
         self.client.loop_start()
         if self.caching:
             self.cache_files_startup()
             os.chdir(self.tmppath)
         else:
             os.chdir(self.rrdpath)
         while not self.stopping:
           if self.caching:
               self.cache_to_storage()
           self.timelast=time.time()
           time.sleep(0.5)
    def on_connect(self,client, userdata, flags, rc):
        client.subscribe("hack42bar/output/session/main/sound")
        client.subscribe("hack42bar/output/session/main/vol")
    def on_message(self,client, userdata, msg):
        if msg.topic=="hack42bar/output/session/main/sound":
            os.path.isfile("/root/kassa/sounds/"+msg.payload)
            os.system("mplayer -ao alsa /root/kassa/sounds/"+msg.payload+">/dev/null 2>/dev/null")
        if msg.topic=="hack42bar/output/session/main/vol":
            os.system("amixer sset Master 10%"+("+" if msg.payload=="up" else "-"))
