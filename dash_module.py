from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.containers import Container,Horizontal,Vertical
from textual.widgets import Header,Static,Footer,Button
import asyncio


class CanApp(App):
    CSS_PATH = "layout.css"
    BINDINGS = [
        ('q','quit','Quit'),
    ]
    def on_mount(self) -> None:
        pass    
        
    def compose(self) -> ComposeResult:
        yield Container(
                Horizontal(
                CanMsg(id=f'MAP',classes=''),
                CanMsg(id='AIR_T',classes=''),
                CanMsg(id='TPS',classes=''),
                CanMsg(id='ENG_T',classes='')
                          )
                )
        yield Container(
                Horizontal(
                CanMsg(id='GEAR',classes=''),
                CanMsg(id='FUEL_P',classes=''),
                CanMsg(id='OIL_P',classes=''),
                CanMsg(id='O2',classes='')
                )

                )
        yield Container(
                Horizontal(
                CanMsg(id='RPM',classes=''),
                CanMsg(id='WS_FR',classes=''),
                CanMsg(id='COR_O2',classes=''),
                CanMsg(id='FUEL_F',classes=''),
                )
                )
        yield Footer()

class CanMsg(Static):
    def on_mount(self) -> None:
        self.set_interval(1/60,self.watch_number)
    def watch_number(self) -> None:
        global array 
        TPS,MAP,AIR_T,ENG_T,GEAR,OIL_P,FUEL_P,O2,RPM,WS_FR,COR_O2,FUEL_F = array
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

def dash_main(array_l):
    global array
    array = array_l
    CanApp().run()

if __name__ == "__main__":    
    CanApp().run()
