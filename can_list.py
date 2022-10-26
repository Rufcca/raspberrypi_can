import struct
import time
import asyncio
import can
from can.notifier import MessageRecipient
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.containers import Container
from textual.widgets import Header,Static,Footer,DataTable

simplified_ids = [336070144 + i for i in range(0,9)]
bus = can.ThreadSafeBus(interface='socketcan', channel='can0')
reader = can.AsyncBufferedReader()
global msgs
msgs = list()
lst_ts = 0
detal_ts = 0
global i 
i = 0
global payload

class Can(DataTable):
    global msgs
    global i

    number = reactive(0)
    def on_mount(self) -> None:
        self.add_columns('timestamp,delta,tps,map,airTemp,engineTemp')
        self.set_interval(1,self.update_number)
    def update_number(self) -> None:
        self.number = i
    def watch_number(self, number: int) -> None:
        msgs.reverse()
        for msg in msgs:
            if msg.arbitration_id == simplified_ids[0]:
                TPS = int.from_bytes(bytes(msg.data[0:2]), byteorder='big', signed=True) * 0.1
                MAP = int.from_bytes(bytes(msg.data[2:4]), byteorder='big', signed=True) * 0.001
                A_T = int.from_bytes(bytes(msg.data[4:6]), byteorder='big', signed=True) * 0.1
                E_T = int.from_bytes(bytes(msg.data[6:8]), byteorder='big', signed=True) * 0.1
            
                crnt_ts = float(msg.timestamp)
                global lst_ts
                global delta_ts
                global payload
                delta_ts = (crnt_ts - lst_ts) if crnt_ts > lst_ts else delta_ts  
                lst_ts = float(msg.timestamp)
                payload = f'{msg.timestamp},{delta_ts:.6f},{TPS:.2f},{MAP:.2f},{A_T:.2f},{E_T:.2f}'
                # self.update(f'{payload.split(",")}')
                self.add_row('1,1,2')
        msgs.reverse()

        # self.update(f'{payload}')

class Display(Static):
    def compose(self) -> ComposeResult:
        yield Can()
    
class CAN(App):
    BINDINGS = [
        ('q','quit','Quit'),
    ]
    def on_mount(self) -> None:
        asyncio.create_task(main())
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(Display())
        yield Footer()

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
        
async def print_w_dly(msgs,dly):
    
    msgs.reverse()
    for msg in msgs:
        if msg.arbitration_id == simplified_ids[0]:
            TPS = int.from_bytes(bytes(msg.data[0:2]), byteorder='big', signed=True) * 0.1
            MAP = int.from_bytes(bytes(msg.data[2:4]), byteorder='big', signed=True) * 0.001
            A_T = int.from_bytes(bytes(msg.data[4:6]), byteorder='big', signed=True) * 0.1
            E_T = int.from_bytes(bytes(msg.data[6:8]), byteorder='big', signed=True) * 0.1
            crnt_ts = float(msg.timestamp)
            global lst_ts
            global delta_ts
            global payload
            delta_ts = (crnt_ts - lst_ts) if crnt_ts > lst_ts else delta_ts  
            lst_ts = float(msg.timestamp)
            
            return f'{msg.timestamp},{delta_ts:.6f},{TPS:.2f},{MAP:.2f},{A_T:.2f},{E_T:.2f}'
    msgs.reverse()
    
    await asyncio.sleep(dly)

async def main() -> None:
    listeners : List[MessageRecipient] = [listen_can,reader]
    loop = asyncio.get_running_loop()
    notifier = can.Notifier(bus,listeners,loop=loop)

if __name__ == "__main__":    
    CAN().run()
