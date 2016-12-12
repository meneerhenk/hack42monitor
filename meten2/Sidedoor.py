#!/usr/bin/python
# -*- coding: utf-8 -*-

from Standard import Standard
from doorduino import doorduino
from hashlib import sha1
from random import randint
from struct import unpack,pack
import time
import re

class meet(doorduino):
    name="sidedoor"
    MAX_FAILURES = 10
    guest_enable=True # Allow a list of unencrypted buttons named 'guests.acl' if the space is open
