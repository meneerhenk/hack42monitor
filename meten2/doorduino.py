#!/usr/bin/python
# -*- coding: utf-8 -*-

from Standard import Standard
from hashlib import sha1
from random import randint
from struct import unpack,pack
from threading import Timer
import time
import re

class doorduino(Standard):
    MAX_FAILURES = 10

    buttons={}
    chalstring=None
    expected_response=None
    failures=0
    spacestate="closed"
    lastdoorbell=0

    def readacl(self):
        self.buttons={x.pop(0):x  for x in [re.split(" |:|\t",line.rstrip('\n')) for line in open('ibuttons/'+self.name+'.acl') if not line.startswith('#') and len(line)>1]}
        if self.guest_enable and self.spacestate=="open":
            self.buttons.update({x.pop(0):x  for x in [re.split(" |:|\t",line.rstrip('\n')) for line in open('ibuttons/guests.acl') if not line.startswith('#') and len(line)>1]})
            
    def on_start(self):
        pass

    def on_connect(self,client, userdata, flags, rc):
        client.subscribe("hack42/state")
        client.subscribe("hack42/brandhok/deuropen")

    def on_message(self,client, userdata, msg):
        if msg.topic=="hack42/state":
           self.spacestate=msg.payload
        if msg.topic=="hack42/brandhok/deuropen" and self.spacestate=="open" and msg.payload=="closed":
           self.access('knopje',"because it is pressed")


    def randomstring(self,mylen):
        return "".join(chr(randint(0,255)) for i in range(0,mylen))

    def ibutton_sha1(self,data):
        up=unpack(">IIIII",sha1("".join(data)).digest())
	H01=[0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0]
	return "".join((pack(">I", up[i]-H01[i] if up[i]-H01[i]>0 else (0xFFFFFFFF + up[i]-H01[i] + 1)  )  for i in range(0,5)))

    def read_mac(self,myid,secret,page,data,challenge):
        secret=secret.decode('hex')
        return self.ibutton_sha1( [ secret[0:4], data, "\xFF\xFF\xFF\xFF", chr(0x40+page), myid.decode('hex')[0:7], secret[4:8], challenge ])

    def write_mac(self,myid,secret,page,data,newdata):
        secret=secret.decode('hex')
        return self.ibutton_sha1( [ secret[0:4], data[0:28], newdata, chr(page), myid.decode('hex')[0:7], secret[4:8], "\xFF\xFF\xFF" ])

    def runresponse(self,data,mac):
         data=data.decode("hex")
         mac=mac.decode('hex')

         if not self.chalstring:
             self.noaccess(self.tocheck[1],'invalid response for extended challenge');
             return

         self.wanted=self.read_mac(self.btnid,self.buttons[self.btnid][0], self.page, data, self.chalstring)[::-1]
	 if self.wanted!=mac:
	     self.noaccess(self.tocheck[1],'invalid response for initial challenge');
             return

	 self.addline('Initiating extended challenge/response for %s' % str(self.btnid));

	 newdata = self.randomstring(8)
         offset = randint(0,4)*8
	 auth = self.write_mac(self.btnid,self.buttons[self.btnid][0],self.page,data,newdata)[::-1]
	 rechallenge = self.randomstring(3)
	 data = data[0:offset] + newdata + data[offset+8:]
         nm=self.read_mac(self.btnid,self.buttons[self.btnid][0],self.page,data,rechallenge)[::-1].encode("hex").upper()
         self.expected_response="<"+data.encode("hex").upper()+" "+nm+">"
	 self.ser.write("X" + chr(self.page) + rechallenge + chr(offset) + newdata + auth)

    def challenge(self):
         self.page=randint(0,4)
         self.chalstring=self.randomstring(3)
         self.ser.write("C"+chr(self.page)+self.chalstring)

    def checkbutton(self,button): 
       self.readacl()
       if button in self.buttons and len(self.buttons[button])==1:
           self.access(self.buttons[button][0],"without challenge/response")
       elif button in self.buttons and len(self.buttons[button])==2:
           self.btnid=button
           self.tocheck=self.buttons[button]
           self.challenge()
       else:
           self.noaccess('unknown',"because it is unlisted")

    def doorbell(self):
        if self.lastdoorbell+10<time.time():
            self.client.publish('hack42/'+self.name+'/doorbell','dingdong',0,False)
            self.lastdoorbell=time.time()
    def access(self,name,reason):
        self.ser.write("A")
        self.addline("Access granted for %s, %s" % (name,reason))
        self.client.publish('hack42/'+self.name+'/access',name,0,False)
        self.failure=0

    def noaccess(self,name,reason):
        self.ser.write("N")
        self.addline("Access denied for %s, %s" % (name,reason))
        self.failure=0

    def monitor(self,line):
        vals=line.split(",")
        spacevolt=str(round(float(vals[0].rstrip())*5.6*5/1024 *2,0)/2)
        bat1volt=str(round(float(vals[1].rstrip())*3.2*5/1024*2,0)/2)
        bat2volt=str(round(float(vals[2].rstrip())*3.2*5/1024*2,0)/2)
        doorsw=  "closed" if vals[3].rstrip()==" 0" else "open"
        locksw=  "open"   if vals[4].rstrip()==" 0" else "closed"
        handlesw="open"   if vals[5].rstrip()==" 0" else "closed"
        alarmsw= "open"   if vals[6].rstrip()==" 0" else "closed"
        self.publish("hack42/"+self.name+"/monitor/spacevolt",spacevolt+" V")
        self.publish("hack42/"+self.name+"/monitor/bat1volt",bat1volt+" V")
        self.publish("hack42/"+self.name+"/monitor/bat2volt",bat2volt+" V")
        self.publish("hack42/"+self.name+"/monitor/alarmsw",alarmsw)
        self.publish("hack42/"+self.name+"/monitor/locksw",locksw)
        self.publish("hack42/"+self.name+"/monitor/doorsw",doorsw)
        self.publish("hack42/"+self.name+"/monitor/handlesw",handlesw)
        self.addline("Spacevolt : %s %s %s" %(str(spacevolt),str(bat1volt),str(bat2volt)))
        self.addline("Monitor door: %s,lock: %s, handle: %s, alarm: %s" % (doorsw,locksw,handlesw,alarmsw))

    def runline(self,line):
        if line==self.expected_response:
	    self.access(self.name, "after extended challenge/response")
            return
        ka=re.match('<K>',line)
        cm=re.match('<([0-9A-Fa-f]{64}) ([0-9A-Fa-f]{40})>',line)
        dm=re.match('<BUTTON>',line)
        so=re.match('<SPACEOPEN>',line)
        sc=re.match('<SPACECLOSED>',line)
        do=re.match('<DOOROPEN>',line)
        dc=re.match('<DOORCLOSED>',line)
        bm=re.match('<(\w{16})>',line)
        sm=re.match('\[(.*)\]',line)
        self.last=time.time()
        if ka:
            self.last=time.time()
        elif cm:
            self.runresponse(cm.group(1),cm.group(2))
            self.last=time.time()
        elif dm:
            self.last=time.time()
            self.doorbell()
        elif bm:
            self.last=time.time()
            self.checkbutton(bm.group(1))
        elif sm:
            self.last=time.time()
            self.monitor(sm.group(1))
            self.ser.write("K")
        elif so:
            self.last=time.time()
            self.publish("hack42/state","open")
        elif sc:
            self.last=time.time()
            self.publish("hack42/state","closed")
        elif do:
            self.last=time.time()
            self.publish("hack42/"+self.name+"/door","open")
            Timer(5, self.request, (["R"])).start()
        elif dc:
            self.last=time.time()
            self.publish("hack42/"+self.name+"/door","closed")
            Timer(5, self.request, (["R"])).start()
        else:
            self.last=time.time()
            self.failures+=1
