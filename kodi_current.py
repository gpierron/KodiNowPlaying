#!/usr/bin/env python

# author (alterer is a more suitable word) : Guillaume Pierron - "Guiwiz"
#
# This script is largely based on the work of Arnaud Bertrand - "Arn-O"
# You can find his original work (a wonderful python script to control XBMC) here :
# https://github.com/Arn-O/py-xbmc-remote-controller
#
# This script is also based on the work (a python script for xchat/hexchat to control
# the linux player amarok locally) of zir0faive, not publically available yet :) 

__module_name__ = "Kodi NowPlaying"
__module_version__ = "0.89c"
__module_description__ = "A dirty/quickly adapted script to print currently playing music on distant Kodi"

print "\003",__module_name__, __module_version__,"has been loaded\003"

import xchat
import socket
import json
from string import Template

BUFFER_SIZE = 1024

''' USERS SHOULD MODIFY THIS SECTION '''
XBMC_IP = "192.168.1.210"
XBMC_PORT = 9090


''' USERS MAY MODIFY THIS TOO '''
COMPATIBLE_ENCODING = 'iso-8859-1'
SCRIPTCMD = 'zik'

'''STRING FORMATTING PREFS PART'''
TITLE = 'Kodi '
DISPLAY_PATTERN = TITLE + '15# $artist 15- $title ' + \
		  '15(#$track 15- $album 15- $year15) ' + \
		  '15[$p_min15:$p_0sec15/$t_min15:$t_0sec ' + \
		  '15,15$elapsed14,14$remaining15]' 

BAR_LENGTH = 10
CHAR_ELAPSED = '#'
CHAR_REMAINING = '='

def now_playing(item, properties):
    if item:
        #constructing initial data
        full_data = {}
        full_data.update(item)
        full_data.update(properties)
       
        # retrieving first artist field only
        if item['artist']:
            full_data['artist'] = item['artist'][0]

        # computing progress bar and time values
        n = int(BAR_LENGTH * properties['percentage'] / 100)
        full_data['elapsed'] = CHAR_ELAPSED * n
        full_data['remaining'] = CHAR_REMAINING * (BAR_LENGTH - n)
        full_data['p_min'] = properties['time']['hours'] * 60 + \
                             properties['time']['minutes'] 
        full_data['p_0sec'] = "%02d" % properties['time']['seconds']
        full_data['t_min'] = properties['totaltime']['hours'] * 60 + \
                             properties['totaltime']['minutes'] 
        full_data['t_0sec'] = "%02d" % properties['totaltime']['seconds']
        

        str_ret = Template(DISPLAY_PATTERN).substitute(full_data)
      
    else:
        str_ret= "[is not playing anything]"
    return str_ret

def get_item(ip, port):
    command = {"jsonrpc": "2.0",
            "method": "Player.GetItem",
            "params": {
                "playerid": 0,
                "properties": [
                    "album",
                    "title",
                    "track",
                    "artist",
                    "year",
                    "genre" ] },
            "id": 1}
    ret = call_api(ip, port, command)
    item = None
    try:
        item = ret['result']['item']
    except KeyError:
        pass
    return item

def get_properties(ip, port):
    command = {"jsonrpc": "2.0",
            "method": "Player.GetProperties",
            "params": {
                "playerid": 0,
                "properties": [
                    "time",
                    "totaltime",
                    "percentage",
                    "position"] },
            "id": 1}
    ret = call_api(ip, port, command)
    result = None
    try:
        result = ret['result']
    except KeyError:
        pass
    return result

def call_api(ip, port, command):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    s.send(json.dumps(command))
    data = ''
    while True:
        filler = s.recv(BUFFER_SIZE)
        data += filler
        nb_open_brackets = data.count('{') - data.count('}')
        if nb_open_brackets == 0:
            break
    s.close()
    ret = json.loads(data)
    return ret


def play_what():
    item = get_item(XBMC_IP, XBMC_PORT)
    properties = get_properties(XBMC_IP, XBMC_PORT)
    return now_playing(item, properties)

def xchat_kodi_cmd(argv, arg_to_eol, c):
    if len(argv) == 1:
        current=play_what()
        xchat.command('me %s' % current.encode(COMPATIBLE_ENCODING))
    return xchat.EAT_ALL

xchat.hook_command(SCRIPTCMD, xchat_kodi_cmd, help="/"+SCRIPTCMD)
