'''
QDPPMS Comms

Interface between Python and QDMonitor

Usage:

from QDPPMSComms.QDPPMSComms import QDPPMS
qd = QDPPMS('host',port) default localhost and port 3333

'''


import socket
import time
import select


class QDPPMS(object):
    STATUSTEMP = 1
    STATUSFIELD = 2

    TEMP_FASTSETTLE=0
    TEMP_NOOVERSHOOT=1

    FIELD_LINEAR=0
    FIELD_NOOVERSHOOT=1
    FIELD_OSCILLATE=2

    FIELD_PERSIST=0
    FIELD_DRIVEN=1


    def __init__(self, ip='localhost', port=3333):
        self.sock = socket.socket()
        self.ip = ip
        self.port = port
        self._connect()


    def __del__(self):
        self._close()

    # Connect to QDMonitor
    def _connect(self):
        try:
            self.sock.connect((self.ip, self.port))
            #self.sock.setblocking(0)
            ready = select.select([self.sock], [], [], 5)
            if ready[0]:
                resp = self.sock.recv(5000).decode()
            else:
                resp = "Timeout has occurred!"

            print(f"Handshake from QDMonitor in {self.ip}:{self.port} is {resp}")
        except socket.error:
            print(f"Ops: Could not connect to QD Monitor {self.ip} {self.port}")

    def _close(self):
        print("Closing connection to QDMonitor bye bye")
        self.sock.close()

    def _writeLog(self,line):
        t = time.localtime()
        f = open("qdppms_log.txt","a")
        f.write(time.strftime('%d/%m/%Y %H:%M:%S')+':'+line+'\r\n')
        f.close()
        print(line)

    def _sendandread(self,cmd):
        #self._writeLog(f"Socket send {cmd}")
        cmd=cmd+"\r\n"
        self.sock.send(cmd.encode())
        time.sleep(0.5)

        ready=select.select([self.sock],[],[],10)
        if ready[0]:
            resp=self.sock.recv(5000).decode()
        else:
            resp="1\r\nTimeout has occurred!"

        #self._writeLog(f"Socket receive {resp}")
        return resp.splitlines()

    def getTemperature(self):
        resp=self._sendandread("gpibsendread getdat? 8388610") #temperature and map23
        try:
            data=resp[1].split(',')
            self._writeLog(f"getTemprature {data}")

            if data[0]=='8388610': #map23 present
                return [float(data[2]),float(data[3])]
            else:
                return [float(data[2]),0]
        except:
            return[float("nan"),float("nan")]

    def getField(self):
        resp=self._sendandread("gpibsendread getdat? 4") #get field
        try:
            data=resp[1].split(',')
            self._writeLog(f"getField {data}")

            return float(data[2])
        except:
            return float("nan")


    def status(self,type):
        resp=self._sendandread('gpibsendread getdat? 1') #get status
        try:
            data=resp[1].split(',')

            if type==self.STATUSTEMP:
                temp_status = int(data[2]) & 0xF
                #self._writeLog(f'Temp status is {temp_status}')
                return temp_status

            if type==self.STATUSFIELD:
                field_status = int((int(data[2]) & 0xF0) / 16)
                #self._writeLog(f'Field status is {field_status}')
                return field_status
        except Exception as e:
            self._writeLog(f"status check crashed for type {type} {e.args}!")
            return -1

    def waitForStable(self, type, extra=0, timeout=3600):
        self._writeLog(f'waitForStable {type},{timeout},{extra}')
        elapsed=0
        time.sleep(1) #Wait 1 second to have time to update at ramp start
        status=self.status(type) #First check

        if type==self.STATUSTEMP: #Condition for stability status=1
            while status!=1 and elapsed<timeout:
                status = self.status(type)  #Is temp stable?
                time.sleep(1)
                elapsed += 1

        if type==self.STATUSFIELD: #Condition for stability status=1 or 4
            while status!=1 and status!=4 and elapsed<timeout:
                status = self.status(type)  #Is field stable?
                time.sleep(1)
                elapsed += 1

        if elapsed>=timeout:
            self._writeLog("Warning! Stability not achieved!")
        else:
            self._writeLog(f"Stable! It took {elapsed} seconds")

        #We want extra time after stability
        if extra>0:
            self._writeLog(f"Wait for more {extra} seconds")
            time.sleep(extra)
            self._writeLog("Done!")

    def setField(self,setpoint,ramp,approach,endmode):
        self._writeLog(f'setField {setpoint},{ramp},{approach},{endmode}')
        resp=self._sendandread(f'setfield {setpoint},{ramp},{approach},{endmode}')
        expire=0
        while (self.status(self.STATUSFIELD)==1 or self.status(self.STATUSFIELD)==4) and expire<30 :
            time.sleep(1)
            expire += 1

        return resp

    def setTemperature(self, setpoint, ramp, approach):
        self._writeLog(f'setTemperature {setpoint},{ramp},{approach}')
        resp=self._sendandread(f'settemp {setpoint},{ramp},{approach}')
        expire=0
        while self.status(self.STATUSTEMP) == 1 and expire<30:
            time.sleep(1)
            expire += 1

        return resp