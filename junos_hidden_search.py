#!/usr/bin/python3

HOST = "192.168.65.198"
user = "lab"
password = "lab123"
commandStart = "show version "     # Must have space at the end!

import telnetlib
import re

alphabet = "abcdefghijklmnopqrstuvwxyz-1234567890."
PAUSE = 3 

def SearchCommands(cmd, on_hidden_now = False):
    for char in alphabet:
        tn.write(cmd.encode('ascii') + char.encode('ascii') + b"\n")
        totData=""
        finished = False
        while not finished:
            inpData = tn.read_until(prompt.encode('ascii'), PAUSE)
            totData = totData + inpData.decode('ascii')
            if "---(more" in inpData.decode('ascii'): 
                tn.write(b" ")
            else:
                finished = True

        cmdNext = cmd + str(char)
        synt_error_exp_cmd = False
        synt_error_period = False
        if "syntax error, expecting <command>." in totData:
            synt_error_exp_cmd = True
        if "syntax error." in totData:
            synt_error_period = True
        
        if not (synt_error_exp_cmd or synt_error_period):  # normal output or ambiguity
            if on_hidden_now:
                print("hidden command >> " + cmdNext)
            else:
                SearchCommands(cmdNext, on_hidden_now) # i.e. False
        else:
            l = re.findall(' *\^', totData)
            lenToHat = len(l[len(l)-1])            
            if synt_error_period:                         
                if lenToHat > lenPrompt + len(cmdNext):
                    SearchCommands(cmdNext, True)        # Hidden command in progress
            if synt_error_exp_cmd:
                if lenToHat == 2 + lenPrompt + len(cmdNext):
                    if on_hidden_now:
                        print("hidden command >> " + cmdNext + "  (incomplete)")
                    # else: print("Entering: " + cmdNext)
                    SearchCommands(cmdNext+" ", on_hidden_now)
                if lenToHat > 2 + lenPrompt + len(cmdNext):  
                    SearchCommands(cmdNext, on_hidden_now)                            

tn = telnetlib.Telnet(HOST)
tn.read_until(b"login: ")
tn.write(user.encode('ascii') + b"\n")
tn.read_until(b"Password:")
tn.write(password.encode('ascii') + b"\n")

loginText = tn.read_until(b"> ").decode('ascii')
prompt = re.search(".*@.*", loginText).group()
print("Working with prompt = " + prompt)
lenPrompt = len(prompt)
SearchCommands(commandStart)
