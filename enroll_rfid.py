from machine import Pin, SPI
from mfrc522 import MFRC522
from time import sleep

# Configuración del SPI para el RC522
spi = SPI(1, baudrate=1000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(23), miso=Pin(19))

# Inicialización del lector RC522
rdr = MFRC522(spi=spi, gpioRst=Pin(4), gpioCs=Pin(5))

print("Acerque una tarjeta o llavero RFID")

try:
    while True:
        (stat, tag_type) = rdr.request(rdr.REQIDL)

        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()

            if stat == rdr.OK:
                uid_str = ''.join('{:02X}'.format(b) for b in raw_uid)
                print("UID detectado:", uid_str)
                print("Esperando otra tarjeta...")
                sleep(2)

except KeyboardInterrupt:
    print("Programa detenido.")
