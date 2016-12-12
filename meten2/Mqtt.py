from Standard import Standard
import time

class meet(Standard):
    def on_start(self):
        pass
    def on_connect(self,client, userdata, flags, rc):
        client.subscribe("hack42/#")
    def on_message(self,client, userdata, msg):
        self.timelast=time.time()
        self.addline(msg.topic+": "+msg.payload)
