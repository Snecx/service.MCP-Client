# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import xbmcaddon
import sys
import socket
import json

__addon__               = xbmcaddon.Addon()
__addon_id__            = __addon__.getAddonInfo('id')
__addonname__           = __addon__.getAddonInfo('name')
__icon__                = __addon__.getAddonInfo('icon')
__addonpath__           = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')
__settings__            = xbmcaddon.Addon(id="service.MCP-Client")

serviceForScript = 'script.MCP-Client'

class ConnectionCheck(xbmc.Monitor):
    isconnected = False
    count = 0
    isdebug = False
    pingtime = 10
    
    
    def Msg(self,message):
       xbmcgui.Dialog().notification("MCP-Client", message, __icon__, 2000)
       
    def onNotification(self,sender, method, data):
        player = self.GetSystemName()
        pre = '{"jsonrpc":"' + player + '","method":"' + method + '","params":{"data":' + data + ',"sender":"xbmc"}}'
        try:
           s.sendall(pre + "\r\n\r\n")
           #xbmc.log("MCP-Client: " + str(pre), level=xbmc.LOGNOTICE)
        except socket.error as msg:
           if self.isdebug == True:
             xbmc.log("MCP-Client:  Send eror code: " + str(msg), level=xbmc.LOGNOTICE)
           self.Msg("Send JSON failed!")
        
    def GetSystemName(self):
         json_response = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{"setting":"services.devicename"},"id":1}')
         parsed_json = json.loads(json_response)
         whichtype = parsed_json['result']['value']
         return str(whichtype)
         
    def GetSystemIP(self):
        json_response = xbmc.getInfoLabel("Network.IPAddress")
        return str(json_response)
        
    def __init__(self):
        xbmc.Monitor.__init__(self)
        self.pingtime = __settings__.getSetting("pingtime")
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(5) 
        #self.socketconn = False
        self.isdebug = __settings__.getSetting("debug")
        try:
           player2 = self.GetSystemName()
           host = __settings__.getSetting("serverip")
           port = __settings__.getSetting("serverport")
           s.connect((host , int(port)))
           self.isconnected = True
           s.sendall(" --(" + player2  + ")-- \r\n")
           
        except socket.error as msg:
           if self.isdebug == True:
             xbmc.log("MCP-Client:" + 'Failed to connect socket.: ' + str(msg) , level=xbmc.LOGNOTICE)
           self.Msg("Connect failed!")
           self.isconnected = False        
        
        while(not xbmc.abortRequested):
             xbmc.sleep(50)
             self.count += 1
             if self.count == int(self.pingtime)*20:
                self.count = 0
                if self.isconnected == False:
                    try:
                        if self.isdebug == True:
                           xbmc.log("MCP-Client:" + "Trying to reconnect...", level=xbmc.LOGNOTICE)
                        player2 = self.GetSystemName()
                        host = __settings__.getSetting("serverip")
                        port = __settings__.getSetting("serverport")
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((host , int(port)))
                        self.isconnected = True
                        #self.localsocket = sock
                        s.sendall(" --(" + player2  + ")-- \r\n")
                    except socket.error as msg:
                        if self.isdebug == True:
                          xbmc.log("MCP-Client:" + 'Failed to reconnect socket.: ' + str(msg), level=xbmc.LOGNOTICE)
                        self.Msg("Reconnect failed!")
                        self.isconnected = False
                else:
                    try:
                        s.sendall("PING\r\n")
                    except socket.error as msg:
                        if self.isdebug == True:
                          xbmc.log("MCP-Client:" + 'Failed to send PING: ' + str(msg), level=xbmc.LOGNOTICE)
                        self.isconnected = False
                        self.Msg("PING failed!")
                        #s.shutdown(2)
                        s.close
        #s.shutdown(2)
        s.close()


xbmc.log("MCP-Client: Start (ver:1.4)", level=xbmc.LOGNOTICE)
xbmc.sleep(1000)
xbmc.log("MCP-Client: Connection monitor start", level=xbmc.LOGNOTICE)
con = ConnectionCheck()
xbmc.log("MCP-Client: Connection monitor stop", level=xbmc.LOGNOTICE)


