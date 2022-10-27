import struct
import time
import asyncio
import can
import csv
import io

from can.notifier import MessageRecipient
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.containers import Container,Horizontal,Vertical
from textual.widgets import Header,Static,Footer

simplified_ids = [336070144 + i for i in range(0,9)]
bus = can.ThreadSafeBus(interface='socketcan', channel='can0')
reader = can.AsyncBufferedReader()

global msgs
global i 
global payload
global delta_ts
global att_hz
att_hz = 20
i = 0
global lst_ts
msgs = list()
lst_ts = 0
detal_ts = 0

class CAN(App):
    CSS_PATH = "layout.css"

    BINDINGS = [
        ('q','quit','Quit'),
    ]
    def on_mount(self) -> None:
        asyncio.create_task(main())
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
                Can(id='MAP',classes='box'),
                Can(id='AIR_T',classes='box'),
                Can(id='TPS',classes='box'),
                Can(id='ENG_T',classes='box')
                )
        yield Footer()


class Can(Static):
    global msgs
    global i
    global att_hz
    number = reactive(0)

    def on_mount(self) -> None:
        self.set_interval(1/att_hz,self.update_number)
    def update_number(self) -> None:
        self.number = i
    def watch_number(self, number: int) -> None:
        global lst_ts

        payload = 0
        delta_ts = 0
        timestamp = 0
        
        TPS = 0
        MAP = 0
        A_T = 0
        E_T = 0
         
        for msg in reversed(msgs):
            if msg.arbitration_id == simplified_ids[0]:
                TPS = int.from_bytes(bytes(msg.data[0:2]), byteorder='big', signed=True) * 0.1
                MAP = int.from_bytes(bytes(msg.data[2:4]), byteorder='big', signed=True) * 0.001
                A_T = int.from_bytes(bytes(msg.data[4:6]), byteorder='big', signed=True) * 0.1
                E_T = int.from_bytes(bytes(msg.data[6:8]), byteorder='big', signed=True) * 0.1
                crnt_ts = float(msg.timestamp)
                delta_ts = crnt_ts - lst_ts if crnt_ts > lst_ts else delta_ts  
                lst_ts = float(msg.timestamp)
                timestamp = msg.timestamp
                break
        # for msg in msgs:
        #     msgs_dict.update({msg.arbitration_id:f'{str(bytes(msg.data[0:2]).hex())} {str(bytes(msg.data[2:4]).hex())} {str(bytes(msg.data[4:6]).hex())} {str(bytes(msg.data[6:8]).hex())}'})
        # self.update(str(self.id))
        if self.id == 'TPS':
            self.update(f'{self.id}: {TPS:.1f}')
        if self.id == 'MAP':
            self.update(f'{self.id}: {MAP:.2f}')
        if self.id == 'AIR_T':
            self.update(f'{self.id}: {A_T:.1f}')
        if self.id == 'ENG_T':
            self.update(f'{self.id}: {E_T:.2f}')
        # self.update(f'{timestamp:.3f},{delta_ts:.3f},{TPS:.2f},{MAP:.2f},{A_T:.2f},{E_T:.2f}')
async def listen_can(msg):
    global i
    i+=1
    if msg.arbitration_id in simplified_ids:
        if len(msgs) < 50:
            msgs.append(msg)
        if len(msgs) >= 50:
            msgs.append(msgs.pop(0))
            msgs.pop()
            msgs.append(msg)
        
async def print_w_dly(msgs):
    global lst_ts
    global payload
    delta_ts =0
    for msg in reversed(msgs):
        if msg.arbitration_id == simplified_ids[0]:
            TPS = int.from_bytes(bytes(msg.data[0:2]), byteorder='big', signed=True) * 0.1
            MAP = int.from_bytes(bytes(msg.data[2:4]), byteorder='big', signed=True) * 0.001
            A_T = int.from_bytes(bytes(msg.data[4:6]), byteorder='big', signed=True) * 0.1
            E_T = int.from_bytes(bytes(msg.data[6:8]), byteorder='big', signed=True) * 0.1
            crnt_ts = float(msg.timestamp)
            delta_ts = (crnt_ts - lst_ts) if crnt_ts - lst_ts  < 25 else delta_ts  
            lst_ts = float(msg.timestamp)
            
            # print(f'T:{msg.timestamp:.3f}-DT{delta_ts:.3f}|TPS:{TPS:.2f},MAP:{MAP:.2f},A_T:{A_T:.2f},E_T:{E_T:.2f}')
            break 
async def main() -> None:
    listeners : List[MessageRecipient] = [listen_can,reader]
    loop = asyncio.get_running_loop()
    notifier = can.Notifier(bus,listeners,loop=loop)
    while True:
        await print_w_dly(msgs)
        await asyncio.sleep(0.5)

if __name__ == "__main__":    
    # asyncio.run(main())
    CAN().run()
