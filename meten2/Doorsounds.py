from Standard import Standard
import os
import time

class meet(Standard):
    def on_start(self):
        pass
    def on_connect(self,client, userdata, flags, rc):
        client.subscribe("hack42/sidedoor/monitor/doorsw")
        client.subscribe("hack42/sidedoor/access")
        client.subscribe("hack42/sidedoor/doorbell")
        client.subscribe("hack42/brandhok/nooddeur1")
        client.subscribe("hack42/brandhok/nooddeur2")
    def on_message(self,client, userdata, msg):
        self.timelast=time.time()
        self.addline("Mendel "+msg.topic+" "+msg.payload)
        if msg.payload=="open" and msg.topic=="hack42/sidedoor/monitor/doorsw":
           os.system("mplayer -ao alsa /root/kassa/sounds/intel_inside.mp3 >/dev/null 2>/dev/null")
        if msg.topic=="hack42/sidedoor/doorbell":
           os.system("mplayer -ao alsa /root/kassa/sounds/doorbell.mp3 >/dev/null 2>/dev/null")
        if msg.topic=="hack42/sidedoor/access":
           os.system("mplayer -ao alsa /root/kassa/sounds/icq.mp3 >/dev/null 2>/dev/null")
        if msg.payload=="open" and msg.topic=="hack42/brandhok/nooddeur1":
           os.system("mplayer -ao alsa /root/kassa/sounds/firealarm.mp3 >/dev/null 2>/dev/null")
        if msg.payload=="open" and msg.topic=="hack42/brandhok/nooddeur2":
           os.system("mplayer -ao alsa /root/kassa/sounds/firealarm.mp3 >/dev/null 2>/dev/null")
