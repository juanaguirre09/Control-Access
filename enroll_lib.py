# enroll_lib.py – función de enrolamiento con mensaje de estado
import time
from machine import UART
from fingerprint import AdafruitFingerprint

uart = UART(2, baudrate=57600, tx=17, rx=16)
sensor = AdafruitFingerprint(uart)
if not sensor.verify_password():
    raise RuntimeError("Sensor AS608 no encontrado")

# --- al inicio del archivo ---
busy = False          # ← nuevo: indica si se está enrolando

# ------------------------------
def enroll_fingerprint(slot):
    global busy
    busy = True        # ← ocupa el sensor
    _led(True)

    sensor.delete_model(slot)
    ...
    # TODA la lógica del enrolamiento
    ...
    _led(False)
    busy = False       # ← libera el sensor
    return True, "OK"


oled = None
def set_oled(display):
    global oled
    oled = display

def _msg(text):
    print(text)
    if oled:
        oled.fill(0)
        for i in range(0, len(text), 16):
            oled.text(text[i:i+16], 0, (i // 16) * 10)
        oled.show()

def _led(on):
    if on and hasattr(sensor, "led_on"):
        try:
            sensor.led_on(1)
        except:
            pass
    elif not on and hasattr(sensor, "led_off"):
        try:
            sensor.led_off()
        except:
            pass

def enroll_fingerprint(slot):
    _led(True)
    sensor.delete_model(slot)  # Solo se borra el slot indicado
    _msg("Coloca dedo")
    print("→ Esperando 1ª imagen")
    t0 = time.time()
    while sensor.get_image() != 0x00:
        if time.time() - t0 > 40:
            _led(False)
            print("⛔ Timeout 1ª imagen")
            return False, "Timeout 1ª imagen"
        time.sleep_ms(200)

    print("✔ Imagen 1 OK")
    time.sleep(1)

    result = sensor.image2Tz(1)
    if result:
        print("⛔ image2Tz 1 → Código:", hex(result))
        _led(False)
        return False, "image2Tz 1"

    _msg("Retira dedo")
    time.sleep(2)

    _msg("Pon otra vez")
    print("→ Esperando 2ª imagen")
    t0 = time.time()
    uart.read()
    while sensor.get_image() != 0x00:
        if time.time() - t0 > 20:
            _led(False)
            print("⛔ Timeout 2ª imagen")
            return False, "Timeout 2ª imagen"
        time.sleep_ms(200)

    print("✔ Imagen 2 OK")
    time.sleep(1)

    uart.read()
    result = sensor.image2Tz(2)
    if result:
        print("⛔ image2Tz 2 → Código:", hex(result))
        _led(False)
        return False, "image2Tz 2"

    _msg("Creando modelo")
    print("→ Creando modelo")
    if sensor.create_model():
        print("⛔ create_model")
        _led(False)
        return False, "create_model"

    if sensor.store_model(slot):
        print("⛔ store_model")
        _led(False)
        return False, "store_model"

    _msg("Huella OK ✓")
    print("✅ Huella guardada en slot", slot)
    _led(False)
    return True, "OK"



