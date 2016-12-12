#!/usr/bin/python
# -*- coding: utf-8 -*-

from Standard import Standard
from threading import Timer
import time

class meet(Standard):
    roms={}
    name="brandhok"
    names={'1': "nooddeur1", '7': "nooddeur2", '3': "nooddeur3", '4': "achterdeur", "5": "zijdeur", "6": "deuropen", "2": "door1b", "8": "none"}
    debug=0
