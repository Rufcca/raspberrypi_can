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
global lst_ts
att_hz = 10
i = 0
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
        yield Container(
                Horizontal(
                Can(id='MAP',classes=''),
                Can(id='AIR_T',classes=''),
                Can(id='TPS',classes=''),
                Can(id='ENG_T',classes='')
                          )
                )
        yield Container(
                Horizontal(
                Can(id='GEAR',classes=''),
                Can(id='FUEL_P',classes=''),
                Can(id='OIL_P',classes=''),
                Can(id='O2',classes='')
                         )

                )
        yield Container(
                Horizontal(
                Can(id='RPM',classes=''),
                Can(id='WS_FR',classes=''),
                Can(id='COR_O2',classes=''),
                Can(id='FUEL_F',classes=''),
                )
                )
        yield Can(id='DELTA_T',classes='')
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
        AIR_T = 0
        ENG_T = 0
                
        GEAR = 0 #[6:8]
        OIL_P = 0 #[0:2]
        FUEL_P = 0 #[2:4]

        O2 = 0
        RPM = 0

        WS_FR = 0
        
        COR_O2 = 0
        FUEL_F = 0

        found0 = False
        found1 = False
        found2 = False
        found3 = False
        found4 = False

        for msg in reversed(msgs):
            if msg.arbitration_id == simplified_ids[0] and found0 == False:
                TPS = int.from_bytes(bytes(msg.data[0:2]), byteorder='big', signed=True) * 0.1
                MAP = int.from_bytes(bytes(msg.data[2:4]), byteorder='big', signed=True) * 0.001
                AIR_T = int.from_bytes(bytes(msg.data[4:6]), byteorder='big', signed=True) * 0.1
                ENG_T = int.from_bytes(bytes(msg.data[6:8]), byteorder='big', signed=True) * 0.1
                crnt_ts = float(msg.timestamp)
                delta_ts = crnt_ts - lst_ts if crnt_ts > lst_ts else delta_ts  
                lst_ts = float(msg.timestamp)
                timestamp = msg.timestamp
                found0 = True
            if msg.arbitration_id == simplified_ids[1] and found1 == False:
                GEAR   = int.from_bytes(bytes(msg.data[6:8]),byteorder='big',signed=True)
                OIL_P  = int.from_bytes(bytes(msg.data[0:2]),byteorder='big',signed=True) * 0.001
                FUEL_P = int.from_bytes(bytes(msg.data[2:4]),byteorder='big',signed=True) * 0.001
                found1 = True
            if msg.arbitration_id == simplified_ids[2] and found2 == False:
                O2 = int.from_bytes(bytes(msg.data[0:2]),byteorder='big',signed=True) * 0.001
                RPM = int.from_bytes(bytes(msg.data[2:4]),byteorder='big',signed=True)
                found2 = True
            if msg.arbitration_id == simplified_ids[3] and found3 == False:
                WS_FR = int.from_bytes(bytes(msg.data[2:4]),byteorder='big',signed=True) * 0.1
                found3 = True
            if msg.arbitration_id == simplified_ids[8]:
                COR_O2 = int.from_bytes(bytes(msg.data[0:2]),byteorder='big',signed=True)
                FUEL_F = int.from_bytes(bytes(msg.data[2:4]),byteorder='big',signed=True) * 0.01
                found4 = True
            if found0 == True and found1 == True and found2 == True and found3 == True and found4 == True:
                break

        if self.id == 'TPS':
            self.update(f'{self.id}: {TPS:.1f}')
        if self.id == 'MAP':
            self.update(f'{self.id}: {MAP:.2f}')
        if self.id == 'AIR_T':
            self.update(f'TEMP AR: {AIR_T:.1f}')
        if self.id == 'ENG_T':
            self.update(f'TEMP MOTOR: {ENG_T:.1f}')
        if self.id == 'GEAR':
            self.update(f'MARCHA: {GEAR}')
        if self.id == 'OIL_P':
            self.update(f'PRESSAO OLEO: {OIL_P:.1f}')
        if self.id == 'FUEL_P':
            self.update(f'PRESSAO COMB: {FUEL_P:.1f}')
        if self.id == 'O2':
            self.update(f'LAMBDA: {O2:.3f}')
        if self.id == 'RPM':
            self.update(f'RPM: {RPM}')
        if self.id == 'WS_FR':
            self.update(f'VEL: {WS_FR}')
        if self.id == 'COR_O2':
            self.update(f'CORR: {COR_O2:.2f}')
        if self.id == 'FUEL_F':
            self.update(f'FLUXO: {FUEL_F:.2f}')
        if self.id == 'DELTA_T':
            self.update(f'DELTA: {delta_ts}')

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
            break 

async def main() -> None:
    listeners : List[MessageRecipient] = [listen_can,reader]
    loop = asyncio.get_running_loop()
    notifier = can.Notifier(bus,listeners,loop=loop)
    # while True:
        # await print_w_dly(msgs)
        # await asyncio.sleep(0.5)

if __name__ == "__main__":    
    # asyncio.run(main())
    CAN().run()
