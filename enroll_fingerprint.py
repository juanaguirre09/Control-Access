# enroll_fingerprint.py
# Enrolamiento de huellas en diferentes slots con AS608 + ESP32
#
# Requiere:
#   • fingerprint.py  (tu librería)                               :contentReference[oaicite:0]{index=0}
#   • ssd1306.py      (driver OLED, opcional)

from machine import UART, Pin, I2C
import time
from fingerprint import AdafruitFingerprint
import gc
global _enroll_count
_enroll_count = _enroll_count + 1 if "_enroll_count" in globals() else 1
print(">> intento", _enroll_count, "RAM:", gc.mem_free())


# ─── Configuración hardware ────────────────────────────────────────────────────
uart = UART(2, baudrate=57600, tx=17, rx=16)      # UART2: 17-TX, 16-RX
sensor = AdafruitFingerprint(uart)                # Instancia lector

# OLED opcional (128x64, dirección 0x3C, SDA 21, SCL 22)
try:
    from ssd1306 import SSD1306_I2C
    i2c  = I2C(0, scl=Pin(22), sda=Pin(21))
    oled = SSD1306_I2C(128, 64, i2c)
    def show(msg):
        oled.fill(0)
        for i in range(0, len(msg), 16):
            oled.text(msg[i:i+16], 0, 10*i//16)
        oled.show()
        print(msg)
except ImportError:
    oled = None
    def show(msg):         # Sólo por consola
        print(msg)

# ─── Verificación de sensor ───────────────────────────────────────────────────
show("Verificando...")
if not sensor.verify_password():
    show("❌ Sensor no encontrado")
    raise SystemExit
show("✅ Sensor listo")

# ─── Funciones auxiliares ─────────────────────────────────────────────────────
def wait_finger(state_msg: str, expected_code: int = 0x00):
    """Espera hasta que get_image devuelve expected_code (0x00 = imagen OK)."""
    show(state_msg)
    while True:
        if sensor.get_image() == expected_code:
            break
        time.sleep_ms(200)

def enroll(location: int):
    """Enrola una huella en la ranura <location>."""
    show(f"Enrolar ID {location}")

    # ─ 1ª imagen ─
    wait_finger("→ Coloca el dedo")
    if sensor.image2Tz(1):
        show("❌ image2Tz slot1"); return

    # ─ 2ª imagen ─
    show("Retira dedo")
    time.sleep(2)
    wait_finger("→ Coloca otra vez")
    if sensor.image2Tz(2):
        show("❌ image2Tz slot2"); return

    # ─ Combinar y guardar ─
    if sensor.create_model():
        show("❌ create_model");   return
    if sensor.store_model(location):
        show("❌ Guardar modelo"); return

    show(f"✅ Huella guardada\nID = {location}")

# ─── Bucle principal ──────────────────────────────────────────────────────────
while True:
    try:
        slot = int(input("\nID de ranura (0-199) o -1 para salir: "))
    except ValueError:
        show("Ingresa un número"); continue
    if slot < 0:
        show("Fin"); break
    if not (0 <= slot <= 199):
        show("Rango 0-199"); continue

    # Comprueba si ya hay algo en ese slot
    if sensor.search(start_page=slot, page_num=1) == 0x00:
        show("Ranura ocupada")
        cont = input("¿Sobrescribir? (s/n): ").lower()
        if cont != "s":
            continue

    enroll(slot)
    time.sleep(2)

