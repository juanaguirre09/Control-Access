from machine import I2C, Pin, SPI, UART, SoftI2C
import time
from time import sleep
from keypad_utp import KeyPad
import ssd1306
from mfrc522 import MFRC522
from fingerprint import AdafruitFingerprint
import ubinascii
import urequests   # ← ¡Agrega esta línea!
from wifi import conecta_wifi
conecta_wifi()        # → se conecta y muestra la IP
from api_queue import log_acceso, flush_pendientes
import ujson
import enroll_lib

# ── CONFIGURACIÓN DEL SERVIDOR ───────────────────────────────
SERVER_IP = "10.253.41.219"  # ← cambia esta IP si vuelves a cambiar de red
API_BASE = f"http://{SERVER_IP}/access"
BASE_URL = f"{API_BASE}/buscar_usuario.php"

enroll_activo = False



# --- Configuración I2C para OLED ---
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))   # en lugar de I2C(...)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
enroll_lib.set_oled(oled)     # ← línea nueva

# ── Servidor HTTP /enroll  (solo se inicia una vez) ─────────────────
try:
    if "_HTTP_ENROLL_STARTED" not in globals():
        import _thread, enrol_server
        _thread.start_new_thread(enrol_server.start_http_server, ())
        globals()["_HTTP_ENROLL_STARTED"] = True
        print("✔️  Servidor /enroll escuchando")
    else:
        print("ℹ️  /enroll ya estaba en ejecución")
except Exception as e:
    print("⚠️  No se pudo iniciar enrol_server:", e)


# --- Configuración teclado ---
Teclas = [
    '1', '2', '3', 'A',
    '4', '5', '6', 'B',
    '7', '8', '9', 'C',
    '*', '0', '#', 'D',
]
keypad = KeyPad(r1=13, r2=12, r3=14, r4=27,
                c1=26, c2=25, c3=33, c4=32, keys=Teclas)
keypad.start()

# --- Configuración LEDS ---
#  Pin 2 → LED verde (acceso concedido)
#  Pin 15 → LED rojo  (reposo / acceso denegado)
#  NOTA: se asume que los módulos LED incluyen la resistencia serie adecuada
led_verde = Pin(2,  Pin.OUT, value=0)
led_rojo  = Pin(15, Pin.OUT, value=1)  # encendido al arrancar (estado reposo)

# --- Configuración RFID SPI ---
spi = SPI(1, baudrate=1000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(23), miso=Pin(19))
rdr = MFRC522(spi=spi, gpioRst=Pin(4), gpioCs=Pin(5))

# --- Configuración Fingerprint (AS608) ---
uart = UART(2, baudrate=57600, tx=17, rx=16)
uart.init(baudrate=57600)
time.sleep(2)           # <— espera a que el sensor arranque
uart.read()             # <— limpia buffer
sensor = AdafruitFingerprint(uart)
if not sensor.verify_password():
    print("Error: sensor fingerprint no detectado.")
    raise SystemExit

clave_ingresada = ""
intentos_fallidos = 0
bloqueado = False
bloqueo_inicio = 0
TIEMPO_BLOQUEO = 20


def mostrar_oled(linea1, linea2=""):
    
    oled.fill(0)
    oled.text(linea1, 0, 0)
    if linea2:
        oled.text(linea2, 0, 10)
    oled.show()

def modo_reposo():
    """Estado por defecto: LED rojo encendido, verde apagado."""
    led_verde.value(0)
    led_rojo.value(1)


def acceso_correcto(nombre: str, uid: str, via: str):
    # 1) registra el evento en la BD
    import gc
    print("Memoria libre antes de log_acceso:", gc.mem_free())
    try:
        log_acceso(uid, via)
    except Exception as e:
        print("Error enviando evento:", e)
    print("Memoria libre después de log_acceso:", gc.mem_free())
    sleep(2)
    mostrar_oled("Bienvenido", nombre)
    led_rojo.value(0)
    led_verde.value(1)
    sleep(5)
    modo_reposo()
    mostrar_oled("Ingrese clave:")


def buscar_usuario_por_pin(pin_str):
    """
    Llama a buscar_usuario.php?pin=<pin_str>
    Devuelve (nombre, id_usuario) si ok == true.
    Si hay error o ok == false, devuelve (None, None).
    """
    try:
        # 1) Construye la URL con el PIN en query-string
        url = "{}?pin={}".format(BASE_URL, pin_str)
        
        # 2) Hace la petición GET
        r = urequests.get(url)
        
        # 3) Lee el texto crudo
        texto = r.text
        # Opcional: print("→ buscar_usuario GET response:", texto)
        
        # 4) Parsea JSON
        data = ujson.loads(texto)
        r.close()
        
        # 5) Si "ok" es verdadero, devuelve nombre e id
        if data.get("ok"):
            nombre = data.get("nombre")
            id_usuario = data.get("id")
            # Asegúrate de que ambos existan y sean válidos
            if nombre is not None and id_usuario is not None:
                return nombre, int(id_usuario)
        
        # Si llegamos aquí, algo falló (ok == false)
        return None, None

    except Exception as e:
        # Puede ser problema de red, JSON inválido, etc.
        print("Error en buscar_usuario_por_pin:", e)
        return None, None
    
def buscar_usuario_por_slot(slot):
    url = f"{API_BASE}/buscar_usuario_huella.php?slot={slot}"
    try:
        response = urequests.get(url)
        data = response.json()
        response.close()
        if data.get("ok"):
            return data["nombre"], data["rfid_uid"], data["pin"]
        else:
            return None, None, None
    except Exception as e:
        print("Error consultando usuario por huella:", e)
        return None, None, None
    
def buscar_usuario_por_rfid(rfid_uid):
    url = f"{API_BASE}/buscar_usuario_rfid.php?rfid_uid={rfid_uid}"
    try:
        response = urequests.get(url)
        data = response.json()
        response.close()
        if data.get("ok"):
            return data["nombre"], data["pin"], data["slot_huella"]
        else:
            return None, None, None
    except Exception as e:
        print("Error consultando usuario por RFID:", e)
        return None, None, None



# Mostrar pantalla inicial y LEDs en reposo
modo_reposo()
mostrar_oled("Ingrese clave o", "use su tarjeta o huella")




def buscar_huella():
    # 0 = FINGERPRINT_OK
    r = sensor.get_image()
    if r != 0:
        # 0x02 = NO_FINGER en la mayoría de librerías
        # Imprime todo retorno diferente de OK
        print("DEBUG get_image →", hex(r))
        return None

    r = sensor.image2Tz(1)
    if r != 0:
        print("DEBUG image2Tz →", hex(r))
        return None

    r = sensor.search(0, 200)         # busca en 0-199
    if r != 0:
        # 0x09 = NOT_FOUND  (huella leída pero sin coincidencia)
        print("DEBUG search →", hex(r))
        return None

    fid = sensor.finger_id             # slot donde hizo match
    score = sensor.confidence
    print("DEBUG match: slot", fid, "| score", score)

    nombre, rfid_uid, pin = buscar_usuario_por_slot(fid)
    print("DEBUG usuario slot:", nombre, rfid_uid, pin)

    if nombre is None:
        # El sensor SI encontró huella, pero ese slot no está en la BD
        return None

    return nombre, rfid_uid, fid


try:
    while True:
        # --- BLOQUEO TEMPORAL ---
        if bloqueado:
            tiempo_restante = TIEMPO_BLOQUEO - int(time.time() - bloqueo_inicio)
            if tiempo_restante <= 0:
                bloqueado = False
                intentos_fallidos = 0
                clave_ingresada = ""
                modo_reposo()
                mostrar_oled("Ingrese clave o", "use su tarjeta o huella")
            else:
                mostrar_oled("Bloqueado", f"Espera {tiempo_restante}s")
                sleep(1)
                continue
            
        



        match = buscar_huella()
        if match:                              # recibió (nombre, rfid_uid, slot)
            nombre, rfid_uid, slot = match
            print("DEBUG acceso por huella:", match)
            acceso_correcto(nombre, str(slot), "huella")
            intentos_fallidos = 0
            continue

        # Si hubo imagen (get_image == 0) pero ningún match:
        if sensor.get_image() == 0:
            mostrar_oled("Huella no", "reconocida")



            
        # --- LECTURA RFID ---
        (stat, tag_type) = rdr.request(rdr.REQIDL)
        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()
            if stat == rdr.OK:
                uid_str = ''.join('{:02X}'.format(b) for b in raw_uid)
                nombre, pin, slot_huella = buscar_usuario_por_rfid(uid_str)
                if nombre:
                    acceso_correcto(nombre, uid_str, "tarjeta")
                    intentos_fallidos = 0
                else:
                    mostrar_oled("Tarjeta no", "registrada")
                    sleep(2)
                    mostrar_oled("Ingrese clave o", "use su tarjeta o huella")
                continue

#         if stat == rdr.OK:
#             (stat, raw_uid) = rdr.anticoll()
#             if stat == rdr.OK:
#                 uid_str = ''.join('{:02X}'.format(b) for b in raw_uid)
#                 if uid_str in uids:
#                     clave = uids[uid_str]
#                     nombre = usuarios[clave]["nombre"]
#                     acceso_correcto(nombre, uid_str, "tarjeta")
#                     intentos_fallidos = 0
#                 else:
#                     mostrar_oled("Tarjeta no", "registrada")
#                     sleep(2)
#                     mostrar_oled("Ingrese clave o", "use su tarjeta o huella")
#                 continue

        # --- LECTURA TECLADO ---
        key = keypad.get_key()
        if key:
            if key == '*':
                clave_ingresada = ""
                mostrar_oled("Ingrese clave:")

            elif key == '#':
                # 1) Llamamos a la función recién definida:
                nombre, id_usuario = buscar_usuario_por_pin(clave_ingresada)
                print("DEBUG: nombre devuelto =", nombre, " | id_usuario =", id_usuario)

                # 2) Si encuentra usuario, pasamos el ID (número) a acceso_correcto
                if nombre is not None:
                    acceso_correcto(nombre, id_usuario, "clave")
                    intentos_fallidos = 0
                else:
                    intentos_fallidos += 1
                    mostrar_oled("Clave incorrecta", f"Intento {intentos_fallidos}/3")
                    sleep(2)
                    if intentos_fallidos >= 3:
                        bloqueado = True
                        bloqueo_inicio = time()
                        mostrar_oled("Demasiados", "intentos")
                        sleep(2)
                    else:
                        mostrar_oled("Ingrese clave:")
                clave_ingresada = ""

            elif key in '0123456789':
                if len(clave_ingresada) < 4:
                    clave_ingresada += key
                    mostrar_oled("Ingrese clave:", '*' * len(clave_ingresada))

            sleep(0.1)

        try:
            flush_pendientes()
        except Exception as e:
            print("Error en flush_pendientes:", e)
        
            

finally:
    keypad.stop()
    led_verde.value(0)
    led_rojo.value(0)





