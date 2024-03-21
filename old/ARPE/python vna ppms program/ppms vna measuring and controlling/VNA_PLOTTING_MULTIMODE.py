'''
- The text ";*OPC" is in the majority of the commands. It forces the Python program to stop until
    the command is executed and finished in the Vna device. However sometimes the Vna needs some
    extra time to execute the commands properly. So to avoid errors that can occur when a parameter is changed,
    a good option is to increase the closest "time.sleep()" before the error, or create a new one.


'''
import matplotlib.pyplot as plt
from drawnow import drawnow
import time
import pyvisa #to connect the python script to the vna
from QDPPMSComms.QDPPMSComms import QDPPMS #to command the ppms
qd = QDPPMS('pcd020e',3333)

#----------------VARIABLES-----------

freq1 = 7.9 #GHz (1st mode frequency)
ratio21=1.626 #freq2/freq1 measured at any temperature and field
ratio41= 1.714 #freq4/freq1 measured at any temperature and field


def multifreq():
    ref = ZNA.query('CALC:MARK:BWID?')
    fref = ref.split(',')
    return ratio21*float(fref[1]), ratio41*float(fref[1])

#finding the vna, or connecting with the vna
rm = pyvisa.ResourceManager()

print ('Device connected to the Laptop' + str(rm.list_resources()))
ZNA = rm.open_resource('TCPIP0::192.168.0.1::hislip0::INSTR')
print('Instrument Identification')
print (ZNA.query('*IDN?'))
time.sleep(0.5)

#restarting VNA
ZNA.write('*RST')
print('reseting')


Power = [-20, -15, -10, 0, 5, 10] #list of powers that we want to measure

#CHANNEL 1 (setting it up)
ZNA.write(':SENS1:SWE:TYPE LIN'+ ";*OPC") #sweep type: linear
ZNA.write(':SENS1:FREQ:CENT '+str(freq1)+' GHz'+ ";*OPC") #setting center and span of the signal that vna is emiting
ZNA.write(':SENS1:FREQ:SPAN 100000 kHz'+ ";*OPC")
#ZNA.write(':SENS1:FREQ:STAR 6 GHz'+ ";*OPC") #instead of setting a central freq. and a span, we can define start and stop freqs.
#ZNA.write(':SENS1:FREQ:STOP 7 GHz'+ ";*OPC")
ZNA.write(':SENS1:SWE:POIN 401'+ ";*OPC") #sweep points
ZNA.write('SENS1:BAND 1 KHz'+ ";*OPC")
ZNA.write(':SOUR1:POW '+str(Power[0])+' dBm'+ ";*OPC") #power (can be written as a variable like it is the first frequency)
ZNA.write(':INIT1:CONT 1'+ ";*OPC") #or ON
ZNA.write(':CALC1:PAR:DEL:SGR'+ ";*OPC") #ch1 calculate s-parameters
ZNA.write(':DISP:WIND1:TITL:DATA \'Channel 1\''+ ";*OPC") #display new window
ZNA.write(':CALC1:PAR:DEL \'Trc1\''+ ";*OPC") #delete the default trace
ZNA.write(':CALC1:PAR:SDEF \'Trc1\', \'S11\''+ ";*OPC") #create a new trace for every s-parameter
ZNA.write(':CALC1:PAR:SDEF \'Trc2\', \'S12\''+ ";*OPC")
ZNA.write(':CALC1:PAR:SDEF \'Trc3\', \'S21\''+ ";*OPC")
ZNA.write(':CALC1:PAR:SDEF \'Trc4\', \'S22\''+ ";*OPC")
ZNA.write(':DISP:WIND1:TRAC:EFE \'Trc1\''+ ";*OPC") #display
ZNA.write(':DISP:WIND1:TRAC:EFE \'Trc2\''+ ";*OPC")
ZNA.write(':DISP:WIND1:TRAC:EFE \'Trc3\''+ ";*OPC")
ZNA.write(':DISP:WIND1:TRAC:EFE \'Trc4\''+ ";*OPC")
ZNA.write(':DISP:TRAC:Y:AUTO ONCE, \'Trc1\''+ ";*OPC") #autoscale traces (this command can be copy-pasted in other places of this script if it is necessary)
ZNA.write(':DISP:TRAC:Y:AUTO ONCE, \'Trc2\''+ ";*OPC")
ZNA.write(':DISP:TRAC:Y:AUTO ONCE, \'Trc3\''+ ";*OPC")
ZNA.write(':DISP:TRAC:Y:AUTO ONCE, \'Trc4\''+ ";*OPC")
time.sleep(0.5)
ZNA.write(':CALC1:PAR:SEL \'Trc3\''+ ";*OPC" ) #select the trace we want to track
ZNA.write(':CALC1:MARK1 1'+ ";*OPC")
ZNA.write('CALC1:MARK1:FUNC:BWID:MODE BPAS'+ ";*OPC") #bandfilter ref to max (vna command)
ZNA.write('CALC1:MARK1:FUNC:EXEC BFIL'+ ";*OPC")
ZNA.write('CALCulate1:MARKer1:SEARch:BFILter:RESult ON'+ ";*OPC") #display peak parameters
ZNA.write('CALC1:MARK1:SEAR:BFIL:RES:AREA LEFT, TOP'+ ";*OPC")
ZNA.write('CALCulate1:MARKer1:SEARch:TRACking ON'+ ";*OPC") #track the peak (while is in the frequency span!)
time.sleep(2)

#CHANNEL 2
ZNA.write(':SENS2:SWE:TYPE LIN'+ ";*OPC")
ZNA.write(':SENS2:FREQ:CENT '+str(round(multifreq()[0]))+' Hz'+ ";*OPC") #we set the new freq. mode in function of the first peak
ZNA.write(':SENS2:FREQ:SPAN 100000 kHz'+ ";*OPC")
ZNA.write(':SENS2:SWE:POIN 401'+ ";*OPC")
ZNA.write('SENS2:BAND 1 KHz'+ ";*OPC")
ZNA.write(':SOUR2:POW '+str(Power[0])+' dBm'+ ";*OPC")
ZNA.write(':INIT2:CONT 1'+ ";*OPC") #o ON
ZNA.write(':CALC2:PAR:DEL:SGR'+ ";*OPC") #ch1 calculate s-parameters
ZNA.write(':CALC2:PAR:SDEF \'Trc5\', \'S11\'')
ZNA.write(':CALC2:PAR:SDEF \'Trc6\', \'S12\'')
ZNA.write(':CALC2:PAR:SDEF \'Trc7\', \'S21\'')
ZNA.write(':CALC2:PAR:SDEF \'Trc8\', \'S22\'')
ZNA.write("DISPLAY:WINDOW2:STATE ON") #display
ZNA.write(':DISP:WIND2:TITL:DATA \'Channel 2\'')
ZNA.write(':DISP:WIND2:TRAC:EFE \'Trc5\'')
ZNA.write(':DISP:WIND2:TRAC:EFE \'Trc6\'')
ZNA.write(':DISP:WIND2:TRAC:EFE \'Trc7\'')
ZNA.write(':DISP:WIND2:TRAC:EFE \'Trc8\'')
ZNA.write(':DISP:TRAC:Y:AUTO ONCE, \'Trc5\'')#autoscale
ZNA.write(':DISP:TRAC:Y:AUTO ONCE, \'Trc6\'')
ZNA.write(':DISP:TRAC:Y:AUTO ONCE, \'Trc7\'')
ZNA.write(':DISP:TRAC:Y:AUTO ONCE, \'Trc8\'')

#CHANNEL 3
ZNA.write(':SENS3:SWE:TYPE LIN'+ ";*OPC")
ZNA.write(':SENS3:FREQ:CENT '+str(round(multifreq()[1]))+' Hz'+ ";*OPC") #we set the new freq. mode in function of the first peak
ZNA.write(':SENS3:FREQ:SPAN 100000 kHz'+ ";*OPC")
ZNA.write(':SENS3:SWE:POIN 401'+ ";*OPC")
ZNA.write('SENS3:BAND 1 KHz'+ ";*OPC")
ZNA.write(':SOUR3:POW '+str(Power[0])+' dBm'+ ";*OPC")
ZNA.write(':INIT3:CONT 1'+ ";*OPC") #or ON
ZNA.write(':CALC3:PAR:DEL:SGR'+ ";*OPC") #ch1 calculate s-parameters
ZNA.write(':CALC3:PAR:SDEF \'Trc9\', \'S11\'')
ZNA.write(':CALC3:PAR:SDEF \'Trc10\', \'S12\'')
ZNA.write(':CALC3:PAR:SDEF \'Trc11\', \'S21\'')
ZNA.write(':CALC3:PAR:SDEF \'Trc12\', \'S22\'')
ZNA.write("DISPLAY:WINDOW3:STATE ON") #display
ZNA.write(':DISP:WIND3:TITL:DATA \'Channel 3\'')
ZNA.write(':DISP:WIND3:TRAC:EFE \'Trc9\'')
ZNA.write(':DISP:WIND3:TRAC:EFE \'Trc10\'')
ZNA.write(':DISP:WIND3:TRAC:EFE \'Trc11\'')
ZNA.write(':DISP:WIND3:TRAC:EFE \'Trc12\'')
ZNA.write(':DISP:TRAC:Y:AUTO ONCE, \'Trc9\'')#autoscale
ZNA.write(':DISP:TRAC:Y:AUTO ONCE, \'Trc10\'')
ZNA.write(':DISP:TRAC:Y:AUTO ONCE, \'Trc11\'')
ZNA.write(':DISP:TRAC:Y:AUTO ONCE, \'Trc12\'')

time.sleep(0.5)

#bandwith ref to max and traking the peaks in 2nd and 3th channels
ZNA.write(':CALC2:PAR:SEL \'Trc7\'')
ZNA.write(':CALC2:MARK1 1'+ ";*OPC")
ZNA.write('CALC2:MARK1:FUNC:BWID:MODE BPAS'+ ";*OPC")
ZNA.write('CALC2:MARK1:FUNC:EXEC BFIL'+ ";*OPC")
ZNA.write('CALCulate2:MARKer:SEARch:BFILter:RESult ON'+ ";*OPC")
ZNA.write('CALC2:MARK:SEAR:BFIL:RES:AREA LEFT, TOP'+ ";*OPC")
ZNA.write('CALCulate2:MARKer4:SEARch:TRACking ON'+ ";*OPC")

ZNA.write(':CALC3:PAR:SEL \'Trc11\'')
ZNA.write(':CALC3:MARK1 1'+ ";*OPC")
ZNA.write('CALC3:MARK1:FUNC:BWID:MODE BPAS'+ ";*OPC")
ZNA.write('CALC3:MARK1:FUNC:EXEC BFIL'+ ";*OPC")
ZNA.write('CALCulate3:MARKer:SEARch:BFILter:RESult ON'+ ";*OPC")
ZNA.write('CALC3:MARK:SEAR:BFIL:RES:AREA LEFT, TOP'+ ";*OPC")
ZNA.write('CALCulate3:MARKer4:SEARch:TRACking ON'+ ";*OPC")
time.sleep(2)

#small loop to change the frequency span in every channel (to 10 times the bandwidth or more)
for i in range(3):
    print(i)
    bw1 = ZNA.query('CALC1:MARK:BWID?'+ ";*OPC").split(',')
    ZNA.write(':SENS1:FREQ:CENT ' + str(round(float(bw1[1]))) + ' Hz' + ";*OPC")
    ZNA.write(':SENS1:FREQ:SPAN ' + str(round(10*float(bw1[0]))) + ' Hz' + ";*OPC")
    ZNA.write(':CALC1:PAR:SEL \'Trc3\'')
    ZNA.write(':CALC1:MARK1 1' + ";*OPC")
    ZNA.write('CALC1:MARK1:FUNC:BWID:MODE BPAS' + ";*OPC")
    ZNA.write('CALC1:MARK1:FUNC:EXEC BFIL' + ";*OPC")
    ZNA.write('CALCulate1:MARKer:SEARch:BFILter:RESult ON' + ";*OPC")
    ZNA.write('CALC1:MARK:SEAR:BFIL:RES:AREA LEFT, TOP' + ";*OPC")
    ZNA.write('CALCulate1:MARKer4:SEARch:TRACking ON' + ";*OPC")
    time.sleep(1)
    bw2 = ZNA.query('CALC2:MARK:BWID?' + ";*OPC").split(',')
    ZNA.write(':SENS2:FREQ:CENT ' + str(round(float(bw2[1]))) + ' Hz' + ";*OPC")
    ZNA.write(':SENS2:FREQ:SPAN ' + str(round(10 * float(bw2[0]))) + ' Hz' + ";*OPC") #very narrow peak, so we need to put more span to track it
    ZNA.write(':CALC2:PAR:SEL \'Trc7\'')
    ZNA.write(':CALC2:MARK1 1' + ";*OPC")
    ZNA.write('CALC2:MARK1:FUNC:BWID:MODE BPAS' + ";*OPC")
    ZNA.write('CALC2:MARK1:FUNC:EXEC BFIL' + ";*OPC")
    ZNA.write('CALCulate2:MARKer:SEARch:BFILter:RESult ON' + ";*OPC")
    ZNA.write('CALC2:MARK:SEAR:BFIL:RES:AREA LEFT, TOP' + ";*OPC")
    ZNA.write('CALCulate2:MARKer4:SEARch:TRACking ON' + ";*OPC")
    time.sleep(1)
    bw3 = ZNA.query('CALC3:MARK:BWID?' + ";*OPC").split(',')
    ZNA.write(':SENS3:FREQ:CENT ' + str(round(float(bw3[1]))) + ' Hz' + ";*OPC")
    ZNA.write(':SENS3:FREQ:SPAN ' + str(round(10 * float(bw3[0]))) + ' Hz' + ";*OPC")
    ZNA.write(':CALC3:PAR:SEL \'Trc11\'')
    ZNA.write(':CALC3:MARK1 1' + ";*OPC")
    ZNA.write('CALC3:MARK1:FUNC:BWID:MODE BPAS' + ";*OPC")
    ZNA.write('CALC3:MARK1:FUNC:EXEC BFIL' + ";*OPC")
    ZNA.write('CALCulate3:MARKer:SEARch:BFILter:RESult ON' + ";*OPC")
    ZNA.write('CALC3:MARK:SEAR:BFIL:RES:AREA LEFT, TOP' + ";*OPC")
    ZNA.write('CALCulate3:MARKer4:SEARch:TRACking ON' + ";*OPC")
    time.sleep(3)
print(i+1)

#avaluating the sweep time of every channel. This can be useful to set some of the "time.sleep()"
t=ZNA.query(':SENS1:SWE:TIME?')
print('sweep time ch1: '+str(t))

t=ZNA.query(':SENS2:SWE:TIME?')
print('sweep time ch2: '+t)

t=ZNA.query(':SENS3:SWE:TIME?')
print('sweep time ch3: '+t)


#avaluating some parameters before starting the measuring loop (not necessary actually)
BandWidth = ZNA.query('CALC1:MARK1:BWID?' + ";*OPC")
print('BandWidth = ' + BandWidth)
system_temperature, user_temperature = qd.getTemperature()
field = qd.getField()
print(f'System temperature = {system_temperature} K (Sample temperature = {user_temperature} K)')
print(f'Field = {field} 0e')



t0=time.perf_counter()

n=0


for j in range(len(Power)):

    BandWidth1 = ZNA.query('CALC1:MARK:BWID?' + ";*OPC") #taking data of the bandfilter ref to max
    print('BandWidth1 = ' + BandWidth1)
    BandWidthData1 = BandWidth1.split(',')
    BandWidth2 = ZNA.query('CALC2:MARK:BWID?' + ";*OPC")
    print('BandWidth2 = ' + BandWidth2)
    BandWidthData2 = BandWidth2.split(',')
    BandWidth3 = ZNA.query('CALC3:MARK:BWID?' + ";*OPC")
    print('BandWidth3 = ' + BandWidth3)
    BandWidthData3 = BandWidth3.split(',')
    time.sleep(0.2)

    #recentering the tree peaks and readjusting the bandwidth (to keep the peak in the frequency rang)
    ZNA.write('SENS1:FREQ:CENT ' + str(BandWidthData1[1]) + ";*OPC")
    ZNA.write('SENS2:FREQ:CENT ' + str(BandWidthData2[1]) + ";*OPC")
    ZNA.write('SENS3:FREQ:CENT ' + str(BandWidthData3[1]) + ";*OPC")

    ZNA.write('SENS1:FREQ:SPAN ' + str(10 * float(BandWidthData1[0])) + ";*OPC")
    ZNA.write('SENS2:FREQ:SPAN ' + str(10 * float(BandWidthData2[0])) + ";*OPC")
    ZNA.write('SENS3:FREQ:SPAN ' + str(10 * float(BandWidthData3[0])) + ";*OPC")

    ZNA.write('SENS1:FREQ:CENT ' + str(BandWidthData1[1]) + ";*OPC")#when we change span we have to center again
    ZNA.write('SENS2:FREQ:CENT ' + str(BandWidthData2[1]) + ";*OPC")
    ZNA.write('SENS3:FREQ:CENT ' + str(BandWidthData3[1]) + ";*OPC")

    #temperature just before taking the data

    user_temperature, system_temperature = qd.getTemperature()

    #writing in a .s2p file the data of the traces that represents the S21 parameter of the tree channels
    ZNA.write(
        'MMEM:STOR:TRAC "TRC3", "C:/Users/Public/Documents/Rohde-Schwarz/VNA/Joan/ ' + str(n)+ str('_1_') + str(Power[j])+'_' + str(
            user_temperature) + str('_') + str(system_temperature) + str('_') + str(qd.getField()) + str(
            '_.s2p') + str("\"") + ";*OPC")
    ZNA.write(
        'MMEM:STOR:TRAC "TRC7", "C:/Users/Public/Documents/Rohde-Schwarz/VNA/Joan/ ' + str(n)+ str('_2_') + str(Power[j])+'_'+ str(
            user_temperature) + str('_') + str(system_temperature) + str('_') + str(qd.getField()) + str(
            '_.s2p') + str(
            "\"") + ";*OPC")
    ZNA.write(
        'MMEM:STOR:TRAC "TRC11", "C:/Users/Public/Documents/Rohde-Schwarz/VNA/Joan/ ' + str(n)+ str('_3_') + str(Power[j])+'_'+ str(
            user_temperature) + str('_') + str(system_temperature) + str('_') + str(qd.getField()) + str(
            '_.s2p') + str(
            "\"") + ";*OPC")

    n=n+1

    time.sleep(1.5)
    if Power[j]!=Power[-1]:
        ZNA.write(':SOUR1:POW '+str(Power[j+1])+' dBm' + ";*OPC")
        ZNA.write(':SOUR2:POW ' + str(Power[j + 1]) + ' dBm' + ";*OPC")
        ZNA.write(':SOUR3:POW ' + str(Power[j + 1]) + ' dBm' + ";*OPC")

    time.sleep(1.5) #time between measurements (below a minimum time it gives an error), every measurement it takes also arround 2 secs
