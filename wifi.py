# boot.py
import network, time, machine
from secrets import WIFI_SSID, WIFI_PASSWORD

def conecta_wifi(ssid=WIFI_SSID, password=WIFI_PASSWORD, timeout=10):
    """
    Conecta el ESP32 al Wi-Fi y devuelve la tupla ifconfig().
    Lanza OSError si no lo logra en <timeout> segundos.
    """
    sta = network.WLAN(network.STA_IF)
    sta.active(True)

    if not sta.isconnected():
        print("Conectando a Wi-Fi…")
        sta.connect(ssid, password)

        t0 = time.ticks_ms()
        while not sta.isconnected():
            if time.ticks_diff(time.ticks_ms(), t0) > timeout*1000:
                raise OSError("⏰ Timeout Wi-Fi")
            time.sleep(0.25)

    print("✅ Wi-Fi OK:", sta.ifconfig())
    return sta.ifconfig()   # (ip, netmask, gateway, dns)

try:
    conecta_wifi()
except OSError as e:
    print("⚠️ ", e)
    # Opcional: reiniciar si nunca enlaza
    machine.reset()
