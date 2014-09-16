#!/usr/bin/env python

# author (alterer is a more suitable word) : Guillaume Pierron - "Guiwiz"
# This script is largely based on the work of Arnaud Bertrand - "Arn-O"
# You can find his original work (a wonderful python script to control XBMC) here :
# https://github.com/Arn-O/py-xbmc-remote-controller



__module_name__ = "Kodi NowPlaying"
__module_version__ = "0.84b"
__module_description__ = "A dirty/quickly adapted script to print currently playing music on distant Kodi"

print "\003",__module_name__, __module_version__,"has been loaded\003"

import xchat
import socket
import json

''' USERS SHOULD MODIFY THIS SECTION '''
XBMC_IP = "192.168.1.210"
XBMC_PORT = 9090


BUFFER_SIZE = 1024

def now_playing(item, properties):
    if item:
        disp_prog = ['.','.','.','.','.','.','.','.','.','.']
        progression=(int(properties['percentage']/10))
        for i in range(progression):
            disp_prog[i]='*'
       
        str_ret= "Kodi :::: [ %s - %s | %s - %s ] [ %s | %02d:%02d:%02d / %02d:%02d:%02d ] ::::"  % (
            item['artist'][0], item['title'],
            item['year'], item['album'],
            ''.join(disp_prog),  
            properties['time']['hours'],
            properties['time']['minutes'],
            properties['time']['seconds'],
            properties['totaltime']['hours'],
            properties['totaltime']['minutes'],
            properties['totaltime']['seconds'])
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
                    "artist",
                    "year",
                    "rating" ] },
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
                    "position" ] },
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
        xchat.command('me %s' % current.encode('iso-8859-1'))

xchat.hook_command("zik", xchat_kodi_cmd, help="/zik")

