#!/usr/bin/python
RRDPATH="/root/rrds/"
import curses
import time
import importlib
import threading

def startports():
  startport("Stookhok","05",RRDPATH,19200)
  startport("Stookkelder","14",RRDPATH,19200)
  startport("Bar","13",RRDPATH,19200)
  startport("Brandhok","11",RRDPATH,19200)
  startport("Wifi",None,RRDPATH,None)
  startport("Kassasounds",None,RRDPATH,None)
  startport("Doorsounds",None,RRDPATH,None)
  startport("Mqtt",None,RRDPATH,None)
  startport("Onewire","OW",RRDPATH,9600)
  startport("Sidedoor","01","/root/software",19200)
  startport("1Door","18","/root/software",38400)


myobjs={}
mythreads={}
names={}
def startport(mod,port,RRDPATH,speed):
  global myobjs,mythreads,enableports,lines,line,lastseen
  pi=len(enableports)
  enableports.append(pi)
  lines[pi]=[]
  lines[pi].append("Hello")
  line[pi]=""
  lastseen[pi]=0
  if mod=="Onewire":
      mymod=importlib.import_module("meten2.MonReader")
      myobjs[pi]=mymod.OneWireReader(None if port==None else "/dev/monitor/P"+port,RRDPATH,speed,lines[pi])
  else:
      mymod=importlib.import_module("meten2."+mod)
      myobjs[pi]=mymod.meet(None if port==None else "/dev/monitor/P"+port,RRDPATH,speed,lines[pi])
  mythreads[pi]=threading.Thread(name=mod,target=myobjs[pi].start).start()
  names[pi]=mod

def paintports():
  global stat,ports,names,screen
  (y,x)=screen.getmaxyx()
  stat.resize(8,x)
  stat.erase();
  stat.box();
  nextline=0
  prevstart=0
  for i in enableports:
    width=len(names[i])+4;
    if(3+prevstart+width)>(x-2):
      prevstart=0
      nextline=1
    ports[i] = stat.subwin( 3 , width, 1+nextline*3, 1+prevstart)
    prevstart+=width+1
    ports[i].box()
    ports[i].addstr(1,1,' '+names[i])
    ports[i].addstr(0,1,' '+chr(ord('a')+i)+' ')
  stat.refresh()

def signal_handler(signal, frame):
    curses.endwin()
    for x in myobjs:
       myobjs[x].stopping=1
    sys.exit(0)

screen = curses.initscr()
curses.noecho()
curses.cbreak()
curses.start_color()
screen.keypad( 1 )    # delete this line
curses.init_pair(1,curses.COLOR_WHITE, curses.COLOR_BLUE)
curses.init_pair(2,curses.COLOR_BLACK, curses.COLOR_GREEN)
curses.init_pair(3,curses.COLOR_BLACK, curses.COLOR_RED)
curses.init_pair(4,curses.COLOR_YELLOW, curses.COLOR_BLUE)
curses.init_pair(5,curses.COLOR_BLACK, curses.COLOR_YELLOW)
highlightText = curses.color_pair( 1 )
normalText = curses.color_pair(1)
#screen.border( 0 )
curses.curs_set( 0 )
stat = curses.newwin( 8, 120, 0, 0 )
stat.bkgd(curses.color_pair(4))
stat.box()

linex=0
liney=0
def resizeoutp():
    global screen,linex,liney
    (y,x)=screen.getmaxyx()
    linex=x-2
    liney=y-2-8
    outp.resize(y-8,x)
    outp.box()
    outp.refresh()
    
outp = curses.newwin( 0, 2, 8, 0 )
outp.bkgd(curses.color_pair(4))
outp.keypad( 1 )
outp.box()
resizeoutp()

enableports=[]
lastseen={}
ports={}
lines={}
line={}
prevactiveport=-1
activeport=0

screen.refresh()    # delete this line
stat.refresh()
outp.refresh()
outp.nodelay(1)

x=0

def setactiveport():
  global prevactiveport,activeport,enableports
  for i in enableports:
    if i!=activeport:
      status=None
      if myobjs[i].timelast>time.time()-60:
        status=True
      ports[i].bkgd( curses.color_pair(2) if status else curses.color_pair(3))
      #if i in enableports and lastseen[i]+60<time.time():
      #  ports[activeport].bkgd( curses.color_pair(3))
      ports[i].refresh()
  ports[activeport].bkgd( curses.color_pair(5))
  ports[activeport].refresh()

startports()
paintports()

olines=None
ofline=None
try:
  while x != 27:
    setactiveport()
    if lines[activeport]!=olines:
        outp.erase();
        outp.box()
        olines=lines[activeport]
    else:
      if len(lines[activeport]) > 0 and ofline!=lines[activeport][-1]:
        outp.erase();
        outp.box()
        ofline=lines[activeport][-1]
    ln=0
    for myline in lines[activeport][-liney:]:
      ln+=1
      if line==liney: break;
      try:
          outp.addstr( ln,1, myline[:linex],curses.color_pair(1) )
      except:
          pass
    ln+=1
    try:
        outp.addstr( ln,1, line[activeport],curses.color_pair(1) )
    except:
        pass
    outp.refresh()     # delete this line
    x = outp.getch()
    if x>=ord('a') and x<ord('a')+24 and x-ord('a') in enableports:
      activeport=x-ord('a')
    elif x==12:
      resizeoutp()
      paintports()
      screen.touchwin()
      screen.refresh()
    elif x<127 and x>0:
      if myobjs[activeport].ser:
        myobjs[activeport].ser.write(chr(x))
    elif x==curses.KEY_RESIZE:
      resizeoutp()
      paintports()
    time.sleep(0.2)
except:
    curses.endwin()
    for x in myobjs:
       myobjs[x].stopping=1
    import traceback
    print traceback.format_exc()
try:
    curses.endwin()
except:
    pass
exit()
