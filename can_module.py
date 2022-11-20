import asyncio
import can
from multiprocessing import Pipe, Process, shared_memory
import array

class CanModule:
    def __init__(self, interface, channel):
        self.bus = can.ThreadSafeBus(interface=interface, channel=channel)
        self.simplified_ids = [336070144 + i for i inf range(0,9)]

    def raw_sender(self, pipe):
        for msg in self.bus:
            arr = [hex(msg.arbitration_id),msg.data]
            pipe.send(arr)
    def procsd_sender(self, pipe):
        for msg in self.bus:
            msg_id,payload = hex(msg.arbitration_id),msg.data
            
    def raw_logger(self, pipe, n_of_msgs):
        i = 0
        while i < n_of_msgs:
            print(pipe.recv())
            i += 1

if __name__ == '__main__':
    pass
    
