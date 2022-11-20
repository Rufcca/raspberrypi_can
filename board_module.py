from multiprocessing import Process, Pipe, Array, Lock
import time
import os
class Board:
    def __init__(self,pipe):
        self.tags = ('TPS','MAP','AIRTEMP','ENGTEMP','GEAR','OILP','FUELP','LAMBDA','RPM','WSFR','LAMBDACORR','FUELFLOW')
        
        self.TPS = 0
        self.MAP = 0
        self.AIRTEMP = 0
        self.ENGTEMP = 0

        self.OILP = 0
        self.FUELP = 0
        self.GEAR = 0

        self.LAMBDA = 0
        self.RPM = 0

        self.WS_FR = 0

        self.LAMBDACORR = 0
        self.FUELFLOW = 0

        self.simplified_id = [336070144 + i for i in range(0,9)]
        self._pipe = pipe

    def write_board(self,array):
        while True:
            i = 0
            j = 0
            msg_id,payload = self._pipe.recv()
            data = list()
            if msg_id == hex(self.simplified_id[0]):
                while i < 8:
                    j = i + 2
                    data.append(payload[i:j])
                    i = i + 2
                self.TPS = int.from_bytes(bytes(data[0]),byteorder='big',signed=True) * 0.1
                self.MAP = int.from_bytes(bytes(data[1]),byteorder='big', signed=True) * 0.001
                self.AIRTEMP = int.from_bytes(bytes(data[2]),byteorder='big', signed=True) * 0.1
                self.ENGTEMP = int.from_bytes(bytes(data[3]),byteorder='big', signed=True) * 0.1
                # print(f'{msg_id} - {self.TPS} , {self.MAP} , {self.AIRTEMP} , {self.ENGTEMP}') 
            if msg_id == hex(self.simplified_id[1]):
                while i < 8:
                    j = i + 2
                    data.append(payload[i:j])
                    i = i + 2
                self.OILP = int.from_bytes(bytes(data[0]),byteorder='big',signed=True) * 0.001
                self.FUELP = int.from_bytes(bytes(data[1]),byteorder='big',signed=True) * 0.001
                self.GEAR = int.from_bytes(bytes(data[3]),byteorder='big',signed=True)
                # print(f'{msg_id} - {self.OILP} , {self.FUELP} , {self.GEAR}')
            if msg_id == hex(self.simplified_id[2]):
                while i < 8:
                    j = i + 2
                    data.append(payload[i:j])
                    i = i + 2
                self.LAMBDA = int.from_bytes(bytes(data[0]),byteorder='big',signed=True) * 0.001
                self.RPM = int.from_bytes(bytes(data[1]),byteorder='big',signed=True)
                # print(f'{msg_id} - {self.LAMBDA} , {self.RPM}')
            if msg_id == hex(self.simplified_id[3]):
                while i < 8:
                    j = i + 2
                    data.append(payload[i:j])
                    i = i + 2
                self.WS_FR = int.from_bytes(bytes(data[1]),byteorder='big',signed=True) * 0.1
                # print(f'{msg_id} - {self.WS_FR}')
            if msg_id == hex(self.simplified_id[8]):
                while i < 8:
                    j = i + 2
                    data.append(payload[i:j])
                    i = i + 2
                self.LAMBDACORR = int.from_bytes(bytes(data[0]),byteorder='big',signed=True)
                self.FUELFLOW = int.from_bytes(bytes(data[1]),byteorder='big',signed=True) * 0.01
                # print(f'{msg_id} - {self.LAMBDACORR} , {self.FUELFLOW}')
            array_l = [self.TPS , self.MAP , self.AIRTEMP , self.ENGTEMP , self.OILP , self.FUELP , self.GEAR , self.LAMBDA , self.RPM , self.WS_FR , self.LAMBDACORR , self.FUELFLOW]
            # print(array_l)
            for i in range(len(array_l)):
                array[i] = array_l[i]

    def read_board(self, array):
        i = 0
        while True:
            os.system('clear')
            print(array[:])
            i+=1
            time.sleep(0.033)

