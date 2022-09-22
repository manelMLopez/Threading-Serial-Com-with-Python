# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 16:32:12 2022

@author: mlopez

This program permits to connect to any COM or dev/tty port
easily and using threading in reception.

The class trx also implements the read option, but this is 
not threaded. Just in case you don't want to use this threading option.
' 
"""

import serial
import sys
import glob
from enum import Enum
import time
from serial.threaded import ReaderThread, Protocol
from queue import Queue


###############################################################################
class comandes(int, Enum):
    '''
    class comandes:
        This class defines the command options to
        send to the device connected to the serial
        COM.
        It uses the Enum library, to make something
        similar to enumerations in C
    '''
    ACTIVA_MOTOR_DC = 1
    ACTIVA_MOTOR_BRL = 2
    LECTURA_AMPEROMETRIA = 3
    TEMPERATURA = 4
    PRESSIO = 5
    HUMITAT = 6
    FINAL = 7
###############################################################################

###############################################################################
class trx():
    '''
    class trx:
        this class make a search of available ports to be used. You have to 
        select to which port you want to connect.
        Modify the speed as you want in configure_serial, changing the baudrate. 
    '''

    def __init__(self):
        self.time_sleep = 0.02
        self.ports_oberts = self.get_ports()

    def get_ports(self):
        ''' 
        CAT Busquem tots els ports disponibles segons el sistema operatiu de 
        l'ordinador
        ENG Here we search all the available ports depending on the OS
        '''
        
        if sys.platform.startswith('win'):
            ports_oberts = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports_oberts = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports_oberts = glob.glob('/dev/cu.*') #glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
        port_final = []
        for port in ports_oberts:
            try:
                s = serial.Serial(port)
                s.close()
                port_final.append(port)
            except (OSError, serial.SerialException):
                pass
        return port_final

    def configure_serial(self, port_of_connection):
        '''
        CAT Reb un string amb el nom del port, l'obre i torna l'objecte pyserial del port corresponent
        així com una variable boolean == True si el port esta obert, o False si esta tancat
        
        ENG From the string parameter "port_of_connection", try to open the port. if success, it 
        returns true, meaning that the port is open, on the contrary, it returns false.
        '''
        
        try:
            print(port_of_connection)
            serialPort = serial.Serial(port=port_of_connection, baudrate=115200,
                                       parity=serial.PARITY_NONE,
                                       stopbits=serial.STOPBITS_ONE,
                                       bytesize=serial.EIGHTBITS)
            if serialPort is None:
                serialPort.open()
            serialbool = serialPort.isOpen()
            return serialPort, serialbool
        except:
            #self.left_recibidoserial_output.insert(END, '> No hi ha port obert \n')
            print('> No hi ha port obert \n')
            sys.exit(2)
            return -1

    def close_port(self, serialPort, header):
        '''
        CAT Reb un objecte port pyserial, intenta tancar-lo
        i retorna el boolean True si es queda obert, False si esta tancat
        
        ENG Receives an pyserial object,and try to close it. 
        it returns true if the port is closed. On te contrary it returns false
        '''

        try:
            serialPort.close()
            serialbool = serialPort.isOpen()
            #panel.insert(END,'> Port was closed \n')
            header.set('Choose COM port')
            return serialbool
        except:
            print("END", 'No puc tancar el port \n')
            return -1

    def transmission(self, serialPort, value):
        
        '''

        Parameters
        ----------
        serialPort : TYPE
            DESCRIPTION.
        value : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        try:
            serialPort.flushInput()
            serialPort.flushOutput()
            time.sleep(.1)
            val = value.encode('utf-8') # codifica el value a enviar pel port
            serialPort.write(val)

        except:
            #self.left_recibidoserial_output.insert(END, '> No puc enviar res pel port \n')
            print('> No puc enviar res pel port \n')
            sys.exit(0)

    def reception(self, serialPort, cua): #timeout
        '''
        a non threaded reception function.
        example of usage of queues here...
        '''
        try:
            print(time.time())
            time.sleep(0.2)
            dades = bytes()
            print("hola")
            print(len(dades))
            while serialPort.inWaiting()>0:
                dades += serialPort.read()
                time.sleep(0.5)
            if(len(dades)>0):
                cua.put(dades)
                print(cua.qsize())
                #cua.join() # block until all tasks are done
        except:
            sys.exit(0)
###############################################################################

###############################################################################
class SerialReaderProtocolRaw(Protocol):
    '''
    https://pyserial.readthedocs.io/en/latest/pyserial_api.html#module-serial.threaded
    '''
    port = None

    def connection_made(self, transport):
        """Called when reader thread is started"""
        print("Connected, ready to receive data...")

    def data_received(self, data):
        """Called with snippets received from the serial port"""
        updateLabelData(data)
###############################################################################
    
def updateLabelData(data):
    data = data.decode("utf-8")
    print("The value is: ", data)


def opcions():
    print("1.- ACTIVA_MOTOR_DC")
    print("2.- ACTIVA_MOTOR_BRL")
    print("3.- LECTURA_AMPEROMETRIA")
    print("4.- TEMPERATURA")
    print("5.- PRESSIO")
    print("6.- HUMITAT") 
    print("7.- FINAL")
    x = int(input("Selecciona opció: "))
    return x

def nop():
    return 0

def main():
    s = trx()
    # https://docs.python.org/2/library/queue.html
    '''
    The Queue module implements multi-producer, multi-consumer queues. 
    It is especially useful in threaded programming when information must
    be exchanged safely between multiple threads. The Queue class in this 
    module implements all the required locking semantics. 
    It depends on the availability of thread support in Python; see the threading module.
    '''
    cua = Queue() # to be implemented..
    
    #obrint el port serie...
    #list the differnet open serial ports
    ports = s.get_ports()
    print("Ports oberts: ")
    print(ports, type(ports))
    #choose one open port
    print("Selecciona el port de communicacions: ")
    dades = input(">")
    serialPort, serialbool = s.configure_serial(dades.upper())
    print("Port escollit: ", serialPort)
    if serialbool == False:
        #In case of problems opening port 
        print("No s'ha pogut obrir el port")
        sys.exit(0)
    else:
        #if port works propertly...
        print("Port obert correctament...")

    reader = ReaderThread(serialPort, SerialReaderProtocolRaw)
    # Start reader
    reader.start()
    while True:
        
        if cua.empty() == False:
            # Do sometring...
            #print("entrada de dades des de la placa pcb")
            #item = cua.get()
            #print(item)
            #cua.task_done()
            nop()
        else:
            print("enviem dades")
            opcio = opcions()
            if opcio == comandes.FINAL:
                serialPort.close()
                sys.exit(0)
            else:
                value = str(opcio)
                s.transmission(serialPort, value)
                time.sleep(0.5)
                while serialPort.inWaiting()>0:
                    print(serialPort.read())
main()