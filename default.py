# -*- coding: utf-8 -*-

import xbmc
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
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.settimeout(5) 
socketconn = False

class ConnectionCheck(xbmc.Monitor):
    isconnected = False
    count = 0
    localsock = False
    

    def onNotification(self,sender, method, data):
        player = self.GetSystemName()
        pre = '{"jsonrpc":"' + player + '","method":"' + method + '","params":{"data":' + data + ',"sender":"xbmc"}}'
        self.SendOverSocket(pre,self.localsock)
        
    def SendOverSocket(self,inpu,qw):
         try:
           qw.sendall(inpu + "\r\n\r\n")
         except socket.error, msg:
           xbmc.log("MCP-Client:  Send eror code: " + str(msg), level=xbmc.LOGNOTICE)
           
    def GetSystemName(self):
         json_response = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{"setting":"services.devicename"},"id":1}')
         parsed_json = json.loads(json_response)
         whichtype = parsed_json['result']['value']
         return str(whichtype)
         
    def GetSystemIP(self):
        json_response = xbmc.getInfoLabel("Network.IPAddress")
        return str(json_response)
        
    def __init__(self,sock):
        xbmc.Monitor.__init__(self)
        self.localsock = sock
        try:
           player2 = self.GetSystemName()
           host = lastintro = __settings__.getSetting("serverip")
           port = __settings__.getSetting("serverport")
           sock.connect((host , int(port)))
           self.isconnected = True
           sock.sendall(" --(" + player2  + ")-- \r\n")
        except socket.error, msg:
           xbmc.log("MCP-Client:" + 'Failed to create socket.: ' + str(msg) , level=xbmc.LOGNOTICE)
           isconnected = False        
        
        while(not xbmc.abortRequested):
             xbmc.sleep(50)
             self.count += 1
             if self.count == 200:
                self.count = 0
                if self.isconnected == False:
                    try:
                        xbmc.log("MCP-Client:" + "Trying to reconnect...", level=xbmc.LOGNOTICE)
                        player2 = self.GetSystemName()
                        host = __settings__.getSetting("serverip")
                        port = __settings__.getSetting("serverport")
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((host , int(port)))
                        self.isconnected = True
                        sock.sendall(" --(" + player2  + ")-- \r\n")
                    except socket.error, msg:
                        xbmc.log("MCP-Client:" + 'Failed to create socket.: ' + str(msg), level=xbmc.LOGNOTICE)
                        self.isconnected = False
                else:
                    try:
                        sock.sendall("PING\r\n")
                    except socket.error, msg:
                        xbmc.log("MCP-Client:" + 'Failed to send PING: ' + str(msg), level=xbmc.LOGNOTICE)
                        self.isconnected = False
                        sock.shutdown(2)
                        sock.close



xbmc.log("MCP-Client: Start", level=xbmc.LOGNOTICE)
xbmc.log("MCP-Client: 1.1", level=xbmc.LOGNOTICE)
xbmc.sleep(1000)
xbmc.log("MCP-Client: Connection monitor start", level=xbmc.LOGNOTICE)
con = ConnectionCheck(s)
xbmc.log("MCP-Client: Connection monitor stop", level=xbmc.LOGNOTICE)
s.close()
xbmc.log("MCP-Client: Start", level=xbmc.LOGNOTICE)
