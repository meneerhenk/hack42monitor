from Standard import Standard
import os
from threading import Timer
import time
import socket
import json
from pprint import pprint
import logging

class meet(Standard):
    aps={'192.168.8.35': "Museum" ,'192.168.8.36': "Maaklab",'192.168.8.37': "Flexlab" ,'192.168.8.38': "Office",'192.168.8.39': "Lounge"}
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
           self.runwifi()
    def runwifi(self):
        clients=[]
        apclients={}
        realclients={}
        for ap in self.aps:
          apclients[ap]=0
          try:
            newdata=""
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ap,668))
            while 1:
                data=sock.recv(2048)
                newdata+=data
                if data=="": break;
            try:
                for client in json.loads('['+newdata.rstrip()+']'):
                    apclients[ap]+=1
                    clients.append(client)
            except:
                self.addline("Level 2")
                self.addline( newdata)
                return
            sock.close()
          except:
            pass
        for client in clients:
           if client['mac']  not in realclients or realclients[client['mac']]<int(client['inactive time'].split(" ")[0]):
               realclients[client['mac']]=int(client['inactive time'].split(" ")[0])
        self.publish("hack42/wlan/clientcount",str(len(realclients)))
        self.addline("Wlan clients: "+str(len(realclients)))
        for ap in apclients:
          self.publish("hack42/wlan/"+self.aps[ap]+"/clientcount",str(apclients[ap]))
          self.addline("Wlan" + self.aps[ap] + "clients: "+str(apclients[ap]))
        self.timelast=time.time()
        time.sleep(5)
