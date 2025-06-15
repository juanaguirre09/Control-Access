#Libreria modificada para leer teclado matricial.
from machine import Pin, Timer
from micropython import const

class KeyPad:
    KEY_UP = const(0)
    KEY_DOWN = const(1)
    TIMER_FREQ = const(100)  # Frecuencia del timer en Hz

    def __init__(self, r1, r2, r3, r4, c1, c2, c3, c4, keys):
        self.keys = [{'char': key, 'state': self.KEY_UP} for key in keys]

        # Inicialización simplificada de pines
        self.row_pins = [Pin(pin, mode=Pin.OUT, value=0) for pin in [r1, r2, r3, r4]]
        self.col_pins = [Pin(pin, mode=Pin.IN, pull=Pin.PULL_DOWN) for pin in [c1, c2, c3, c4]]

        self.timer = Timer(-1)
        self.scan_row = 0
        self.key_code = None
        self.key_char = None

    def get_key(self):
        key_char, self.key_char = self.key_char, None
        return key_char

    def key_process(self, key_code, col_pin):
        current_value = col_pin.value()
        key_state = self.keys[key_code]['state']
        if current_value and key_state == self.KEY_UP:
            self.keys[key_code]['state'] = self.KEY_DOWN
            return self.KEY_DOWN
        elif not current_value and key_state == self.KEY_DOWN:
            self.keys[key_code]['state'] = self.KEY_UP
            return self.KEY_UP
        return None

    def scan_row_update(self):
        self.row_pins[self.scan_row].value(0)  # Desactiva la fila actual
        self.scan_row = (self.scan_row + 1) % len(self.row_pins)
        self.row_pins[self.scan_row].value(1)  # Activa la siguiente fila

    def timer_callback(self, timer):
        key_code_base = self.scan_row * len(self.col_pins)
        for index, col_pin in enumerate(self.col_pins):
            key_event = self.key_process(key_code_base + index, col_pin)
            if key_event == self.KEY_DOWN:
                self.key_char = self.keys[key_code_base + index]['char']
        self.scan_row_update()

    def start(self):
        self.timer.init(freq=self.TIMER_FREQ, mode=Timer.PERIODIC, callback=self.timer_callback)

    def stop(self):
        self.timer.deinit()
