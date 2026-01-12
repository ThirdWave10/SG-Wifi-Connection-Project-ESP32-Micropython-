# Snake Industries Global
# ESP32 Wi-Fi initialisation module
#
# copyright infringement enforced with death by 10_000 paper cuts.

import os
import json
import network
import time
import sys
from machine import unique_id, reset
from ubinascii import hexlify
import socket
import gc



station = network.WLAN(network.STA_IF)
station.active(True)
settings_path = "settings.json"
time_dur = time.time() + 20
startup_time = time.time()



urlencodedchars = {
    "%21": "!",  
    "%22": "\"",
    "%23": "#",
    "%24": "$",
    "%25": "%",
    "%26": "&",
    "%27": "'",
    "%28": "(",
    "%29": ")",
    "%2A": "*",
    "%2B": "+",
    "%2C": ",",
    "%2D": "-",
    "%2E": ".",
    "%2F": "/",
    "%3A": ":",
    "%3B": ";",
    "%3C": "<",
    "%3D": "=",
    "%3E": ">",
    "%3F": "?",
    "%40": "@",
    "%5B": "[",
    "%5D": "]",
    "%5E": "^",
    "%5F": "_",
    "%60": "`",
    "%7B": "{",
    "%7D": "}",
    "%7C": "|",
    "%7E": "~"
}
            


def getHWUID():
    # collect the uniquie hardware ID
    hwid = unique_id()
    # convert binary string into hex and decode to ASCII
    hwid = hexlify(hwid).decode('utf-8')
    # update hwid to just be last 4 digits of ID string
    hwid = hwid[-4:]
    return hwid


def startWAP():
    ''' Initalise network WiFi interface and setup to operate in Access Point mode'''
    global wap
    ip = '###########'
    mask = '#########'
    gw = '##########'
    dns = '######'
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    wap = network.WLAN(network.AP_IF)
    print(f'Activating WAP interface')
    wap.active(True)
    wapssid = 'snake-' + ip + '_' + getHWUID()
    print(f'Configuring WAP interface')
    wap.config(ssid=wapssid, channel=11)
    while wap.active() == False:
        print(f'.')
        sleep(0.5)
    print(f'WiFi Access Point Established')
    print(f'Setting WiFi Access Point IP Details')
    wap.ifconfig((ip,mask,'',dns))
    print(f'WiFi Access Point IP Details Configured - Access via http://{ip}')


def wifisectype(x):
    ''' convert wifi.scan() network security type into readable string'''
    ''' 0 – open, 1 – WEP, 2 – WPA-PSK, 3 – WPA2-PSK, 4 – WPA/WPA2-PSK'''
    if x == 0:
        sectype = 'Open'
    elif x == 1:
        sectype = 'WEP'
    elif x == 2:
        sectype = 'WPA-PSK'
    elif x == 3:
        sectype = 'WPA2-PSK'
    else:
        sectype = 'WPA/WPA2-PSK'
    return sectype


def initWIFIscan():
    ''' Perform scan of WiFi environment and return the list of networks and assoicated information'''
    global rawSSIDlist
    rawSSIDlist = wap.scan()
    #print(rawSSIDlist)
    print(f'\nIdentified broadcasting SSID''s\n')
    for x in rawSSIDlist:
        print('SSID: {}\t Channel: {}\t Signal: {}\t Security: {}'.format(x[0].decode('utf-8'), x[2], x[3], wifisectype(x[4])))


def webgenssidlist():
    htmlcode = "<HTML><HEAD><TITLE>Web Setup Interface</TITLE></HEAD><BODY>"
    htmlcode = htmlcode + "<CENTRE><H1>Snake Tech - Web WiFi Setup Interface</H1></CENTRE>"
    htmlcode = htmlcode + "<BR><BR>"
    htmlcode = htmlcode + '''<h3>Select SSID to connect to an enter required password</h3>
    <FORM action="/wifisetup/" method="post" accept-charset="utf-8">
    <table>
    '''
    for x in rawSSIDlist:
        htmlcode = htmlcode + '<tr><td><input type="radio" name="ssid" value="{}"></td><td>SSID: {}</td><td>Channel: {}</td><td>Signal: {}</td><td>Security: {}</td></tr>'.format(x[0].decode('utf-8'), x[0].decode('utf-8'), x[2], x[3], wifisectype(x[4]))

    htmlcode = htmlcode + '''
    <tr></tr><tr><td></td><td><label for="pwd">SSID Password:</label><br>
    <input type="password" id="pwd" name="pwd"><br><br>
    <input type="submit" value="Submit"><input type="reset" value="Reset"></td></tr>
    </table></body></html>
    '''
    
    return htmlcode


def wifi_settings_save(ssid, ssidpw):
   
    settings_path = "settings.json"     # I suggest you put this at the top of your code but it doesnt matter too much
    network_info = {"SSID" : ssid, "SSIDPW" : ssidpw}  # Make the ssid and ssidpw the users input
   
    with open (settings_path, "w") as file:
        json.dump(network_info, file)  


def readhttppost(string):
    ''' Function to read in the http header string and extract the HTTP POST data into key:value pairs and return a dictionary ''' 
    string = string.decode('utf-8')
    postpos=string.rfind('\r\n')
    #print(f'DATA: {postpos}')
    postdata=string[postpos+2:]
    #print(f'POST DATA: {postdata}')
    postnum=postdata.count('&')+1
    #print(f'Number of fields posted: {postnum}')
    postdict={}
    postslice=postdata
    for x in range(postnum):
        f = postslice.find('&')
        if f != -1:
            #print(f'\nLoop: {x} F: {f}')
            data = postslice[0:f]
            #print(f'DATA: {data}')
            postslice = postslice[f+1:]
            #print(f'POSTSLICE: {postslice}')
            datasep = data.find('=')
            postkey = data[0:datasep]
            postvalue = data[datasep+1:]
            print(f'KEY: {postkey} VALUE: {postvalue}')
            postdict[postkey] = postvalue
        
        else:
            #print(f'\nLoop: {x} F: {f}')
            data = postslice
            #print(f'DATA: {data}')
            datasep = data.find('=')
            postkey = data[0:datasep]
            postvalue = data[datasep+1:]
            print(f'KEY: {postkey} VALUE: {postvalue}')
            postdict[postkey] = postvalue

            
    for key, value in postdict.items():
        for encoded, character in urlencodedchars.items():
            if encoded in value:
                print (f"found encoded value in {value} which was {encoded} or {character}")
                value = value.replace(encoded,character)
                postdict[key] = value


    return(postdict)


def webhandler(srv):
    print('Handler starting')
    cs,ca = srv.accept()
    print('Serving:', ca)
    request = cs.recv(1024)
    reqdata = request
    request = request.decode('utf-8')
    #print('\n\nRequest: {}\n\n'.format(request))
    reqval=request.find('HTTP/')
    req=request[4:reqval-1]
    #req=req.decode('utf-8')
    print(f'Req string: {req}')
    cs.setblocking(False)
    if '/wifisetup/' in req:
        postdict = readhttppost(reqdata)
        print(postdict)
        #set a blank htmlerror string variable for later use
        htmlerror = ""
        try:
            wifi_settings_save(postdict['ssid'], postdict['pwd'])
            cs.write('HTTP/1.1 200 OK\n')
            cs.write('Content-Type: text/html\n')
            cs.write('Connection: close\n\n')
            cs.write(f'<HTML><HEAD><TITLE>Data page</TITLE></HEAD><BODY><CENTER><h1>DATA UPDATED</H1></CENTER></BODY></HTML>')
            cs.close()
            print("New SSID information saved. Restarting device.")
            time.sleep(2)
            reset() 
        except KeyError:
            print(f'Submitted data error')
            cs.write('HTTP/1.1 200 OK\n')
            cs.write('Content-Type: text/html\n')
            cs.write('Connection: close\n\n')
            cs.write(f'<HTML><HEAD><TITLE>Data page</TITLE></HEAD><BODY><CENTER><h1>DATA UPDATED</H1><BR><BR><CENTRE><H2 COLOR=RED> WARNING: DATA SUBMITTION ERROR. TRY AGAIN</H2><BR><A HREF=''/''> RETURN TO SETTINGS PAGE AND TRY AGAIN</A></CENTRE></BODY></HTML>')
            cs.close()
    else:
        cs.write('HTTP/1.1 200 OK\n')
        cs.write('Content-Type: text/html\n')
        cs.write('Connection: close\n\n')
        cs.write(f'{webgenssidlist()}')
        cs.close()
 


def initWIFIweb():
    global srv  
    port = 80
    addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
    
    if 'srv' in globals() and srv.fileno() != -1:  # Check if socket is in globals and if so close the socket
        print("Closing existing server socket...")
        srv.close()

    try:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
        srv.bind(addr)
        srv.listen(5)
        print("Server is listening...")
    except Exception as e:
        print(f"Error during listen: {e}")
        return 

    srv.setblocking(False)
    srv.setsockopt(socket.SOL_SOCKET, 20, webhandler)
    
    
def initWIFIsetup():
    print(f'Main function starts here\n\n')
    print(f'Hardware ID: {getHWUID()}')
    startWAP()
    initWIFIscan()
    initWIFIweb()


def wifi_settings_load():
    
    if settings_path in os.listdir():
        with open (settings_path, "r") as file:
            contents = json.load(file)
            return contents
        
    else:
        initWIFIsetup()        
    
    
def start_wifi():
    settings_data = wifi_settings_load()
    
    for x in range(3):
            
            try:
                print(f"Attempt {x + 1} to connect to {settings_data['SSID']}...")
                
            except:
                print(f"Attempt {x + 1} to connect to wifi")
            
            if station.isconnected():
                station.disconnect()
                time.sleep(1)
            
            try: 
                station.connect(settings_data["SSID"],settings_data["SSIDPW"])
                time.sleep(2)
            except Exception as e:
                print(f"connection failed: {e}") 
                continue
            
            if station.isconnected():
                print("connection successful!")
                print(f"Connection info: {station.ifconfig()[0]}")
                return
            
            while not station.isconnected() and time.time() < time_dur:
                time.sleep(0.1)
                
    print("Failed to connect after 3 attempts. Starting AP")
    station.disconnect()             
    initWIFIsetup()

  
  
  
# MAIN CODE

if __name__ == '__main__':
    print(f'Executing as a stand alone script')
    start_wifi()




